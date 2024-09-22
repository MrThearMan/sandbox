#!/usr/bin/env python
from argparse import ArgumentParser

from prff.exception import PullRequestFastForwardError
from prff.fast_forward import fast_forward_pull_request
from prff.github_event import load_issue_comment_event
from prff.logging import logger

if __name__ == "__main__":
    argparser = ArgumentParser()
    argparser.add_argument("--event-path", type=str, required=True)
    argparser.add_argument("--log-level", type=str, default="INFO")
    args = argparser.parse_args()

    logger.setLevel(args.log_level.upper())

    try:
        event = load_issue_comment_event(path=args.event_path)

        pull_request_url = event["issue"]["pull_request"]["url"]

        username = event["sender"]["login"]
        collaborators_url = event["repository"]["collaborators_url"].format(**{"/collaborator": f"/{username}"})
        permissions_url = f"{collaborators_url}/permission"

    except Exception as error:
        logger.exception("Error loading required data from GitHub event", exc_info=error)
        raise SystemExit(1) from error

    try:
        fast_forward_pull_request(pull_request_url=pull_request_url, permissions_url=permissions_url)

    # TODO: Add comment to PR when job fails
    except PullRequestFastForwardError as error:
        logger.error(error)
        raise SystemExit(1) from error

    except Exception as error:
        logger.exception("An unexpected error occurred", exc_info=error)
        raise SystemExit(1) from error

    raise SystemExit(0)
