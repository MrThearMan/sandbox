import json
from dataclasses import dataclass
from typing import TYPE_CHECKING

from prff import constants
from prff.logging import SUMMARY, logger

if TYPE_CHECKING:
    from prff.github_schema import IssueCommentEvent


__all__ = [
    "load_event_data",
]


@dataclass
class EventData:
    pull_request_url: str
    permissions_url: str
    reactions_url: str


def load_event_data() -> EventData:
    logger.info("Loading GitHub Actions event data from file...")

    with open(constants.EVENT_PATH, encoding="utf-8") as f:  # noqa: PTH123
        event: IssueCommentEvent = json.load(f)

    logger.info("Event data loaded.")
    logger.info("Parsing event data...")

    pull_request_url = event["issue"]["pull_request"]["url"]

    username = event["sender"]["login"]
    collaborators_url = event["repository"]["collaborators_url"].format(**{"/collaborator": f"/{username}"})
    permissions_url = f"{collaborators_url}/permission"

    comment_url = event["comment"]["url"]
    reactions_url = f"{comment_url}/reactions"

    logger.info("Event data parsed.")

    return EventData(
        pull_request_url=pull_request_url,
        permissions_url=permissions_url,
        reactions_url=reactions_url,
    )


def write_job_summary() -> None:
    SUMMARY.seek(0)
    summary = str(SUMMARY.read())
    with open(constants.SUMMARY_FILE, "w") as summary_file:  # noqa: PTH123
        summary_file.write(summary)
