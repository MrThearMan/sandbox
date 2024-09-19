import json
from argparse import ArgumentParser
from typing import TypeGuard

from schema import Event, PullRequestCommentEvent, PullRequestEvent


# https://github.com/sequoia-pgp/fast-forward/blob/main/.github/workflows/fast-forward.yml
# https://github.com/sequoia-pgp/fast-forward/blob/main/action.yml
# https://github.com/sequoia-pgp/fast-forward/blob/main/src/fast-forward.sh


def is_pr_created(data: Event) -> TypeGuard[PullRequestEvent]:
    return hasattr(data, "pull_request")


def is_pr_comment(data: Event) -> TypeGuard[PullRequestCommentEvent]:
    return hasattr(data, "issue")


def main(*, github_token: str, event_path: str) -> int:
    print(f"github_token len", f"{len(github_token)}")

    with open(event_path, encoding="utf-8") as f:
        data: Event = json.load(f)

    print(f"data: {data}")

    if is_pr_created(data):
        pr = data["pull_request"]
        print(f"base_re: {pr}")

    elif is_pr_comment(data):
        issue = data["issue"]
        print(f"issue: {issue}")

    return 0


if __name__ == "__main__":
    argparser = ArgumentParser()
    argparser.add_argument("--github-token", type=str, required=True)
    argparser.add_argument("--event-path", type=str, required=True)
    args = argparser.parse_args()

    raise SystemExit(main(**vars(args)))
