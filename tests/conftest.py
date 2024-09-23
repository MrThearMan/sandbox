import os

os.environ["GITHUB_TOKEN"] = "TOKEN"  # noqa: S105
os.environ["GITHUB_ACTOR"] = "ACTOR"
os.environ["GITHUB_STEP_SUMMARY"] = "./tests/summary.txt"
os.environ["GITHUB_EVENT_PATH"] = "./tests/fixtures/comment_created.json"
