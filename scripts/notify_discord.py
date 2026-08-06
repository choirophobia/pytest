"""Posts a pytest run's results to Discord via webhook.

Reads the JSON report produced by pytest-json-report (see
`.github/workflows/nightly-tests.yml`) and sends a summary embed,
clearly flagged as coming from pytest, to the webhook URL in
DISCORD_WEBHOOK_URL.
"""
import json
import os
import sys
from datetime import datetime, timezone

import requests

COLOR_PASS = 0x2ECC71
COLOR_FAIL = 0xE74C3C

MAX_FAILURES_LISTED = 10
DISCORD_FIELD_VALUE_LIMIT = 1024


def load_summary(report_path):
    with open(report_path) as f:
        report = json.load(f)

    summary = report.get("summary", {})
    summary["duration"] = report.get("duration", 0.0)
    tests = report.get("tests", [])
    failures = [t for t in tests if t.get("outcome") in ("failed", "error")]
    return summary, failures


def format_failures(failures):
    if not failures:
        return None

    lines = []
    for test in failures[:MAX_FAILURES_LISTED]:
        node_id = test.get("nodeid", "<unknown test>")
        lines.append(f"❌ `{node_id}`")

    remaining = len(failures) - MAX_FAILURES_LISTED
    if remaining > 0:
        lines.append(f"...and {remaining} more")

    value = "\n".join(lines)
    return value[:DISCORD_FIELD_VALUE_LIMIT]


def build_payload(summary, failures):
    passed = summary.get("passed", 0)
    failed = summary.get("failed", 0)
    errors = summary.get("error", 0)
    skipped = summary.get("skipped", 0)
    total = summary.get("total", passed + failed + errors + skipped)
    duration = summary.get("duration", 0.0)

    all_green = failed == 0 and errors == 0
    status_line = "✅ All tests passed" if all_green else "❌ Failures detected"

    repo = os.environ.get("GITHUB_REPOSITORY", "unknown/repo")
    run_id = os.environ.get("GITHUB_RUN_ID", "")
    run_number = os.environ.get("GITHUB_RUN_NUMBER", "?")
    server_url = os.environ.get("GITHUB_SERVER_URL", "https://github.com")
    run_url = f"{server_url}/{repo}/actions/runs/{run_id}" if run_id else None

    fields = [
        {"name": "Passed", "value": str(passed), "inline": True},
        {"name": "Failed", "value": str(failed), "inline": True},
        {"name": "Errors", "value": str(errors), "inline": True},
        {"name": "Skipped", "value": str(skipped), "inline": True},
        {"name": "Total", "value": str(total), "inline": True},
        {"name": "Duration", "value": f"{duration:.2f}s", "inline": True},
    ]

    failures_text = format_failures(failures)
    if failures_text:
        fields.append({"name": "Failed tests", "value": failures_text, "inline": False})

    embed = {
        "title": "DummyJSON API Suite — Nightly Run",
        "description": status_line,
        "color": COLOR_PASS if all_green else COLOR_FAIL,
        "fields": fields,
        "footer": {"text": f"Source: pytest  •  {repo}  •  run #{run_number}"},
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    if run_url:
        embed["url"] = run_url

    return {"username": "pytest", "embeds": [embed]}


def main():
    report_path = sys.argv[1] if len(sys.argv) > 1 else "report.json"
    webhook_url = os.environ.get("DISCORD_WEBHOOK_URL")

    if not webhook_url:
        print("DISCORD_WEBHOOK_URL is not set - skipping Discord notification.", file=sys.stderr)
        sys.exit(1)

    summary, failures = load_summary(report_path)
    payload = build_payload(summary, failures)

    response = requests.post(webhook_url, json=payload, timeout=15)
    response.raise_for_status()
    print(f"Discord notification sent ({response.status_code}).")


if __name__ == "__main__":
    main()
