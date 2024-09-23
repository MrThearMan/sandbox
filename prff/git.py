from __future__ import annotations

from prff import constants
from prff.command import run_command
from prff.exception import PullRequestFastForwardError
from prff.logging import logger

__all__ = [
    "clone_repo_at_branch",
    "create_branch",
    "fetch_commit",
    "validate_fast_forward",
]


def clone_repo_at_branch(*, repo_url: str, branch_name: str) -> None:
    """
    Clones the repository at the specified branch.
    Only that branch is cloned, not the entire repository.
    Repo is cloned to the 'REPO_PATH'.

    :param repo_url: The URL of the repository to clone.
    :param branch_name: The branch to clone.
    """
    logger.info(f"Cloning repo `{repo_url}` at branch `{branch_name}`...")

    result = run_command(f"git clone --quiet --single-branch --branch {branch_name} {repo_url} {constants.REPO_PATH}")
    if result.exit_code != 0:
        msg = f"Could not clone branch `{branch_name}`."
        if result.err:
            msg += f" Error: {result.err}"
        raise PullRequestFastForwardError(msg)

    logger.info("Repo cloned.")


def fetch_commit(*, repo_url: str, commit_sha: str) -> None:
    """
    Fetches commits until the specified commit SHA from the given repository.
    Operation is performed in the 'REPO_PATH'.

    :param repo_url: The URL of the repository to fetch from.
    :param commit_sha: The commit to target.
    """
    logger.info(f"Fetching commit `{commit_sha[:7]}` from repo `{repo_url}`...")

    result = run_command(f"git fetch --quiet {repo_url} {commit_sha}", directory=constants.REPO_PATH)
    if result.exit_code != 0:
        msg = f"Could not fetch commit `{commit_sha[:7]}`."
        if result.err:
            msg += f" Error: {result.err}"
        raise PullRequestFastForwardError(msg)

    logger.info("Commit fetched.")


def create_branch(*, branch_name: str, commit_sha: str) -> None:
    """
    Creates a new branch at the given commit SHA with the given name.
    Operation is performed in the 'REPO_PATH'.

    Note: Adding a commit to a branch removes it from a detached state (e.g. from 'fetch_commit').

    :param branch_name: The name of the new branch.
    :param commit_sha: The commit SHA to create the branch from.
    """
    logger.info(f"Creating a new branch `{branch_name}` at `{commit_sha[:7]}`...")

    result = run_command(f"git branch -f {branch_name} {commit_sha}", directory=constants.REPO_PATH)
    if result.exit_code != 0:
        msg = f"Could not create branch at commit `{commit_sha[:7]}`."
        if result.err:
            msg += f" Error: {result.err}"
        raise PullRequestFastForwardError(msg)

    logger.info("Branch created.")


def validate_fast_forward(*, base_sha: str, head_sha: str) -> None:
    """
    Checks if the base commit can be fast-forwarded to the head commit.
    Operation is performed in the 'REPO_PATH'.

    :param base_sha: The commit to check fast-forwarding for.
    :param head_sha: The commit to check fast-forwarding against.
    """
    logger.info(f"Checking if `{base_sha[:7]}` can be fast-forwarded to `{head_sha[:7]}`...")

    result = run_command(f"git merge-base --is-ancestor {base_sha} {head_sha}", directory=constants.REPO_PATH)
    if result.exit_code != 0:
        msg = f"Cannot fast-forward `{base_sha[:7]}` to `{head_sha[:7]}`."
        if result.err:
            msg += f" Error: {result.err}"
        raise PullRequestFastForwardError(msg)

    logger.info("Fast-forwarding is possible.")


def push_branch_to_commit(*, branch_name: str, commit_sha: str) -> None:
    """
    Pushes the specified branch to the specified SHA by fast-forwarding.
    Operation is performed in the 'REPO_PATH'.

    Note: Since we are using the 'GITHUB_TOKEN', push doesn't trigger additional workflows.
    https://docs.github.com/actions/security-for-github-actions/security-guides/automatic-token-authentication

    :param branch_name: The branch to push.
    :param commit_sha: The commit SHA to push to the head of the branch to.
    """
    logger.info(f"Pushing `{branch_name}` to `{commit_sha[:7]}`...")

    result = run_command(f"git push origin {commit_sha}:{branch_name}", directory=constants.REPO_PATH)
    if result.exit_code != 0:
        msg = f"Could not push `{branch_name}` to `{commit_sha[:7]}`."
        if result.err:
            msg += f" Error: {result.err}"
        raise PullRequestFastForwardError(msg)

    logger.info("Push successful.")
