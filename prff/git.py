from __future__ import annotations

from prff import constants
from prff.command import run_command
from prff.exception import PullRequestFastForwardError
from prff.logging import logger

__all__ = [
    "approve_git_credentials",
    "clone_repo_at_ref",
    "create_branch",
    "fetch_ref",
    "set_git_credential_helper_to_store",
    "validate_fast_forward",
]


def set_git_credential_helper_to_store() -> None:
    """
    Sets the git credential.helper to use the on-disk store.
    See: https://git-scm.com/docs/git-credential-store
    """
    logger.info("Configure git 'credential.helper' to use on-disk store...")

    result = run_command("git config --global credential.helper store")
    if result.exit_code != 0:
        msg = f"Could not set git 'credential.helper' to store. Error: {result.err}"
        raise PullRequestFastForwardError(msg)

    logger.info("Git 'credential.helper' set.")


def approve_git_credentials(*, clone_url: str) -> None:
    """
    Approves the git credentials for the given clone URL.

    :param clone_url: The URL of the repository to approve the credentials for.
    """
    logger.info("Approving git credentials...")

    credentials = f"url={clone_url}\nusername={constants.GITHUB_ACTOR}\npassword={constants.GITHUB_TOKEN}"

    result = run_command(f'echo -e "{credentials}" | git credential approve')
    if result.exit_code != 0:
        msg = f"Could not approve git credentials. Error: {result.err}"
        raise PullRequestFastForwardError(msg)

    logger.info("Git credentials approved.")


def clone_repo_at_ref(*, clone_url: str, ref: str) -> None:
    """
    Clones the repository at the specified reference.
    Only the specified reference is cloned, not the entire repository.
    Repo is cloned to the 'REPO_PATH'.

    :param clone_url: The URL of the repository to clone.
    :param ref: The reference to clone.
    """
    logger.info(f"Cloning '{ref}' from '{clone_url}'...")

    result = run_command(f"git clone --quiet --single-branch --branch {ref} {clone_url} {constants.REPO_PATH}")
    if result.exit_code != 0:
        msg = f"Could not clone base ref. Error: {result.err}"
        raise PullRequestFastForwardError(msg)

    logger.info("Repo cloned.")


def fetch_ref(*, clone_url: str, ref: str) -> None:
    """
    Fetches the specified reference from the repository.

    :param clone_url: The URL of the repository to fetch from.
    :param ref: The reference to fetch.
    """
    logger.info(f"Fetching '{ref}' from '{clone_url}'...")

    result = run_command(f"git fetch --quiet {clone_url} {ref}", directory=constants.REPO_PATH)
    if result.exit_code != 0:
        msg = f"Could not fetch pull request ref. Error: {result.err}"
        raise PullRequestFastForwardError(msg)

    logger.info("Ref fetched.")


def create_branch(*, name: str, sha: str) -> None:
    """
    Creates a new branch to the given commit with the given name.

    Note: Adding a commit to a branch removes it from a detached state (e.g. from 'fetch_ref').

    :param name: The name of the new branch.
    :param sha: The commit SHA to create the branch from.
    """
    logger.info(f"Creating a new branch '{name}' at '{sha[:7]}'...")

    result = run_command(f"git branch -f {name} {sha}", directory=constants.REPO_PATH)
    if result.exit_code != 0:
        msg = f"Could not add commit to branch. Error: {result.err}"
        raise PullRequestFastForwardError(msg)

    logger.info("Branch created.")


def validate_fast_forward(*, base_sha: str, head_sha: str) -> None:
    """
    Checks if the base SHA can be fast-forwarded to the head SHA.

    :param base_sha: The base SHA to check.
    :param head_sha: The head SHA to check.
    """
    logger.info(f"Checking if '{base_sha[:7]}' can fast forwarded to '{head_sha[:7]}'...")

    result = run_command(f"git merge-base --is-ancestor {base_sha} {head_sha}", directory=constants.REPO_PATH)
    if result.exit_code != 0:
        msg = f"Cannot fast forward '{base_sha[:7]}' to '{head_sha[:7]}'. Error: {result.err}"
        raise PullRequestFastForwardError(msg)

    logger.info("Fast forwarding is possible.")


def push_branch_to_ref(*, branch: str, sha: str) -> None:
    """
    Pushes the specified branch to the specified SHA by fast-forwarding.

    :param branch: The branch to fast-forward.
    :param sha: The commit SHA to push to the head of the branch.
    """
    logger.info("Pushing branch to ref by fast-forwarding...")

    result = run_command(f"git push origin {sha}:{branch}", directory=constants.REPO_PATH)
    if result.exit_code != 0:
        msg = f"Could not fast forward '{branch}' to '{sha}'. Error: {result.err}"
        raise PullRequestFastForwardError(msg)

    logger.info("Fast-forwarding done.")
