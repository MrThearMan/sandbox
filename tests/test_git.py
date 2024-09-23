import re
from unittest.mock import patch

import pytest

from prff.command import CommandResult
from prff.exception import PullRequestFastForwardError
from prff.git import clone_repo_at_branch, create_branch, fetch_commit, push_branch_to_commit, validate_fast_forward


def test_clone_repo_at_branch(caplog):
    path = "prff.git.run_command"
    result = CommandResult(out="", err=None, exit_code=0)

    with patch(path, return_value=result) as mock:
        clone_repo_at_branch(repo_url="https://github.com/MrThearMan/sandbox.git", branch_name="main")

    assert mock.call_args.args == (
        "git clone --quiet --single-branch --branch main https://github.com/MrThearMan/sandbox.git ./clone",
    )
    assert mock.call_args.kwargs == {}

    assert caplog.messages == [
        "Cloning repo `https://github.com/MrThearMan/sandbox.git` at branch `main`...",
        "Repo cloned.",
    ]


def test_clone_repo_at_branch__error():
    path = "prff.git.run_command"
    result = CommandResult(out=None, err="foo", exit_code=1)

    msg = "Could not clone branch `main`. Error: foo"
    with patch(path, return_value=result), pytest.raises(PullRequestFastForwardError, match=re.escape(msg)):
        clone_repo_at_branch(repo_url="https://github.com/MrThearMan/sandbox.git", branch_name="main")


def test_fetch_commit(caplog):
    path = "prff.git.run_command"
    result = CommandResult(out="", err=None, exit_code=0)

    with patch(path, return_value=result) as mock:
        fetch_commit(
            repo_url="https://github.com/MrThearMan/sandbox.git",
            commit_sha="485ef4d105874bf076684ef1c30b2a7e93d3aa46",
        )

    assert mock.call_args.args == (
        "git fetch --quiet https://github.com/MrThearMan/sandbox.git 485ef4d105874bf076684ef1c30b2a7e93d3aa46",
    )
    assert mock.call_args.kwargs == {"directory": "./clone"}

    assert caplog.messages == [
        "Fetching commit `485ef4d` from repo `https://github.com/MrThearMan/sandbox.git`...",
        "Commit fetched.",
    ]


def test_fetch_commit__error():
    path = "prff.git.run_command"
    result = CommandResult(out=None, err="foo", exit_code=1)

    msg = "Could not fetch commit `485ef4d`. Error: foo"
    with patch(path, return_value=result), pytest.raises(PullRequestFastForwardError, match=re.escape(msg)):
        fetch_commit(
            repo_url="https://github.com/MrThearMan/sandbox.git",
            commit_sha="485ef4d105874bf076684ef1c30b2a7e93d3aa46",
        )


def test_create_branch(caplog):
    path = "prff.git.run_command"
    result = CommandResult(out="", err=None, exit_code=0)

    with patch(path, return_value=result) as mock:
        create_branch(
            branch_name="main",
            commit_sha="485ef4d105874bf076684ef1c30b2a7e93d3aa46",
        )

    assert mock.call_args.args == ("git branch -f main 485ef4d105874bf076684ef1c30b2a7e93d3aa46",)
    assert mock.call_args.kwargs == {"directory": "./clone"}

    assert caplog.messages == [
        "Creating a new branch `main` at `485ef4d`...",
        "Branch created.",
    ]


def test_create_branch__error():
    path = "prff.git.run_command"
    result = CommandResult(out=None, err="foo", exit_code=1)

    msg = "Could not create branch at commit `485ef4d`. Error: foo"
    with patch(path, return_value=result), pytest.raises(PullRequestFastForwardError, match=re.escape(msg)):
        create_branch(
            branch_name="main",
            commit_sha="485ef4d105874bf076684ef1c30b2a7e93d3aa46",
        )


def test_validate_fast_forward(caplog):
    path = "prff.git.run_command"
    result = CommandResult(out="", err=None, exit_code=0)

    with patch(path, return_value=result) as mock:
        validate_fast_forward(
            base_sha="924b13bfb8b631450378e39c2f89d55b1285ac9d",
            head_sha="485ef4d105874bf076684ef1c30b2a7e93d3aa46",
        )

    assert mock.call_args.args == (
        (
            "git merge-base --is-ancestor 924b13bfb8b631450378e39c2f89d55b1285ac9d "
            "485ef4d105874bf076684ef1c30b2a7e93d3aa46"
        ),
    )
    assert mock.call_args.kwargs == {"directory": "./clone"}

    assert caplog.messages == [
        "Checking if `924b13b` can be fast-forwarded to `485ef4d`...",
        "Fast-forwarding is possible.",
    ]


def test_validate_fast_forward__failed():
    path = "prff.git.run_command"
    result = CommandResult(out=None, err="foo", exit_code=1)

    msg = "Cannot fast-forward `924b13b` to `485ef4d`. Error: foo"
    with patch(path, return_value=result), pytest.raises(PullRequestFastForwardError, match=re.escape(msg)):
        validate_fast_forward(
            base_sha="924b13bfb8b631450378e39c2f89d55b1285ac9d",
            head_sha="485ef4d105874bf076684ef1c30b2a7e93d3aa46",
        )


def test_push_branch_to_commit(caplog):
    path = "prff.git.run_command"
    result = CommandResult(out="", err=None, exit_code=0)

    with patch(path, return_value=result) as mock:
        push_branch_to_commit(
            branch_name="main",
            commit_sha="485ef4d105874bf076684ef1c30b2a7e93d3aa46",
        )

    assert mock.call_args.args == ("git push origin 485ef4d105874bf076684ef1c30b2a7e93d3aa46:main",)
    assert mock.call_args.kwargs == {"directory": "./clone"}

    assert caplog.messages == [
        "Pushing `main` to `485ef4d`...",
        "Push successful.",
    ]


def test_push_branch_to_commit__failed(caplog):
    path = "prff.git.run_command"
    result = CommandResult(out=None, err="foo", exit_code=1)

    msg = "Could not push `main` to `485ef4d`. Error: foo"
    with patch(path, return_value=result), pytest.raises(PullRequestFastForwardError, match=re.escape(msg)):
        push_branch_to_commit(
            branch_name="main",
            commit_sha="485ef4d105874bf076684ef1c30b2a7e93d3aa46",
        )
