#!/usr/bin/env python

import os
from argparse import ArgumentParser

from prff.exception import PullRequestFastForwardError
from prff.fast_forward import fast_forward_pull_request
from prff.github_event import load_urls_from_event
from prff.logging import SUMMARY, logger

if __name__ == "__main__":
    argparser = ArgumentParser()
    argparser.add_argument("--log-level", type=str, default="INFO")
    args = argparser.parse_args()

    exit_code: int = 0
    logger.setLevel(args.log_level.upper())

    try:
        pull_request_url, permissions_url = load_urls_from_event()
        fast_forward_pull_request(pull_request_url=pull_request_url, permissions_url=permissions_url)

    except PullRequestFastForwardError as error:
        logger.error(error)
        exit_code = 1

    except Exception as error:  # noqa: BLE001
        logger.exception("An unexpected error occurred", exc_info=error)
        exit_code = 1

    finally:
        # Add job summary for the GitHub Actions run
        SUMMARY.seek(0)
        os.environ["GITHUB_STEP_SUMMARY"] = str(SUMMARY.read())

    raise SystemExit(exit_code)
