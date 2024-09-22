from __future__ import annotations

import urllib.parse
from dataclasses import dataclass
from typing import Self

from prff import constants
from prff.command import run_command
from prff.exception import PullRequestFastForwardError
from prff.github_api import fetch_pull_request
from prff.logging import logger

__all__ = [
    "PullRequestData",
]


@dataclass
class PullRequestData:
    base_clone_url: str
    """Clone URL for the pull request's base branch."""

    base_branch_name: str
    """Name for the pull request's base branch."""

    base_head_sha: str
    """Commit SHA for the pull request's base branch's head commit."""

    pr_clone_url: str
    """Clone URL for the pull request's branch."""

    pr_branch_name: str
    """Name for the pull request's branch."""

    pr_head_sha: str
    """Commit SHA for the pull request branch's head commit."""

    comments_url: str
    """GitHub API URL to post error comments to."""

    @classmethod
    def from_github(cls, *, url: str) -> Self:
        response = fetch_pull_request(url=url)
        logger.info("Parsing pull request data...")

        info = PullRequestData(
            base_clone_url=cls.add_auth(url=response["base"]["repo"]["clone_url"]),
            base_branch_name=response["base"]["ref"],
            base_head_sha=response["base"]["sha"],
            pr_clone_url=cls.add_auth(url=response["head"]["repo"]["clone_url"]),
            pr_branch_name=response["head"]["ref"],
            pr_head_sha=response["head"]["sha"],
            comments_url=response["comments_url"],
        )

        logger.info("Pull request data parsed.")
        return info

    @staticmethod
    def add_auth(*, url: str) -> str:
        clone_url_parts = urllib.parse.urlparse(url)._asdict()
        clone_url_parts["netloc"] = f"{constants.GITHUB_ACTOR}:{constants.GITHUB_TOKEN}@{clone_url_parts['netloc']}"
        return urllib.parse.urlunparse(clone_url_parts.values())  # type: ignore[return-value]

    def fix_base_sha(self) -> None:
        # 'base_sha' is not updated correctly when the PR base is changed.
        # See. https://github.com/orgs/community/discussions/59677
        # Therefore, we need to parse the actual base SHA from the cloned repo.
        logger.info("Parsing base ref...")

        result = run_command(f"git rev-parse origin/{self.base_branch_name}", directory=constants.REPO_PATH)
        if result.err is not None:
            msg = f"Could not parse base ref. Error: {result.err}"
            raise PullRequestFastForwardError(msg)

        logger.info("Base ref parsed.")
        self.base_head_sha = result.out
