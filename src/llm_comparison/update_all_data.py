from __future__ import annotations

import argparse
import asyncio
import subprocess
import sys
from collections.abc import Sequence
from datetime import date
from pathlib import Path

from . import update_artificial_analysis, update_opencode_go

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PUBLISH_SCRIPT = PROJECT_ROOT / "scripts/update-gh-pages.py"


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Update all source data and publish GitHub Pages."
    )
    parser.add_argument(
        "--artificial-analysis-url", default=update_artificial_analysis.DEFAULT_URL
    )
    parser.add_argument("--opencode-go-url", default=update_opencode_go.DEFAULT_URL)
    parser.add_argument(
        "--artificial-analysis-csv",
        default=update_artificial_analysis.DEFAULT_CSV,
        type=Path,
    )
    parser.add_argument(
        "--opencode-go-csv", default=update_opencode_go.DEFAULT_CSV, type=Path
    )
    parser.add_argument(
        "--html", default=update_artificial_analysis.DEFAULT_HTML, type=Path
    )
    parser.add_argument(
        "--template", default=update_artificial_analysis.DEFAULT_TEMPLATE, type=Path
    )
    parser.add_argument(
        "--uploaded-date",
        default=None,
        type=date.fromisoformat,
        help="Data upload date in YYYY-MM-DD format. Defaults to today.",
    )
    parser.add_argument("--headed", action="store_true")
    parser.add_argument("--timeout-ms", default=30_000, type=int)
    parser.add_argument(
        "--skip-publish",
        action="store_true",
        help="Update both local datasets without running scripts/update-gh-pages.py.",
    )
    parser.add_argument(
        "--publish-script",
        default=DEFAULT_PUBLISH_SCRIPT,
        type=Path,
        help="Path to the GitHub Pages update script, relative to the repository root.",
    )
    return parser.parse_args(argv)


def run_publish_script(script_path: Path) -> None:
    resolved_script = (
        script_path if script_path.is_absolute() else PROJECT_ROOT / script_path
    )
    publish_result = subprocess.run(
        [sys.executable, str(resolved_script)],
        cwd=PROJECT_ROOT,
        check=False,
        encoding="utf-8",
        capture_output=True,
    )
    if publish_result.returncode != 0:
        output = publish_result.stderr or publish_result.stdout
        detail = " ".join(output.splitlines()[-3:])
        message = "GitHub Pages publishing failed"
        if detail:
            message = f"{message}: {detail}"
        raise RuntimeError(message)


async def async_main(args: argparse.Namespace) -> None:
    artificial_analysis_args = argparse.Namespace(
        url=args.artificial_analysis_url,
        csv=args.artificial_analysis_csv,
        html=args.html,
        template=args.template,
        uploaded_date=args.uploaded_date,
        headed=args.headed,
        timeout_ms=args.timeout_ms,
    )
    await update_artificial_analysis.async_main(artificial_analysis_args)

    opencode_go_args = argparse.Namespace(
        url=args.opencode_go_url,
        csv=args.opencode_go_csv,
        aa_csv=args.artificial_analysis_csv,
        headed=args.headed,
        timeout_ms=args.timeout_ms,
    )
    await update_opencode_go.async_main(opencode_go_args)

    if not args.skip_publish:
        run_publish_script(args.publish_script)


def main() -> None:
    asyncio.run(async_main(parse_args()))


if __name__ == "__main__":
    main()
