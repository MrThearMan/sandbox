import re
from unittest.mock import patch

import pytest

from prff.command import CommandResult
from prff.exception import PullRequestFastForwardError
from prff.github_schema import PullRequest, Ref, Repository
from prff.pull_request import PullRequestData


def test_pull_request_data__from_github(caplog):
    fetch_path = "prff.pull_request.fetch_pull_request"

    data = PullRequest(
        base=Ref(
            ref="main",
            sha="924b13bfb8b631450378e39c2f89d55b1285ac9d",
            repo=Repository(
                clone_url="https://github.com/MrThearMan/example.git",
            ),
        ),
        head=Ref(
            ref="branch",
            sha="485ef4d105874bf076684ef1c30b2a7e93d3aa46",
            repo=Repository(
                clone_url="https://github.com/MrThearMan/fork.git",
            ),
        ),
        comments_url="https://api.github.com/repos/MrThearMan/example/issues/11/comments",
    )

    with patch(fetch_path, return_value=data):
        pull_request = PullRequestData.from_github(url="foo")

    assert pull_request.base_clone_url == "https://ACTOR:TOKEN@github.com/MrThearMan/example.git"
    assert pull_request.base_branch_name == "main"
    assert pull_request.base_head_sha == "924b13bfb8b631450378e39c2f89d55b1285ac9d"

    assert pull_request.pr_clone_url == "https://ACTOR:TOKEN@github.com/MrThearMan/fork.git"
    assert pull_request.pr_branch_name == "branch"
    assert pull_request.pr_head_sha == "485ef4d105874bf076684ef1c30b2a7e93d3aa46"

    assert pull_request.comments_url == "https://api.github.com/repos/MrThearMan/example/issues/11/comments"

    assert caplog.messages == [
        "Parsing pull request data...",
        "Pull request data parsed.",
    ]


def test_pull_request_data__fix_base_sha(caplog):
    pull_request = PullRequestData(
        base_clone_url="https://ACTOR:TOKEN@github.com/MrThearMan/example.git",
        base_branch_name="main",
        base_head_sha="924b13bfb8b631450378e39c2f89d55b1285ac9d",
        pr_clone_url="https://ACTOR:TOKEN@github.com/MrThearMan/fork.git",
        pr_branch_name="branch",
        pr_head_sha="485ef4d105874bf076684ef1c30b2a7e93d3aa46",
        comments_url="https://api.github.com/repos/MrThearMan/example/issues/11/comments",
    )

    result = CommandResult(out="4480ac4f1dad3a5b6a044dd64f0c7c39486831cb", err=None, exit_code=0)

    with patch("prff.pull_request.run_command", return_value=result):
        pull_request.fix_base_sha()

    assert pull_request.base_head_sha == "4480ac4f1dad3a5b6a044dd64f0c7c39486831cb"

    assert caplog.messages == [
        "Parsing commit sha for `main`...",
        "Commit SHA parsed.",
    ]


def test_pull_request_data__fix_base_sha__error():
    pull_request = PullRequestData(
        base_clone_url="https://ACTOR:TOKEN@github.com/MrThearMan/example.git",
        base_branch_name="main",
        base_head_sha="924b13bfb8b631450378e39c2f89d55b1285ac9d",
        pr_clone_url="https://ACTOR:TOKEN@github.com/MrThearMan/fork.git",
        pr_branch_name="branch",
        pr_head_sha="485ef4d105874bf076684ef1c30b2a7e93d3aa46",
        comments_url="https://api.github.com/repos/MrThearMan/example/issues/11/comments",
    )

    result = CommandResult(out=None, err="foo", exit_code=1)

    msg = "Could not parse base sha. Error: foo"
    with (
        pytest.raises(PullRequestFastForwardError, match=re.escape(msg)),
        patch("prff.pull_request.run_command", return_value=result),
    ):
        pull_request.fix_base_sha()
