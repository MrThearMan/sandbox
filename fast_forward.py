import json
import http.client
import os
import urllib.parse
from argparse import ArgumentParser
from contextlib import closing

from schema import IssueCommentEvent


# https://github.com/sequoia-pgp/fast-forward/blob/main/.github/workflows/fast-forward.yml
# https://github.com/sequoia-pgp/fast-forward/blob/main/action.yml
# https://github.com/sequoia-pgp/fast-forward/blob/main/src/fast-forward.sh


def main(*, github_token: str, event_path: str) -> int:
    print("github_token:", github_token)
    print("event_path:", event_path)

    with open(event_path, encoding="utf-8") as f:
        data: IssueCommentEvent = json.load(f)

    pull_request_url = data["issue"]["pull_request"]["url"]
    url_parts = urllib.parse.urlparse(pull_request_url)

    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {github_token}",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    connection = http.client.HTTPSConnection(url_parts.netloc)

    with closing(connection):
        connection.request("GET", url=url_parts.path, headers=headers)
        response = connection.getresponse()
        content = response.read().decode()

        print("PR:", content)

        if response.status != 200:
            raise RuntimeError(f"Unexpected status code: {response.status}: {content}")

    return 0


if __name__ == "__main__":
    argparser = ArgumentParser()
    argparser.add_argument("--github-token", type=str, default=os.environ["GITHUB_TOKEN"])
    argparser.add_argument("--event-path", type=str, required=True)
    args = argparser.parse_args()

    raise SystemExit(main(github_token=args.github_token, event_path=args.event_path))

