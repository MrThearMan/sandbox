#!/usr/bin/env python
from argparse import ArgumentParser

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

        fast_forward_pull_request(pull_request_url=pull_request_url, permissions_url=permissions_url)

    except RuntimeError as error:
        logger.error(error)
        raise SystemExit(1) from error

    except Exception as error:
        logger.exception(error)
        raise SystemExit(1) from error

    raise SystemExit(0)
