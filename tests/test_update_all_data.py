from __future__ import annotations

import argparse
import asyncio
import subprocess
import sys
from pathlib import Path

import pytest
from pytest import MonkeyPatch

import llm_comparison.update_all_data as updater


def test_default_paths_and_shared_options() -> None:
    args = updater.parse_args([])

    assert (
        args.artificial_analysis_url
        == updater.update_artificial_analysis.DEFAULT_URL
    )
    assert args.opencode_go_url == updater.update_opencode_go.DEFAULT_URL
    assert (
        args.artificial_analysis_csv
        == updater.update_artificial_analysis.DEFAULT_CSV
    )
    assert args.opencode_go_csv == updater.update_opencode_go.DEFAULT_CSV
    assert args.html == updater.update_artificial_analysis.DEFAULT_HTML
    assert args.template == updater.update_artificial_analysis.DEFAULT_TEMPLATE
    assert args.publish_script == updater.PROJECT_ROOT / "scripts/update-gh-pages.py"
    assert args.skip_publish is False


def make_args(tmp_path: Path, *, skip_publish: bool = False) -> argparse.Namespace:
    return argparse.Namespace(
        artificial_analysis_url="https://example.test/aa",
        opencode_go_url="https://example.test/go",
        artificial_analysis_csv=tmp_path / "results.csv",
        opencode_go_csv=tmp_path / "opencode_go.csv",
        html=tmp_path / "index.html",
        template=tmp_path / "template.py",
        uploaded_date=None,
        headed=True,
        timeout_ms=123,
        skip_publish=skip_publish,
        publish_script=tmp_path / "publish.py",
    )


def test_async_main_runs_aa_then_go_then_one_publish(
    tmp_path: Path, monkeypatch: MonkeyPatch
) -> None:
    calls: list[str] = []
    args = make_args(tmp_path)

    async def fake_aa(child: argparse.Namespace) -> None:
        assert vars(child) == {
            "url": args.artificial_analysis_url,
            "csv": args.artificial_analysis_csv,
            "html": args.html,
            "template": args.template,
            "uploaded_date": None,
            "headed": True,
            "timeout_ms": 123,
        }
        calls.append("aa")

    async def fake_go(child: argparse.Namespace) -> None:
        assert vars(child) == {
            "url": args.opencode_go_url,
            "csv": args.opencode_go_csv,
            "aa_csv": args.artificial_analysis_csv,
            "headed": True,
            "timeout_ms": 123,
        }
        calls.append("go")

    monkeypatch.setattr(updater.update_artificial_analysis, "async_main", fake_aa)
    monkeypatch.setattr(updater.update_opencode_go, "async_main", fake_go)
    monkeypatch.setattr(
        updater, "run_publish_script", lambda path: calls.append(f"publish:{path}")
    )

    asyncio.run(updater.async_main(args))

    assert calls == ["aa", "go", f"publish:{args.publish_script}"]


def test_skip_publish_still_runs_both_children(
    tmp_path: Path, monkeypatch: MonkeyPatch
) -> None:
    calls: list[str] = []

    async def fake_aa(child: argparse.Namespace) -> None:
        calls.append("aa")

    async def fake_go(child: argparse.Namespace) -> None:
        calls.append("go")

    monkeypatch.setattr(updater.update_artificial_analysis, "async_main", fake_aa)
    monkeypatch.setattr(updater.update_opencode_go, "async_main", fake_go)
    monkeypatch.setattr(
        updater, "run_publish_script", lambda path: calls.append("publish")
    )

    asyncio.run(updater.async_main(make_args(tmp_path, skip_publish=True)))

    assert calls == ["aa", "go"]


def test_aa_failure_skips_go_and_publish(
    tmp_path: Path, monkeypatch: MonkeyPatch
) -> None:
    calls: list[str] = []

    async def failed_aa(child: argparse.Namespace) -> None:
        calls.append("aa")
        raise RuntimeError("aa failed")

    async def fake_go(child: argparse.Namespace) -> None:
        calls.append("go")

    monkeypatch.setattr(updater.update_artificial_analysis, "async_main", failed_aa)
    monkeypatch.setattr(updater.update_opencode_go, "async_main", fake_go)
    monkeypatch.setattr(
        updater, "run_publish_script", lambda path: calls.append("publish")
    )

    with pytest.raises(RuntimeError, match="aa failed"):
        asyncio.run(updater.async_main(make_args(tmp_path)))

    assert calls == ["aa"]


def test_go_failure_skips_publish(tmp_path: Path, monkeypatch: MonkeyPatch) -> None:
    calls: list[str] = []

    async def fake_aa(child: argparse.Namespace) -> None:
        calls.append("aa")

    async def failed_go(child: argparse.Namespace) -> None:
        calls.append("go")
        raise RuntimeError("go failed")

    monkeypatch.setattr(updater.update_artificial_analysis, "async_main", fake_aa)
    monkeypatch.setattr(updater.update_opencode_go, "async_main", failed_go)
    monkeypatch.setattr(
        updater, "run_publish_script", lambda path: calls.append("publish")
    )

    with pytest.raises(RuntimeError, match="go failed"):
        asyncio.run(updater.async_main(make_args(tmp_path)))

    assert calls == ["aa", "go"]


def test_run_publish_script_resolves_relative_path_from_project_root(
    tmp_path: Path, monkeypatch: MonkeyPatch
) -> None:
    repo_root = tmp_path / "repo"
    calls: list[tuple[list[str], Path | None]] = []

    def fake_run(
        command: list[str],
        *,
        check: bool,
        encoding: str | None = None,
        capture_output: bool = False,
        cwd: Path | None = None,
    ) -> subprocess.CompletedProcess[str]:
        assert check is False
        assert encoding == "utf-8"
        assert capture_output is True
        calls.append((command, cwd))
        return subprocess.CompletedProcess(command, 0, stdout="", stderr="")

    monkeypatch.setattr(updater, "PROJECT_ROOT", repo_root)
    monkeypatch.setattr(subprocess, "run", fake_run)

    updater.run_publish_script(Path("scripts/update-gh-pages.py"))

    assert calls == [
        ([sys.executable, str(repo_root / "scripts/update-gh-pages.py")], repo_root),
    ]


def test_run_publish_script_preserves_failure_shape(
    tmp_path: Path, monkeypatch: MonkeyPatch
) -> None:
    result = subprocess.CompletedProcess(
        ["publish"], 1, stdout="ignored", stderr="line one\nline two\n"
    )
    monkeypatch.setattr(subprocess, "run", lambda *args, **kwargs: result)

    with pytest.raises(
        RuntimeError,
        match="GitHub Pages publishing failed: line one line two",
    ):
        updater.run_publish_script(tmp_path / "publish.py")
