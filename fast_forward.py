import logging
from argparse import ArgumentParser
from pathlib import Path

logger = logging.getLogger(__name__)


def main(*, github_token: str, event_path: str) -> int:
    print("Hello, world!")

    logger.error(f"github_token: {github_token}")
    logger.error(f"event_path: {event_path}")

    text = Path(event_path).read_text()
    print(text)

    return 0


if __name__ == "__main__":
    argparser = ArgumentParser()
    argparser.add_argument("--github-token", type=str, required=True)
    argparser.add_argument("--event-path", type=str, required=True)
    args = argparser.parse_args()

    raise SystemExit(main(**vars(args)))
