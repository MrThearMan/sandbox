from __future__ import annotations

import urllib.parse
from dataclasses import dataclass
from typing import TYPE_CHECKING, Self

from prff import constants
from prff.command import run_command
from prff.exception import PullRequestFastForwardError
from prff.http_requests import get_request
from prff.logging import logger

if TYPE_CHECKING:
    from prff.github_schema import PullRequest

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

    @classmethod
    def from_github(cls, *, url: str) -> Self:
        logger.info("Fetching pull request data from GitHub...")

        response: PullRequest | None = get_request(url=url)
        if not response:
            msg = "Could not get pull request"
            raise PullRequestFastForwardError(msg)

        logger.info("Pull request data received.")
        logger.info("Parsing pull request data...")

        info = PullRequestData(
            base_clone_url=response["base"]["repo"]["clone_url"],
            base_branch_name=response["base"]["ref"],
            base_head_sha=response["base"]["sha"],
            pr_clone_url=response["head"]["repo"]["clone_url"],
            pr_branch_name=response["head"]["ref"],
            pr_head_sha=response["head"]["sha"],
        )

        logger.info("Pull request data parsed.")
        return info

    @property
    def auth_base_clone_url(self) -> str:
        return self.add_actor_to_clone_url(url=self.base_clone_url)

    @property
    def auth_pr_clone_url(self) -> str:
        return self.add_actor_to_clone_url(url=self.pr_clone_url)

    @staticmethod
    def add_actor_to_clone_url(*, url: str) -> str:
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

        logger.debug(f"Base Ref: {self.base_branch_name}")
        logger.debug(f"Base SHA (original): {self.base_head_sha}")
        logger.debug(f"Base SHA (current): {result.out}")
        logger.debug(f"PR Ref: {self.pr_branch_name}")
        logger.debug(f"PR SHA: {self.pr_head_sha}")

        self.base_head_sha = result.out
