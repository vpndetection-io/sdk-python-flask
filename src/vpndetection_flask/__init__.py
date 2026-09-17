"""Official Flask extension for the VPNDetection API.

Classifies the visitor behind each request and hangs the answer off ``g.vpndetection``,
where your views can read it. Blocking is opt-in.

    from flask import Flask
    from vpndetection_flask import VPNDetection

    app = Flask(__name__)
    VPNDetection(app, api_key=os.environ["VPNDETECTION_API_KEY"])

The framework-agnostic half lives in ``vpndetection.middleware``; this package is only
the parts that are genuinely Flask-shaped.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from flask import Flask, Response, g, jsonify, request
from vpndetection.middleware import (
    Core,
    IpSelector,
    Lookup,
    Options,
    RequestView,
    Selectors,
    bind_selectors,
)
from werkzeug.wrappers import Request as WerkzeugRequest

__all__ = [
    "VPNDetection",
    "default_ip_selector",
    "header_ip_selector",
    "lookup",
    "xff_ip_selector",
]

__version__ = "2.0.1"

_SELECTORS: Selectors[WerkzeugRequest] = bind_selectors(
    lambda req: RequestView(
        header=lambda name: req.headers.get(name),
        framework_ip=lambda: req.remote_addr,
    )
)

#: ``request.remote_addr``, which is the socket peer unless you have wrapped the app in
#: werkzeug's ``ProxyFix``.
#:
#: Behind a load balancer without it, every visitor looks like the load balancer - a
#: datacenter address a hosting rule would block them all for. If you are behind one,
#: add ``ProxyFix`` (Flask's own answer) or use :func:`header_ip_selector`.
default_ip_selector: IpSelector[WerkzeugRequest] = _SELECTORS.default

#: An address from ``X-Forwarded-For``.
#:
#: The LEFT-MOST entry (``depth`` 0) is whatever the caller sent, because proxies
#: append to this header. It is only trustworthy when an edge you control overwrites
#: it. When you know how many proxies sit in front, count from the right:
#: ``xff_ip_selector(1)`` is the address your nearest proxy saw.
xff_ip_selector = _SELECTORS.xff

#: An address from a single-value header your edge writes -
#: ``header_ip_selector("CF-Connecting-IP")`` behind Cloudflare. Falls back to
#: ``remote_addr`` when the header is absent.
header_ip_selector = _SELECTORS.header


def lookup() -> Lookup | None:
    """What the extension found out about this visitor.

    None when the extension has not run for this request, or when ``skip`` claimed it.
    """
    return getattr(g, "vpndetection", None)


class VPNDetection:
    """Classify the visitor, and optionally refuse the request.

    Takes everything :class:`vpndetection.middleware.Options` does, plus ``on_blocked``.

    Without a ``block_condition`` this only enriches the request and never refuses one,
    leaving the decision to your own views. A lookup that fails - network, quota, an
    outage of ours - lets the request through and records why on ``lookup().error``,
    unless you set ``fail_closed``.
    """

    def __init__(
        self,
        app: Flask | None = None,
        *,
        on_blocked: Callable[[Lookup], Response] | None = None,
        **options: Any,
    ) -> None:
        self._on_blocked = on_blocked or _refuse
        self._core: Core[WerkzeugRequest] = Core(Options(**options), default_ip_selector)
        if app is not None:
            self.init_app(app)

    def init_app(self, app: Flask) -> None:
        """Register on an app, for the factory pattern."""
        app.extensions.setdefault("vpndetection", self)
        app.before_request(self._before_request)

    def _before_request(self) -> Response | None:
        found = self._core.evaluate(request)
        if found is None:
            return None
        g.vpndetection = found
        if found.blocked:
            # Returning a response from before_request is what STOPS the view from
            # running; merely building one would let the request through.
            return self._on_blocked(found)
        return None


def _refuse(_lookup: Lookup) -> Response:
    response = jsonify({"error": "access denied"})
    response.status_code = 403
    return response
