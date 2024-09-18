import json
from argparse import ArgumentParser
from typing import Any


def main(*, github_token: str, event_path: str) -> int:
    print("Hello, world!")

    print(f"github_token len", f"{len(github_token)}")

    with open(event_path, encoding="utf-8") as f:
        data: dict[str, Any] = json.load(f)

    print("Data", data)

    return 0


if __name__ == "__main__":
    argparser = ArgumentParser()
    argparser.add_argument("--github-token", type=str, required=True)
    argparser.add_argument("--event-path", type=str, required=True)
    args = argparser.parse_args()

    raise SystemExit(main(**vars(args)))
