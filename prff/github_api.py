from __future__ import annotations

import http.client
import json
import urllib.parse
from inspect import cleandoc
from typing import TYPE_CHECKING, Any

from prff import constants
from prff.exception import PullRequestFastForwardError
from prff.logging import logger

if TYPE_CHECKING:
    from prff.github_schema import PullRequest, UserPermission

__all__ = [
    "fetch_pull_request",
    "fetch_user_permissions",
    "post_error_comment",
    "validate_push_permissions",
]


_GITHUB_API_HEADERS = {
    "Accept": "application/vnd.github+json",
    "Authorization": f"Bearer {constants.GITHUB_TOKEN}",
    "X-GitHub-Api-Version": "2022-11-28",
    "User-Agent": "MrThearMan-GitHub-Fast-Forward-Action",
}


def get_request(*, url: str) -> dict[str, Any] | None:
    url_parts = urllib.parse.urlparse(url)

    connection = http.client.HTTPSConnection(url_parts.netloc)

    headers = _GITHUB_API_HEADERS.copy()

    try:
        connection.request("GET", url=url_parts.path, headers=headers)
        response = connection.getresponse()
        content = response.read().decode()
    finally:
        connection.close()

    if 200 <= response.status < 300:  # noqa: PLR2004
        logger.error(f"Unexpected status code: {response.status}: {content}")
        return None

    try:
        return json.loads(content)
    except Exception as error:  # noqa: BLE001
        logger.error(f"Could not decode JSON response: {error}")
        return None


def post_request(*, url: str, data: dict[str, Any]) -> dict[str, Any] | None:
    url_parts = urllib.parse.urlparse(url)

    connection = http.client.HTTPSConnection(url_parts.netloc)

    headers = _GITHUB_API_HEADERS.copy()
    headers["Content-Type"] = "application/json"

    body = json.dumps(data, separators=(",", ":"))

    try:
        connection.request("POST", url=url_parts.path, body=body, headers=headers)
        response = connection.getresponse()
        content = response.read().decode()
    finally:
        connection.close()

    if 200 <= response.status < 300:  # noqa: PLR2004
        logger.error(f"Unexpected status code: {response.status}: {content}")
        return None

    try:
        return json.loads(content)
    except Exception as error:  # noqa: BLE001
        logger.error(f"Could not decode JSON response: {error}")
        return None


def fetch_pull_request(*, url: str) -> PullRequest:
    logger.info("Fetching pull request data from GitHub...")

    response: PullRequest | None = get_request(url=url)
    if not response:
        msg = "Could not get pull request"
        raise PullRequestFastForwardError(msg)

    logger.info("Pull request data received.")
    return response


def fetch_user_permissions(permissions_url: str) -> UserPermission:
    logger.info("Fetching user permissions...")

    response = get_request(url=permissions_url)
    if not response:
        msg = "Could not get permissions"
        raise PullRequestFastForwardError(msg)

    logger.info("Permissions received.")
    return response


def validate_push_permissions(*, permissions: UserPermission) -> None:
    username = permissions["user"]["login"]
    logger.info(f"Checking if user '{username}' has permissions for pushing to this repo...")

    if permissions["user"]["permissions"]["push"] is False:
        msg = f"User '{username}' does not have permissions for pushing to this repo."
        raise PullRequestFastForwardError(msg)

    logger.info(f"User '{username}' has the correct permissions.")


def post_error_comment(*, error: str, comments_url: str) -> None:
    data = {
        "body": cleandoc(
            f"""
            Failed to fast-forward the pull request:

            > {error}
            """
        )
    }
    response = post_request(url=comments_url, data=data)
    if not response:
        logger.error("Could not post comment to pull request")
