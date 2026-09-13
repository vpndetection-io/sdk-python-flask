"""The extension, through a real Flask request cycle, plus the shared corpus.

A test client connects from ``127.0.0.1``, which is a bogon and is answered locally
without a request. Anything that needs a served answer therefore has to arrive wearing
a public address, through a selector.
"""

from __future__ import annotations

import json
import pathlib
from typing import Any

import httpx
import pytest
from flask import Flask, jsonify
from vpndetection import VPNDetection as Client

from vpndetection_flask import (
    VPNDetection,
    default_ip_selector,
    header_ip_selector,
    lookup,
    xff_ip_selector,
)

PUBLIC_IP = "45.83.91.1"
CORPUS = json.loads(
    (pathlib.Path(__file__).parent.parent / "testdata/testdata.json").read_text()
)
MIDDLEWARE = CORPUS["middleware"]


def serving(body: dict[str, Any], *, status: int = 200) -> Client:
    """A client whose every answer is ``body``, recording what it was asked about."""

    def handle(request: httpx.Request) -> httpx.Response:
        ip = request.url.path.lstrip("/")
        asked.append(ip)
        return httpx.Response(status, json={"ip": ip, **body})

    asked: list[str] = []
    client = Client(cache=False, retries=0, transport=httpx.MockTransport(handle))
    client.asked = asked  # type: ignore[attr-defined]
    return client


def app_with(**options: Any) -> Flask:
    app = Flask(__name__)
    VPNDetection(app, **options)

    @app.route("/")
    def index() -> Any:
        found = lookup()
        return jsonify(
            {
                "ip": found.ip if found else None,
                "is_vpn": found.result.is_vpn if found and found.result else None,
                "is_bogon": found.result.is_bogon if found and found.result else None,
                "error": type(found.error).__name__ if found and found.error else None,
                "attached": found is not None,
            }
        )

    return app


def get(app: Flask, headers: dict[str, str] | None = None) -> tuple[int, dict[str, Any]]:
    response = app.test_client().get("/", headers=headers or {})
    return response.status_code, response.get_json()


def fixed_ip(_request: Any) -> str:
    return PUBLIC_IP


def test_enriches_the_request_and_leaves_the_decision_to_the_app() -> None:
    client = serving({"is_vpn": True, "vpn": {"provider": "nordvpn"}})
    status, body = get(app_with(client=client, ip_selector=fixed_ip))
    assert status == 200
    assert body["attached"] is True and body["is_vpn"] is True and body["ip"] == PUBLIC_IP
    assert client.asked == [PUBLIC_IP]


def test_blocks_when_the_condition_matches_and_the_view_never_runs() -> None:
    vpn = serving({"is_vpn": True, "vpn": {"provider": "nordvpn"}})
    status, body = get(
        app_with(client=vpn, ip_selector=fixed_ip, block_condition={"is_vpn": True})
    )
    assert status == 403
    assert body == {"error": "access denied"}

    clean = serving({"is_vpn": False, "vpn": {}})
    status, _ = get(
        app_with(client=clean, ip_selector=fixed_ip, block_condition={"is_vpn": True})
    )
    assert status == 200


def test_a_condition_reaches_the_evidence_fields() -> None:
    nord = serving({"is_vpn": True, "vpn": {"provider": "nordvpn"}})
    status, _ = get(
        app_with(
            client=nord, ip_selector=fixed_ip, block_condition={"vpn": {"provider": "mullvad"}}
        )
    )
    assert status == 200, "a different provider must not match"

    mullvad = serving({"is_vpn": True, "vpn": {"provider": "MULLVAD"}})
    status, _ = get(
        app_with(
            client=mullvad,
            ip_selector=fixed_ip,
            block_condition={"vpn": {"provider": "mullvad"}},
        )
    )
    assert status == 403, "a provider must compare without case"


def test_on_blocked_replaces_the_refusal() -> None:
    client = serving({"is_vpn": True, "vpn": {"provider": "nordvpn"}})
    app = app_with(
        client=client,
        ip_selector=fixed_ip,
        block_condition={"is_vpn": True},
        on_blocked=lambda found: (jsonify({"why": found.result.vpn.provider}), 451),
    )
    response = app.test_client().get("/")
    assert response.status_code == 451
    assert response.get_json() == {"why": "nordvpn"}


def test_skip_leaves_the_request_untouched() -> None:
    client = serving({"is_vpn": True})
    status, body = get(
        app_with(
            client=client,
            ip_selector=fixed_ip,
            block_condition={"is_vpn": True},
            skip=lambda request: request.path == "/",
        )
    )
    assert status == 200 and body["attached"] is False
    assert client.asked == []


def test_a_failing_lookup_lets_the_visitor_through() -> None:
    failing = serving({"error": "boom"}, status=500)
    status, body = get(
        app_with(client=failing, ip_selector=fixed_ip, block_condition={"is_vpn": True})
    )
    assert status == 200
    assert body["error"] == "VPNDetectionError"


# The test that matters. Every other assertion here would pass whether or not the
# selector is right, because a direct connection has nothing to confuse.
def test_a_forged_x_forwarded_for_is_ignored_by_default() -> None:
    client = serving({"is_vpn": True})
    _, body = get(app_with(client=client), {"X-Forwarded-For": PUBLIC_IP})
    assert body["ip"] == "127.0.0.1", "remote_addr is the socket peer; the header is a forgery"
    assert client.asked == [], "and a bogon is answered locally, so nothing was asked"

    explicit = serving({"is_vpn": True})
    _, body = get(
        app_with(client=explicit, ip_selector=xff_ip_selector()), {"X-Forwarded-For": PUBLIC_IP}
    )
    assert body["ip"] == PUBLIC_IP
    assert explicit.asked == [PUBLIC_IP]


def test_a_header_selector_reads_the_edge_that_writes_it() -> None:
    client = serving({"is_vpn": True})
    _, body = get(
        app_with(client=client, ip_selector=header_ip_selector("CF-Connecting-IP")),
        {"CF-Connecting-IP": "45.83.91.9"},
    )
    assert body["ip"] == "45.83.91.9"
    assert client.asked == ["45.83.91.9"]


def test_depth_counts_trusted_hops_from_the_right() -> None:
    client = serving({"is_vpn": True})
    get(
        app_with(client=client, ip_selector=xff_ip_selector(1)),
        {"X-Forwarded-For": f"{PUBLIC_IP}, 70.41.3.18, 150.172.238.178"},
    )
    assert client.asked == ["150.172.238.178"]


def test_a_private_client_address_is_answered_locally_and_never_blocks() -> None:
    client = serving({"is_vpn": True})
    status, body = get(
        app_with(
            client=client, block_condition={"is_vpn": True}, ip_selector=default_ip_selector
        )
    )
    assert status == 200, "local development must not lock you out of your own app"
    assert body["is_bogon"] is True
    assert client.asked == []


def test_a_condition_that_constrains_nothing_is_refused_at_construction() -> None:
    with pytest.raises(ValueError, match="constrains nothing"):
        VPNDetection(block_condition={"is_vpn": False})


@pytest.mark.parametrize("case", MIDDLEWARE["conditions"], ids=lambda c: c["name"])
def test_corpus_conditions(case: dict[str, Any]) -> None:
    ip = case.get("bogon") or case["body"]["ip"]
    client = serving({k: v for k, v in (case.get("body") or {}).items() if k != "ip"})
    warnings: list[str] = []
    status, _ = get(
        app_with(
            client=client,
            ip_selector=lambda _request, ip=ip: ip,
            block_condition=case["condition"],
            on_warn=warnings.append,
        )
    )
    assert status == (403 if case["expect"]["blocked"] else 200), case["why"]
    reported = [w for w in warnings if "does not include" in w]
    assert len(reported) == (1 if case["expect"]["missing"] else 0), case["why"]
    for member in case["expect"]["missing"]:
        assert member in reported[0], case["why"]
