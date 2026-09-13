# [<img src="https://s3.vpndetection.io/vpndetection-public/brand/mark.svg" alt="VPNDetection" width="24"/>](https://vpndetection.io/) VPNDetection Flask Extension

[![PyPI](https://img.shields.io/pypi/v/vpndetection-flask.svg)](https://pypi.org/project/vpndetection-flask/)
[![license](https://img.shields.io/pypi/l/vpndetection-flask.svg)](LICENSE)

The official Flask Extension for the [VPNDetection](https://vpndetection.io) API.

It classifies the visitor behind each request — VPN, residential proxy, Tor, hosting, CDN, relay — and hands the answer to your code. Blocking is opt-in.

## Getting Started

```bash
pip install vpndetection-flask
```

Requires Python 3.11 or newer.

You need an API key. Create one in the [console](https://app.vpndetection.io); the free tier's allowance is counted per source address, and a server is a single source address, so a key is what makes this usable in production rather than optional.

```python
from flask import Flask
from vpndetection_flask import VPNDetection

app = Flask(__name__)
VPNDetection(app, api_key=os.environ["VPNDETECTION_API_KEY"])
```

`init_app(app)` is supported for the application-factory pattern.

```python
from vpndetection_flask import lookup


@app.route("/")
def index():
    found = lookup()
    return "Hello, VPN user" if found.result.is_vpn else "Hello"
```

By default nothing is blocked. Every request gets an answer and your own code decides what that means — which is usually what you want, because whether a VPN visitor is a problem depends entirely on what they are doing.

## Blocking

Pass a `block_condition` and a matching request is answered with `403` and never reaches your code.

```python
block_condition = {"is_vpn": True}
```

A condition is written in the shape of a result, keyed by the same names the API uses, and only the members you name are considered. That lets it reach the evidence, not just the flags:

```python
{"is_vpn": True, "vpn": {"provider": "nordvpn"}}  # one provider
{"is_resproxy": True, "resproxy": {"hits": {"gte": 5}}}  # a numeric threshold
{"vpn": {"confidence": ["high", "medium"]}}  # any of these
[{"is_tor": True}, {"is_resproxy": True}]  # a list is OR
```

Values are matched by equality, strings without regard to case. A list means any-of. A dict of `gte`/`gt`/`lte`/`lt` compares numbers, and every bound you give must hold, so two of them are a range. Members set to `False` or `None` are ignored, so a condition states the signals you act on; one that constrains nothing would match every request, and is refused when the middleware is built rather than silently blocking all your traffic.

Replace the refusal with `on_blocked`.

## Where the client address comes from

This is the setting that decides whether any of the above works, and it is the one thing only you can get right.

By default the extension uses `request.remote_addr`, which is the socket peer unless you have wrapped the app in werkzeug's `ProxyFix`. Behind a load balancer without it, every visitor looks like the load balancer — a datacenter address, so a hosting rule would block all of them. Adding `ProxyFix` is Flask's own answer and everything else here follows from it.

For an edge that writes the address into its own header, name the header:

```python
from python_flask import header_ip_selector

ip_selector = header_ip_selector("CF-Connecting-IP")  # or True-Client-IP, or your own
```

`xff_ip_selector()` reads `X-Forwarded-For` directly. Be aware that the left-most entry is whatever the caller sent, because proxies append to that header — it is only trustworthy when an edge you control overwrites it. If you know how many proxies sit in front, count from the right instead: `xff_ip_selector(1)` is the address your nearest proxy saw.

Anything else, pass your own callable. It receives the request and returns an address.

If the address resolves to a private one, the middleware says so once through the `vpndetection` logger. That is expected on localhost and is the signal to fix your configuration anywhere else.

## When a lookup fails

The request is let through, and the reason is recorded on the answer's `error`. Our outage should not become yours, so a network failure, an exhausted quota or a rejected key all fail open. Pass `fail_closed=True` to block instead. Private addresses are answered locally and never fail, so this will not lock you out in development.

## Cost and latency

Answers are cached for an hour, so a returning visitor costs nothing, and private addresses never leave the process. A cache miss is one request to our API, bounded at 2.5 seconds by default and not retried — on a request path, failing open quickly beats holding a visitor while we try again. Both are adjustable, as is the cache, through a `vpndetection` client you build yourself and pass as `client`.

Skip what you do not care about:

```python
skip = lambda request: request.path.startswith("/static")
```

Beyond a few million distinct visitors a day, stop calling the API per request: [download the dataset](https://vpndetection.io/databases) and look addresses up locally instead.

## Absent is not false

Only `ip` and `is_vpn` come back on every plan. A field your plan does not include is `None`, which means "not in your plan" rather than "checked, and no".

```python
lookup().result.is_hosting  # None when your plan does not include it
```

A `block_condition` naming a member your plan does not serve can never match, so the middleware warns once instead of failing silently. Pass `on_missing_field="raise"` to make it an error.

## Other Libraries

There are official VPNDetection client libraries available for many languages including PHP, Python, Go, Java, Ruby, and many popular frameworks such as Django, Rails, and Laravel. See our GitHub at https://github.com/vpndetection-io for more.

## About VPNDetection

VPN Detection API: Accurate anonymity detection identifying VPNs, residential proxies, hosting servers, Tor nodes, CDNs, relays and more.

[<img src="https://s3.vpndetection.io/vpndetection-public/brand/mark.svg" alt="VPNDetection" width="96"/>](https://vpndetection.io/)

## License

This project is licensed under the [MIT License](LICENSE).
