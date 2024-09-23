from __future__ import annotations

from prff.git import clone_repo_at_branch, create_branch, fetch_commit, push_branch_to_commit, validate_fast_forward
from prff.github_api import fetch_user_permissions, post_error_comment, validate_push_permissions
from prff.pull_request import PullRequestData

__all__ = [
    "fast_forward_pull_request",
]


def fast_forward_pull_request(*, pull_request_url: str, permissions_url: str) -> None:
    pull_request = PullRequestData.from_github(url=pull_request_url)

    try:
        permissions = fetch_user_permissions(url=permissions_url)
        validate_push_permissions(permissions=permissions)

        clone_repo_at_branch(repo_url=pull_request.base_clone_url, branch_name=pull_request.base_branch_name)
        fetch_commit(repo_url=pull_request.pr_clone_url, commit_sha=pull_request.pr_head_sha)
        create_branch(branch_name=pull_request.pr_branch_name, commit_sha=pull_request.pr_head_sha)
        pull_request.fix_base_sha()

        validate_fast_forward(base_sha=pull_request.base_head_sha, head_sha=pull_request.pr_head_sha)
        push_branch_to_commit(branch_name=pull_request.base_branch_name, commit_sha=pull_request.pr_head_sha)

        # TODO: Trigger another workflow after merging:
        #  https://docs.github.com/en/actions/writing-workflows/choosing-when-your-workflow-runs/events-that-trigger-workflows#repository_dispatch

    except Exception as error:
        post_error_comment(error=str(error), comments_url=pull_request.comments_url)
        raise
