from __future__ import annotations

from prff.git import (
    approve_git_credentials,
    clone_repo_at_ref,
    create_branch,
    fetch_ref,
    push_branch_to_ref,
    set_git_credential_helper_to_store,
    validate_fast_forward,
)
from prff.permissions import fetch_user_permissions, validate_push_permissions
from prff.pull_request import PullRequestData

__all__ = [
    "fast_forward_pull_request",
]


def fast_forward_pull_request(*, pull_request_url: str, permissions_url: str) -> None:
    permissions = fetch_user_permissions(permissions_url=permissions_url)
    validate_push_permissions(permissions=permissions)

    pull_request = PullRequestData.from_github(url=pull_request_url)

    set_git_credential_helper_to_store()
    approve_git_credentials(repo_url=pull_request.base_clone_url)
    if pull_request.pr_clone_url != pull_request.base_clone_url:
        approve_git_credentials(repo_url=pull_request.pr_clone_url)

    clone_repo_at_ref(repo_url=pull_request.auth_base_clone_url, branch_name=pull_request.base_branch_name)
    fetch_ref(repo_url=pull_request.auth_pr_clone_url, commit_sha=pull_request.pr_head_sha)
    create_branch(branch_name=pull_request.pr_branch_name, commit_sha=pull_request.pr_head_sha)

    pull_request.fix_base_sha()

    validate_fast_forward(base_sha=pull_request.base_head_sha, head_sha=pull_request.pr_head_sha)

    push_branch_to_ref(branch_name=pull_request.base_branch_name, commit_sha=pull_request.pr_head_sha)

    # TODO: Add job summary:
    #  https://docs.github.com/en/actions/writing-workflows/choosing-what-your-workflow-does/workflow-commands-for-github-actions#adding-a-job-summary
