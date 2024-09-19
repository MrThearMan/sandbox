import json
import http.client
import os
import urllib.parse
from argparse import ArgumentParser
from contextlib import closing

from command import run_command, get_exit_code
from schema import IssueCommentEvent, Permission, PullRequest, UserPermission

# https://github.com/sequoia-pgp/fast-forward/blob/main/.github/workflows/fast-forward.yml
# https://github.com/sequoia-pgp/fast-forward/blob/main/action.yml
# https://github.com/sequoia-pgp/fast-forward/blob/main/src/fast-forward.sh

HEADERS = {
    "Accept": "application/vnd.github+json",
    "Authorization": f"Bearer {os.environ['GITHUB_TOKEN']}",
    "X-GitHub-Api-Version": "2022-11-28",
    "User-Agent": "MrThearMan-GitHub-Fast-Forward-Action",
}


def request(connection: http.client.HTTPSConnection, *, url: str) -> str | None:
    path = urllib.parse.urlparse(url).path
    connection.request("GET", url=path, headers=HEADERS)
    response = connection.getresponse()
    content = response.read().decode()

    if response.status != 200:
        print(f"Unexpected status code: {response.status}: {content}")
        return None

    return content


def main(*, event_path: str, connection: http.client.HTTPSConnection) -> int:
    with open(event_path, encoding="utf-8") as f:
        data: IssueCommentEvent = json.load(f)

    response = request(connection, url=data["issue"]["pull_request"]["url"])
    if not response:
        print("Could not get pull request")
        return 1

    pull_request: PullRequest = json.loads(response)

    base_ref = pull_request["base"]["ref"]

    # 'pull_request["base"]["sha"]' is from the time when the PR was created.
    # See. https://github.com/orgs/community/discussions/59677
    base_sha = run_command(f"git rev-parse origin/{base_ref}")
    if base_sha is None:
        print("Could not find base ref")
        return 1

    print(f"Base ref: {base_ref}")
    print(f"Base SHA: {base_sha}")

    head_ref = pull_request["head"]["ref"]
    head_sha = pull_request["head"]["sha"]

    print(f"Head ref: {head_ref}")
    print(f"Head SHA: {head_sha}")

    can_fast_forward = get_exit_code(f"git merge-base --is-ancestor {base_sha} {head_sha}")
    if can_fast_forward != 0:
        print(f"Cannot fast forward base {base_sha} to head {head_sha}")
        return 1

    # Check permissions
    sender = data["sender"]["login"]
    collaborators_url = data["repository"]["collaborators_url"].format(**{"/collaborator": f"/{sender}"})

    permissions_url = f"{collaborators_url}/permission"

    response = request(connection, url=permissions_url)
    if not response:
        print("Could not get pull request")
        return 1

    permissions: UserPermission = json.loads(response)

    print(f"Permissions: {permissions}")

    if permissions["permission"]["pull"] is False:
        print(f"User {sender} does not have permissions for merging.")
        return 1

    return 0


if __name__ == "__main__":
    argparser = ArgumentParser()
    argparser.add_argument("--event-path", type=str, required=True)
    args = argparser.parse_args()

    connection = http.client.HTTPSConnection("api.github.com")

    try:
        return_value = main(event_path=args.event_path, connection=connection)
    finally:
        connection.close()

    raise SystemExit(return_value)

