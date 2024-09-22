import json
import http.client
import logging
import os
import urllib.parse
from argparse import ArgumentParser

from command import run_command
from schema import IssueCommentEvent, PullRequest, UserPermission

# https://github.com/sequoia-pgp/fast-forward/blob/main/.github/workflows/fast-forward.yml
# https://github.com/sequoia-pgp/fast-forward/blob/main/action.yml
# https://github.com/sequoia-pgp/fast-forward/blob/main/src/fast-forward.sh


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


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
        logger.error(f"Unexpected status code: {response.status}: {content}")
        return None

    return content


def main(*, event_path: str, connection: http.client.HTTPSConnection) -> int:
    logger.info(f"Loading github event from '{event_path}'...")

    with open(event_path, encoding="utf-8") as f:
        data: IssueCommentEvent = json.load(f)

    logger.info("Getting pull request data...")

    response = request(connection, url=data["issue"]["pull_request"]["url"])
    if not response:
        logger.error("Could not get pull request")
        return 1
    else:
        logger.info("Pull request data received.")

    pull_request: PullRequest = json.loads(response)

    clone_url = pull_request["base"]["repo"]["clone_url"]
    credentials = f"url={clone_url}\nusername={GITHUB_ACTOR}\npassword={GITHUB_TOKEN}"

    logger.info("Setting git credential helper to store...")

    result = run_command("git config --global credential.helper store")
    if result.exit_code != 0:
        logger.error(f"Could not set git credential helper to store. Error: {result.err}")
        return 1
    else:
        logger.info("Git credential helper set.")

    logger.info("Approving git credentials...")

    result = run_command(f'echo -e "{credentials}" | git credential approve')
    if result.exit_code != 0:
        logger.error(f"Could not approve git credentials. Error: {result.err}")
        return 1
    else:
        logger.info("Git credentials approved.")

    base_ref = pull_request["base"]["ref"]
    pr_ref = pull_request["head"]["ref"]
    pr_sha = pull_request["head"]["sha"]

    logger.info(f"Base Ref: {base_ref}")
    logger.info(f"Original Base Ref: {pull_request['base']['sha']}")
    logger.info(f"PR Ref: {pr_ref}")
    logger.info(f"PR SHA: {pr_sha}")

    # 'pull_request["base"]["sha"]' is from the time when the PR was created.
    # See. https://github.com/orgs/community/discussions/59677
    # Therefore, we need to clone the repo to get the SHA.

    clone_path = "./clone"

    logger.info("Configuring clone url...")  # TODO: Check is necessary?

    clone_url_parts = urllib.parse.urlparse(clone_url)._asdict()
    clone_url_parts["netloc"] = f"{GITHUB_ACTOR}@{clone_url_parts['netloc']}"
    auth_clone_url = urllib.parse.urlunparse(clone_url_parts.values())

    logger.info(f"Cloning {clone_url}:{base_ref} to {clone_path}...")

    result = run_command(f"git clone --quiet --single-branch --branch {base_ref} {auth_clone_url} {clone_path}")
    if result.exit_code != 0:
        logger.error(f"Could not clone base ref. Error: {result.err}")
        return 1
    else:
        logger.info("Base ref cloned.")

    logger.info(f"Fetching {clone_url}:{pr_ref} to {clone_path}...")

    result = run_command(f"git fetch --quiet {auth_clone_url} {pr_ref}", directory=clone_path)
    if result.exit_code != 0:
        logger.error(f"Could not fetch pull request ref. Error: {result.err}")
        return 1
    else:
        logger.info("Pull request ref fetched.")

    # Adding the commit to a branch removes it from a detached state
    logger.info(f"Add '{pr_sha}' to a new branch '{pr_ref}'...")

    result = run_command(f"git branch -f {pr_ref} {pr_sha}", directory=clone_path)
    if result.exit_code != 0:
        logger.error(f"Could not add commit to branch. Error: {result.err}")
        return 1
    else:
        logger.info("Commit added to branch.")

    logger.info("Finding base ref...")

    result = run_command(f"git rev-parse origin/{base_ref}", directory=clone_path)
    if result.err is not None:
        logger.error(f"Could not find base ref. Error: {result.err}")
        return 1
    else:
        logger.info("Base ref found.")

    base_sha = result.out

    logger.info(f"Current Base SHA: {base_sha}")

    logger.info("Checking if can fast forward...")
    result = run_command(f"git merge-base --is-ancestor {base_sha} {pr_sha}", directory=clone_path)
    if result.exit_code != 0:
        logger.error(f"Cannot fast forward base {base_sha[:7]} to head {pr_sha[:7]}. Error: {result.err}")
        return 1
    else:
        logger.info("Can fast forward.")

    logger.info("Formatting permissions url...")

    username = data["sender"]["login"]
    collaborators_url = data["repository"]["collaborators_url"].format(**{"/collaborator": f"/{username}"})
    permissions_url = f"{collaborators_url}/permission"

    logger.info("Fetching user permissions...")

    response = request(connection, url=permissions_url)
    if not response:
        logger.error(f"Could not get permissions for user {username}")
        return 1
    else:
        logger.info("Permissions received.")

    permissions: UserPermission = json.loads(response)

    logger.info("Checking permissions for pushing...")

    if permissions["user"]["permissions"]["push"] is False:
        logger.error(f"User '{username}' does not have permissions for merging.")
        return 1
    else:
        logger.info(f"User '{username}' has permissions for merging.")

    logger.info("Fast-forwarding...")

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
