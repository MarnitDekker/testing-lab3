import argparse
import json
import subprocess
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", type=Path, default=Path("artifacts/bandit.json"))
    parser.add_argument("--fixture", type=Path)
    args = parser.parse_args()
    args.report.parent.mkdir(parents=True, exist_ok=True)

    if args.fixture:
        args.report.write_bytes(args.fixture.read_bytes())
        print("DEMO: synthetic Bandit report")
    else:
        result = subprocess.run(
            [sys.executable, "-m", "bandit", "-r", "shop", "-f", "json", "-o", str(args.report)],
            check=False,
        )
        if result.returncode not in (0, 1) or not args.report.is_file():
            return 2

    report = json.loads(args.report.read_text(encoding="utf-8"))
    if report["errors"]:
        print("Bandit scan errors")
        return 2
    findings = [entry for entry in report["results"] if entry["issue_severity"] == "HIGH"]
    for finding in findings:
        print(f"HIGH {finding['test_id']}: {finding['issue_text']}")
    print(f"Security gate: {len(findings)} HIGH findings")
    return int(bool(findings))


if __name__ == "__main__":
    sys.exit(main())
