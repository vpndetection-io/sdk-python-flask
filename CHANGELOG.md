# Changelog

What each release changed for you, newest first. Each line is a commit's summary, linked to its full description and diff. Releases before 2.0.5 are described by their release commits.

## 2.1.14 - 2026-10-28

### Fixes

- Require vpndetection 5.12.3: a date-time whose T or Z is lowercase is read ([`1a0b641`](https://github.com/vpndetection-io/sdk-python-flask/commit/1a0b6417a903bb88dd022b1b5258506a34a6376a))

## 2.1.13 - 2026-10-26

### Fixes

- Require vpndetection 5.12.2: re-pinned to the 2026.10.25 spec ([`08c77c3`](https://github.com/vpndetection-io/sdk-python-flask/commit/08c77c36fce20b1a15b5815b77283532af6b6709))

## 2.1.12 - 2026-10-25

### Fixes

- Require vpndetection 5.12.1: retry counts and dates are checked ([`dd220f6`](https://github.com/vpndetection-io/sdk-python-flask/commit/dd220f68342359f7c20bd33a999080626e69ed8f))

## 2.1.11 - 2026-10-23

### Fixes

- Require vpndetection 5.12.0, which adds oauth.register ([`f884727`](https://github.com/vpndetection-io/sdk-python-flask/commit/f8847278743b8c2740f5e53ff4dea016e588d08c))

## 2.1.10 - 2026-10-22

### Fixes

- Require vpndetection 5.11.1: a wrong-typed member is a server_error ([`2213a2d`](https://github.com/vpndetection-io/sdk-python-flask/commit/2213a2d8140055b6ff793b4ba6ea7f2662ba6868))

## 2.1.9 - 2026-10-20

### Features

- Require vpndetection 5.11.0: lookup results carry location and asn ([`e347a91`](https://github.com/vpndetection-io/sdk-python-flask/commit/e347a91c3f0f9f8467487cf03b953335deb4e9fa))

## 2.1.8 - 2026-10-19

### Fixes

- Require vpndetection 5.10.0: num_ports and num_proxies in the pubproxy detail ([`c7ced24`](https://github.com/vpndetection-io/sdk-python-flask/commit/c7ced2429460f978dea05ee374919b9b8eafa2a8))

## 2.1.7 - 2026-10-18

### Fixes

- Require vpndetection 5.9.0: is_pubproxy and the pubproxy detail ([`bcf1c47`](https://github.com/vpndetection-io/sdk-python-flask/commit/bcf1c474af70b513d339f6dfec6a8d33d05d3ce6))

## 2.1.6 - 2026-10-17

### Features

- Require vpndetection 5.8.0: OauthMetadata carries registration_endpoint ([`f2af483`](https://github.com/vpndetection-io/sdk-python-flask/commit/f2af483eb0610fbfe43b1cae501fb5945636ebc7))

## 2.1.5 - 2026-10-16

### Fixes

- Require vpndetection 5.7.3: the spec re-pinned to 2026.10.15 ([`1df70b0`](https://github.com/vpndetection-io/sdk-python-flask/commit/1df70b008137578382f1ceca8b993be2725c9361))

## 2.1.4 - 2026-10-15

### Fixes

- Require vpndetection 5.7.2: Retry-After, the key, the base URL and unreadable answers ([`5cade35`](https://github.com/vpndetection-io/sdk-python-flask/commit/5cade3560e8034e61ebb06246713d3cb31ed8abd))

## 2.1.3 - 2026-10-10

### Fixes

- Require vpndetection 5.7.1: the spec re-pinned to 2026.10.09 ([`a7b2970`](https://github.com/vpndetection-io/sdk-python-flask/commit/a7b297016d96f145b571611ab1ee00fcf122d459))

## 2.1.2 - 2026-10-06

### Features

- Require vpndetection 5.7.0: the authorization code sign-in ([`84075cc`](https://github.com/vpndetection-io/sdk-python-flask/commit/84075ccacb9acca92fe38a0d843c655b6f087ba4))

## 2.1.1 - 2026-10-04

### Fixes

- Require vpndetection 5.6.1, re-pinned to spec 2026.10.03 ([`dcb9d10`](https://github.com/vpndetection-io/sdk-python-flask/commit/dcb9d10e9ccce93ba8797d70e23749601a133455))

## 2.1.0 - 2026-10-03

### Features

- Add block_if, a decorator refusing one view to a visitor matching a condition ([`a376d74`](https://github.com/vpndetection-io/sdk-python-flask/commit/a376d74867e3e8f6b785dd67bda86507554b033d))

## 2.0.9 - 2026-10-02

### Fixes

- Require vpndetection 5.5.3: a long Retry-After or timeout no longer raises OverflowError ([`438e0ed`](https://github.com/vpndetection-io/sdk-python-flask/commit/438e0ed957e5c9c918cf11e2547c5bbee43abe56))

## 2.0.8 - 2026-09-29

### Fixes

- Require vpndetection 5.5.2: 26 more reserved ranges are answered locally ([`64c2a46`](https://github.com/vpndetection-io/sdk-python-flask/commit/64c2a461290a6a9bed3db6be17a51df93950fcfb))

## 2.0.7 - 2026-09-28

### Fixes

- Require vpndetection 5.5.1: IPv4-mapped visitors are looked up, not waved through ([`a946afc`](https://github.com/vpndetection-io/sdk-python-flask/commit/a946afc6955f6261da401c03c6d418d2f678d065))

## 2.0.6 - 2026-09-27

### Features

- Require vpndetection 5.5.0: OauthMetadata carries client_id_metadata_document_supported ([`4d6b906`](https://github.com/vpndetection-io/sdk-python-flask/commit/4d6b906b30b98635d4e79c650ade22543d55799e))

## 2.0.5 - 2026-09-25

### Fixes

- Raise the base floor to vpndetection 5.4.2 ([`5edfe0e`](https://github.com/vpndetection-io/sdk-python-flask/commit/5edfe0ee9bb73000cdd658f7e31d412bb0d69e47))
