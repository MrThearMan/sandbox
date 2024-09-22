from __future__ import annotations

import json
from typing import TYPE_CHECKING

from prff.logging import logger

if TYPE_CHECKING:
    from prff.github_schema import IssueCommentEvent

__all__ = [
    "load_issue_comment_event",
]


def load_issue_comment_event(*, path: str) -> IssueCommentEvent:
    logger.info(f"Loading github event from '{path}'...")

    with open(path, encoding="utf-8") as f:  # noqa: PTH123
        data: IssueCommentEvent = json.load(f)

    logger.info("PR event loaded...")
    return data
