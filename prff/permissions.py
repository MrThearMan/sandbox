from __future__ import annotations

from typing import TYPE_CHECKING

from prff.exception import PullRequestFastForwardError
from prff.http_requests import get_request
from prff.logging import logger

if TYPE_CHECKING:
    from prff.github_schema import UserPermission

__all__ = [
    "fetch_user_permissions",
    "validate_push_permissions",
]


def fetch_user_permissions(permissions_url: str) -> UserPermission:
    logger.info("Fetching user permissions...")

    response = get_request(url=permissions_url)
    if not response:
        msg = "Could not get permissions"
        raise PullRequestFastForwardError(msg)

    logger.info("Permissions received.")
    return response


def validate_push_permissions(*, permissions: UserPermission) -> None:
    logger.info("Checking if user has permissions for pushing...")

    if permissions["user"]["permissions"]["push"] is False:
        msg = "User does not have permissions for pushing."
        raise PullRequestFastForwardError(msg)

    logger.info("User has permissions for pushing.")
