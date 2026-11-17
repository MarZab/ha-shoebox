"""Print an access token for the dev Home Assistant, onboarding it as dev/dev on first use.

Usage: dev_token.py [base URL]  (default http://localhost:8123)
"""

from __future__ import annotations

import json
import sys
from typing import Any
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

USER = {"name": "Dev", "username": "dev", "password": "dev", "language": "en"}


def call(
    url: str, data: dict[str, Any] | None = None, *, form: bool = False, token: str = ""
) -> Any:
    body = None
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    if data is not None:
        if form:
            body = urlencode(data).encode()
            headers["Content-Type"] = "application/x-www-form-urlencoded"
        else:
            body = json.dumps(data).encode()
            headers["Content-Type"] = "application/json"
    with urlopen(Request(url, body, headers)) as response:
        return json.loads(response.read() or b"null")


def token(base: str) -> str:
    client = f"{base}/"
    try:
        steps = {s["step"]: s["done"] for s in call(f"{base}/api/onboarding")}
    except HTTPError as err:
        if err.code != 404:  # 404: onboarding is finished and its API is gone
            raise
        steps = {"user": True, "core_config": True, "analytics": True, "integration": True}
    if not steps.get("user"):
        code = call(f"{base}/api/onboarding/users", USER | {"client_id": client})["auth_code"]
    else:
        flow = call(
            f"{base}/auth/login_flow",
            {"client_id": client, "handler": ["homeassistant", None], "redirect_uri": client},
        )
        login = {"username": USER["username"], "password": USER["password"], "client_id": client}
        code = call(f"{base}/auth/login_flow/{flow['flow_id']}", login)["result"]
    grant = {"grant_type": "authorization_code", "code": code, "client_id": client}
    access: str = call(f"{base}/auth/token", grant, form=True)["access_token"]
    for step, payload in (
        ("core_config", {}),
        ("analytics", {}),
        ("integration", {"client_id": client, "redirect_uri": client}),
    ):
        if not steps.get(step):
            call(f"{base}/api/onboarding/{step}", payload, token=access)
    return access


if __name__ == "__main__":
    sys.stdout.write(token(sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8123") + "\n")
