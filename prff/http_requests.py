from __future__ import annotations

import http.client
import json
import urllib.parse
from typing import Any

from prff import constants
from prff.logging import logger

__all__ = [
    "get_request",
]


def get_request(*, url: str) -> dict[str, Any] | None:
    url_parts = urllib.parse.urlparse(url)

    connection = http.client.HTTPSConnection(url_parts.netloc)

    github_api_headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {constants.GITHUB_TOKEN}",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "MrThearMan-GitHub-Fast-Forward-Action",
    }

    try:
        connection.request("GET", url=url_parts.path, headers=github_api_headers)
        response = connection.getresponse()
        content = response.read().decode()
    finally:
        connection.close()

    if response.status != 200:  # noqa: PLR2004
        logger.error(f"Unexpected status code: {response.status}: {content}")
        return None

    try:
        return json.loads(content)
    except Exception as error:  # noqa: BLE001
        logger.error(f"Could not decode JSON: {error}")
        return None
