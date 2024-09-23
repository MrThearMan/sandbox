import json
import re
from dataclasses import dataclass
from typing import Any, Self
from unittest.mock import Mock, patch

import pytest

from prff.exception import PullRequestFastForwardError
from prff.github_api import (
    HttpResponse,
    add_rocket_reaction,
    fetch_pull_request,
    fetch_user_permissions,
    get_request,
    post_error_comment,
    post_request,
    validate_push_permissions,
)
from prff.github_schema import Permission, UserPermission, UserWithPermission


@dataclass
class MockResponse:
    content: bytes
    status: int

    def read(self) -> bytes:
        return self.content


class MockConnection:
    def __init__(self, content: Any, status: int = 200) -> None:
        self.content = json.dumps(content).encode()
        self.status = status
        self.patch = patch("prff.github_api.HTTPSConnection", return_value=self)
        self.mock: Mock | None = None
        self.method: str | None = None
        self.url: str | None = None
        self.headers: str | None = None
        self.body: str | None = None

    def __call__(self, netloc: str):
        return self

    def request(
        self,
        method: str | None = None,
        url: str | None = None,
        headers: dict[str, Any] | None = None,
        body: str | None = None,
    ) -> None:
        self.method = method
        self.url = url
        self.headers = headers
        self.body = body

    def getresponse(self) -> MockResponse:
        return MockResponse(content=self.content, status=self.status)

    def close(self) -> None: ...

    def __enter__(self) -> Self:
        self.mock = self.patch.start()
        return self

    def __exit__(self, *args: object, **kwargs: Any) -> None:
        self.patch.stop()


def test_get_request():
    with MockConnection(content={"foo": 1}) as connection:
        response = get_request(url="https://github.com/MrThearMan/sandbox")

    assert response.status == 200
    assert response.data == {"foo": 1}

    assert connection.mock.call_args.args == ("github.com",)
    assert connection.mock.call_args.kwargs == {}

    assert connection.method == "GET"
    assert connection.url == "/MrThearMan/sandbox"
    assert connection.headers == {
        "Accept": "application/vnd.github+json",
        "Authorization": "Bearer TOKEN",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "MrThearMan-GitHub-Fast-Forward-Action",
    }


def test_get_request__cannot_decode_json():
    connection = MockConnection(content="foo")
    connection.content = b""

    msg = "Could not decode JSON response: Expecting value: line 1 column 1 (char 0)."

    with connection, pytest.raises(PullRequestFastForwardError, match=re.escape(msg)):
        get_request(url="https://github.com/MrThearMan/sandbox")


def test_get_request__cannot_decode_json__content():
    connection = MockConnection(content="foo")
    connection.content = b"2c25c"

    msg = "Could not decode JSON response: Extra data: line 1 column 2 (char 1). Content: '2c25c'"

    with connection, pytest.raises(PullRequestFastForwardError, match=re.escape(msg)):
        get_request(url="https://github.com/MrThearMan/sandbox")


def test_post_request():
    with MockConnection(content={"foo": 1}) as connection:
        response = post_request(url="https://github.com/MrThearMan/sandbox", data={"fizz": "buzz"})

    assert response.status == 200
    assert response.data == {"foo": 1}

    assert connection.mock.call_args.args == ("github.com",)
    assert connection.mock.call_args.kwargs == {}

    assert connection.method == "POST"
    assert connection.url == "/MrThearMan/sandbox"
    assert connection.headers == {
        "Accept": "application/vnd.github+json",
        "Content-Type": "application/json",
        "Authorization": "Bearer TOKEN",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "MrThearMan-GitHub-Fast-Forward-Action",
    }
    assert connection.body == '{"fizz":"buzz"}'


def test_post_request__cannot_decode_json():
    connection = MockConnection(content="foo")
    connection.content = b""

    msg = "Could not decode JSON response: Expecting value: line 1 column 1 (char 0)."

    with connection, pytest.raises(PullRequestFastForwardError, match=re.escape(msg)):
        post_request(url="https://github.com/MrThearMan/sandbox", data={"fizz": "buzz"})


def test_post_request__cannot_decode_json__content():
    connection = MockConnection(content="foo")
    connection.content = b"2c25c"

    msg = "Could not decode JSON response: Extra data: line 1 column 2 (char 1). Content: '2c25c'"

    with connection, pytest.raises(PullRequestFastForwardError, match=re.escape(msg)):
        post_request(url="https://github.com/MrThearMan/sandbox", data={"fizz": "buzz"})


def test_fetch_pull_request(caplog):
    path = "prff.github_api.get_request"
    response = HttpResponse(status=200, data={"foo": 1})

    with patch(path, return_value=response):
        pr = fetch_pull_request(url="https://github.com/MrThearMan/sandbox")

    assert pr == {"foo": 1}

    assert caplog.messages == [
        "Fetching pull request data from GitHub...",
        "Pull request data received.",
    ]


def test_fetch_pull_request__failed():
    path = "prff.github_api.get_request"
    response = HttpResponse(status=400, data={"error": "message"})

    msg = "[`400`] Could not get pull request: {'error': 'message'}"
    with patch(path, return_value=response), pytest.raises(PullRequestFastForwardError, match=re.escape(msg)):
        fetch_pull_request(url="https://github.com/MrThearMan/sandbox")


def test_fetch_user_permissions(caplog):
    path = "prff.github_api.get_request"
    response = HttpResponse(status=200, data={"foo": 1})

    with patch(path, return_value=response):
        pr = fetch_user_permissions(url="https://github.com/MrThearMan/sandbox")

    assert pr == {"foo": 1}

    assert caplog.messages == [
        "Fetching user permissions...",
        "Permissions received.",
    ]


def test_fetch_user_permissions__failed():
    path = "prff.github_api.get_request"
    response = HttpResponse(status=400, data={"error": "message"})

    msg = "[`400`] Could not fetch permissions: {'error': 'message'}"
    with patch(path, return_value=response), pytest.raises(PullRequestFastForwardError, match=re.escape(msg)):
        fetch_user_permissions(url="https://github.com/MrThearMan/sandbox")


def test_validate_push_permissions__has_permissions(caplog):
    permissions = UserPermission(
        user=UserWithPermission(
            login="test_user",
            permissions=Permission(
                push=True,
            ),
        ),
    )
    validate_push_permissions(permissions=permissions)

    assert caplog.messages == [
        "Checking if user `test_user` has permissions for pushing to this repo...",
        "User `test_user` has the required permissions.",
    ]


def test_validate_push_permissions__missing_permissions():
    permissions = UserPermission(
        user=UserWithPermission(
            login="test_user",
            permissions=Permission(
                push=False,
            ),
        ),
    )
    msg = "User `test_user` does not have required permissions."
    with pytest.raises(PullRequestFastForwardError, match=re.escape(msg)):
        validate_push_permissions(permissions=permissions)


def test_post_error_comment(caplog):
    path = "prff.github_api.post_request"
    response = HttpResponse(status=200, data={"foo": 1})

    with patch(path, return_value=response) as mock:
        post_error_comment(error="error", comments_url="https://api.github.com/repos/MrThearMan/main/issues/1/comments")

    assert mock.call_args.kwargs == {
        "url": "https://api.github.com/repos/MrThearMan/main/issues/1/comments",
        "data": {
            "body": "Failed to fast-forward the pull request:\n\n> error",
        },
    }

    assert caplog.messages == [
        "Adding a comment to issue about error...",
        "Comment added.",
    ]


def test_post_error_comment__failed(caplog):
    path = "prff.github_api.post_request"
    response = HttpResponse(status=400, data={"foo": 1})

    with patch(path, return_value=response):
        post_error_comment(error="error", comments_url="https://api.github.com/repos/MrThearMan/main/issues/1/comments")

    assert caplog.messages == [
        "Adding a comment to issue about error...",
        "[`400`] Could not post comment to pull request: {'foo': 1}",
    ]


def test_add_rocket_reaction(caplog):
    path = "prff.github_api.post_request"
    response = HttpResponse(status=200, data={"foo": 1})

    with patch(path, return_value=response) as mock:
        add_rocket_reaction(reactions_url="https://api.github.com/repos/MrThearMan/main/issues/comments/1/reactions")

    assert mock.call_args.kwargs == {
        "url": "https://api.github.com/repos/MrThearMan/main/issues/comments/1/reactions",
        "data": {
            "content": "rocket",
        },
    }

    assert caplog.messages == [
        "Adding a rocker reaction to comment to indicate successful merge...",
        "Reaction added.",
    ]


def test_add_rocket_reaction__failed(caplog):
    path = "prff.github_api.post_request"
    response = HttpResponse(status=400, data={"foo": 1})

    with patch(path, return_value=response) as mock:
        add_rocket_reaction(reactions_url="https://api.github.com/repos/MrThearMan/main/issues/comments/1/reactions")

    assert caplog.messages == [
        "Adding a rocker reaction to comment to indicate successful merge...",
        "[`400`] Could not add rocket reaction to comment: {'foo': 1}",
    ]
