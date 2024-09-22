from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Self

from prff import constants
from prff.command import run_command
from prff.http_requests import get_request
from prff.logging import logger

if TYPE_CHECKING:
    from prff.github_schema import PullRequest

__all__ = [
    "PullRequestData",
]


@dataclass
class PullRequestData:
    clone_url: str
    base_ref: str
    base_sha: str
    head_ref: str
    head_sha: str

    @classmethod
    def from_github(cls, *, url: str) -> Self:
        logger.info("Fetching pull request data from GitHub...")

        response: PullRequest | None = get_request(url=url)
        if not response:
            msg = "Could not get pull request"
            raise RuntimeError(msg)

        logger.info("Pull request data received.")
        logger.info("Parsing pull request data...")

        info = PullRequestData(
            clone_url=response["base"]["repo"]["clone_url"],
            base_ref=response["base"]["ref"],
            base_sha=response["base"]["sha"],
            head_ref=response["head"]["ref"],
            head_sha=response["head"]["sha"],
        )

        logger.info("Pull request data parsed.")
        return info

    def fix_base_sha(self) -> None:
        # 'base_sha' is not updated correctly when the PR base is changed.
        # See. https://github.com/orgs/community/discussions/59677
        # Therefore, we need to parse the actual base SHA from the cloned repo.
        logger.info("Parsing base ref...")

        result = run_command(f"git rev-parse origin/{self.base_ref}", directory=constants.REPO_PATH)
        if result.err is not None:
            msg = f"Could not parse base ref. Error: {result.err}"
            raise RuntimeError(msg)

        logger.info("Base ref parsed.")

        logger.debug(f"Base Ref: {self.base_ref}")
        logger.debug(f"Base SHA (original): {self.base_sha}")
        logger.debug(f"Base SHA (current): {result.out}")
        logger.debug(f"PR Ref: {self.head_ref}")
        logger.debug(f"PR SHA: {self.head_sha}")

        self.base_sha = result.out
