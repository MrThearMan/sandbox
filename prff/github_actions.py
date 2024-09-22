import json
from typing import TYPE_CHECKING

from prff import constants
from prff.logging import SUMMARY, logger

if TYPE_CHECKING:
    from prff.github_schema import IssueCommentEvent


__all__ = [
    "load_urls_from_event",
]


def load_urls_from_event() -> tuple[str, str]:
    logger.info("Loading GitHub Actions event data...")

    with open(constants.EVENT_PATH, encoding="utf-8") as f:  # noqa: PTH123
        event: IssueCommentEvent = json.load(f)

    logger.info("Event data loaded.")
    logger.info("Parsing pull request URL and permissions URL from event data...")

    pull_request_url = event["issue"]["pull_request"]["url"]

    username = event["sender"]["login"]
    collaborators_url = event["repository"]["collaborators_url"].format(**{"/collaborator": f"/{username}"})
    permissions_url = f"{collaborators_url}/permission"

    logger.info("URLs parsed.")

    return pull_request_url, permissions_url


def write_job_summary() -> None:
    SUMMARY.seek(0)
    summary = str(SUMMARY.read())
    with open(constants.SUMMARY_FILE, "w") as summary_file:  # noqa: PTH123
        summary_file.write(summary)
