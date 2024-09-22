import json
import http.client
import os
import urllib.parse
from argparse import ArgumentParser

from command import run_command
from schema import IssueCommentEvent, PullRequest, UserPermission

# https://github.com/sequoia-pgp/fast-forward/blob/main/.github/workflows/fast-forward.yml
# https://github.com/sequoia-pgp/fast-forward/blob/main/action.yml
# https://github.com/sequoia-pgp/fast-forward/blob/main/src/fast-forward.sh


GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]
GITHUB_ACTOR = os.environ["GITHUB_ACTOR"]  # Required? data["sender"]["login"]?
HEADERS = {
    "Accept": "application/vnd.github+json",
    "Authorization": f"Bearer {GITHUB_TOKEN}",
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
    print("Loading event...")
    with open(event_path, encoding="utf-8") as f:
        data: IssueCommentEvent = json.load(f)

    print("Getting pull request data...")
    response = request(connection, url=data["issue"]["pull_request"]["url"])
    if not response:
        print("Could not get pull request")
        return 1

    pull_request: PullRequest = json.loads(response)

    print("Cloning pull request repo...")
    clone_url = pull_request["base"]["repo"]["clone_url"]
    credentials = f"url={clone_url}\nusername={GITHUB_ACTOR}\npassword={GITHUB_TOKEN}"

    print("Setting git credential helper to store...")
    result = run_command("git config --global credential.helper store")
    if result.exit_code != 0:
        print(f"Could not set git credential helper to store. Error: {result.err}")
        return 1

    print("Approving git credentials...")
    result = run_command(f'echo -e "{credentials}" | git credential approve')
    if result.exit_code != 0:
        print(f"Could not approve git credentials. Error: {result.err}")
        return 1

    base_ref = pull_request["base"]["ref"]
    pr_ref = pull_request["head"]["ref"]
    pr_sha = pull_request["head"]["sha"]

    print(f"Base Ref: {base_ref}")
    print(f"Original Base Ref: {pull_request['base']['sha']}")
    print(f"PR Ref: {pr_ref}")
    print(f"PR SHA: {pr_sha}")

    # 'pull_request["base"]["sha"]' is from the time when the PR was created.
    # See. https://github.com/orgs/community/discussions/59677
    # Therefore, we need to clone the repo to get the SHA.

    clone_path = "./clone"

    print("Configuring clone url...")  # TODO: Check is necessary?
    clone_url_parts = urllib.parse.urlparse(clone_url)._asdict()
    clone_url_parts["netloc"] = f"{GITHUB_ACTOR}@{clone_url_parts['netloc']}"
    auth_clone_url = urllib.parse.urlunparse(clone_url_parts.values())

    print(f"Cloning {clone_url}:{base_ref} to {clone_path}...")
    result = run_command(f"git clone --quiet --single-branch --branch {base_ref} {auth_clone_url} {clone_path}")
    if result.exit_code != 0:
        print(f"Could not clone base ref. Error: {result.err}")
        return 1

    print(f"Fetching {clone_url}:{pr_ref} to {clone_path}...")
    result = run_command(f"git fetch --quiet {auth_clone_url} {pr_ref}", directory=clone_path)
    if result.exit_code != 0:
        print(f"Could not fetch pull request ref. Error: {result.err}")
        return 1

    print(f"Add '{pr_sha}' to a new branch '{pr_ref}', removing it from a detached state...")
    result = run_command(f"git branch -f {pr_ref} {pr_sha}", directory=clone_path)
    if result.exit_code != 0:
        print(f"Could not add commit to branch. Error: {result.err}")
        return 1

    print("Finding base ref...")
    result = run_command(f"git rev-parse origin/{base_ref}", directory=clone_path)
    if result.err is not None:
        print(f"Could not find base ref. Error: {result.err}")
        return 1

    base_sha = result.out

    print(f"Current Base SHA: {base_sha}")

    print("Checking if can fast forward...")
    result = run_command(f"git merge-base --is-ancestor {base_sha} {pr_sha}", directory=clone_path)
    if result.exit_code != 0:
        print(f"Cannot fast forward base {base_sha[:7]} to head {pr_sha[:7]}. Error: {result.err}")
        return 1

    print("Formatting permissions url...")
    username = data["sender"]["login"]
    collaborators_url = data["repository"]["collaborators_url"].format(**{"/collaborator": f"/{username}"})
    permissions_url = f"{collaborators_url}/permission"

    print("Checking permissions for pushing...")
    response = request(connection, url=permissions_url)
    if not response:
        print("Could not get user permissions")
        return 1

    permissions: UserPermission = json.loads(response)

    print(f"Permissions: {permissions}")

    if permissions["permission"]["pull"] is False:
        print(f"User '{username}' does not have permissions for merging.")
        return 1

    print("Fast-forwarding...")

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
