#!/usr/bin/env python

from prff.exception import PullRequestFastForwardError
from prff.fast_forward import fast_forward_pull_request
from prff.github_actions import load_event_data, write_job_summary
from prff.github_api import add_rocket_reaction
from prff.logging import logger

if __name__ == "__main__":
    exit_code: int = 0

    try:
        event_data = load_event_data()
        fast_forward_pull_request(
            pull_request_url=event_data.pull_request_url,
            permissions_url=event_data.permissions_url,
        )

    except PullRequestFastForwardError as error:
        logger.error(error)
        exit_code = 1

    except Exception as error:  # noqa: BLE001
        logger.exception("An unexpected error occurred", exc_info=error)
        exit_code = 1

    else:
        add_rocket_reaction(reactions_url=event_data.reactions_url)

    finally:
        write_job_summary()

    raise SystemExit(exit_code)
