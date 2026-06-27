from __future__ import annotations

import argparse
import shutil
import subprocess
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

DEFAULT_PAGES_BRANCH = "gh-pages"
DEFAULT_COMMIT_MESSAGE = "Update GitHub Pages site"
DEFAULT_SOURCE_COMMIT_MESSAGE = "Update generated analysis outputs"

GENERATED_FILES = (
    "src/llm_comparison/compare_models_template.py",
    "public/index.html",
    "data/results.csv",
)


@dataclass(frozen=True)
class PublicFile:
    source: str
    destination: str


PUBLIC_FILES = (
    PublicFile("public/index.html", "index.html"),
    PublicFile("data/results.csv", "results.csv"),
    PublicFile("src/llm_comparison/compare_models.py", "compare_models.py"),
    PublicFile("src/llm_comparison/compare_models_core.py", "compare_models_core.py"),
    PublicFile(
        "src/llm_comparison/compare_models_template.py",
        "compare_models_template.py",
    ),
    PublicFile("README.md", "README.md"),
    PublicFile(".gitignore", ".gitignore"),
)


class PublishError(RuntimeError):
    pass


def run_git(
    repo_root: Path,
    *args: str,
    capture: bool = False,
    check: bool = True,
) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        ["git", *args],
        cwd=repo_root,
        check=False,
        encoding="utf-8",
        stdout=subprocess.PIPE if capture else None,
        stderr=subprocess.PIPE if capture else None,
    )
    if check and result.returncode != 0:
        command = " ".join(("git", *args))
        message = f"{command} failed"
        if capture and result.stderr:
            message = f"{message}: {result.stderr.strip()}"
        raise PublishError(message)
    return result


def git_output(repo_root: Path, *args: str) -> str:
    return run_git(repo_root, *args, capture=True).stdout.strip()


def status_paths(status_lines: Sequence[str]) -> list[str]:
    paths: list[str] = []
    seen: set[str] = set()
    for line in status_lines:
        if not line:
            continue
        path = line[3:]
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        if path not in seen:
            paths.append(path)
            seen.add(path)
    return paths


def status_lines(repo_root: Path, *paths: str) -> list[str]:
    args = ["status", "--porcelain"]
    if paths:
        args.extend(("--", *paths))
    output = git_output(repo_root, *args)
    return output.splitlines() if output else []


def require_clean_or_commit_generated(
    repo_root: Path,
    generated_files: Sequence[str],
    source_commit_message: str,
) -> None:
    status = status_lines(repo_root)
    if status:
        dirty_paths = status_paths(status)
        generated = set(generated_files)
        unexpected_paths = [path for path in dirty_paths if path not in generated]
        if unexpected_paths:
            paths = ", ".join(unexpected_paths)
            raise PublishError(
                "Working tree has changes outside generated analysis files: "
                f"{paths}"
            )

        run_git(repo_root, "add", "--", *generated_files)
        if status_lines(repo_root, *generated_files):
            run_git(repo_root, "commit", "-m", source_commit_message)

    if status_lines(repo_root):
        raise PublishError("Working tree must be clean before publishing.")


def remove_worktree_contents(repo_root: Path) -> None:
    for path in repo_root.iterdir():
        if path.name == ".git":
            continue
        if path.is_dir():
            shutil.rmtree(path)
        else:
            path.unlink()


def publish_files(
    repo_root: Path,
    source_branch: str,
    public_files: Sequence[PublicFile],
) -> None:
    for public_file in public_files:
        run_git(repo_root, "checkout", source_branch, "--", public_file.source)

        source_path = repo_root / public_file.source
        destination_path = repo_root / public_file.destination
        destination_path.parent.mkdir(parents=True, exist_ok=True)
        if source_path != destination_path:
            source_path.replace(destination_path)

    for path_name in ("src", "public", "data"):
        publish_path = repo_root / path_name
        if publish_path.exists():
            shutil.rmtree(publish_path)


def publish(
    pages_branch: str = DEFAULT_PAGES_BRANCH,
    commit_message: str = DEFAULT_COMMIT_MESSAGE,
    source_commit_message: str = DEFAULT_SOURCE_COMMIT_MESSAGE,
    repo_root: Path | None = None,
) -> None:
    if repo_root is None:
        try:
            root_text = subprocess.check_output(
                ["git", "rev-parse", "--show-toplevel"],
                encoding="utf-8",
                stderr=subprocess.PIPE,
            ).strip()
        except subprocess.CalledProcessError as exc:
            raise PublishError("Run this script from inside a git repository.") from exc
        repo_root = Path(root_text)

    repo_root = repo_root.resolve()

    source_branch = git_output(repo_root, "branch", "--show-current")
    if not source_branch:
        raise PublishError("Could not determine the current source branch.")
    if source_branch == pages_branch:
        raise PublishError(
            f"Run this script from the source branch, not {pages_branch}."
        )

    require_clean_or_commit_generated(
        repo_root,
        GENERATED_FILES,
        source_commit_message,
    )

    for public_file in PUBLIC_FILES:
        if not (repo_root / public_file.source).exists():
            raise PublishError(
                f"Required public file is missing on {source_branch}: "
                f"{public_file.source}"
            )

    branch_exists = (
        run_git(
            repo_root,
            "show-ref",
            "--verify",
            "--quiet",
            f"refs/heads/{pages_branch}",
            check=False,
        ).returncode
        == 0
    )

    try:
        if branch_exists:
            run_git(repo_root, "switch", pages_branch)
        else:
            run_git(repo_root, "switch", "--orphan", pages_branch)

        remove_worktree_contents(repo_root)
        publish_files(repo_root, source_branch, PUBLIC_FILES)

        run_git(repo_root, "add", "-A")
        if not status_lines(repo_root):
            print("No GitHub Pages changes to commit.")
        else:
            run_git(repo_root, "commit", "-m", commit_message)
            print(f"Updated {pages_branch} from {source_branch}.")

        run_git(repo_root, "push", "-u", "origin", pages_branch)
        print(f"Pushed {pages_branch} to origin.")
    finally:
        run_git(repo_root, "switch", source_branch)


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Refresh the gh-pages branch with the public static-site files."
    )
    parser.add_argument(
        "--pages-branch",
        default=DEFAULT_PAGES_BRANCH,
        help=f"Pages branch to update (default: {DEFAULT_PAGES_BRANCH}).",
    )
    parser.add_argument(
        "--commit-message",
        default=DEFAULT_COMMIT_MESSAGE,
        help="Commit message for the gh-pages update.",
    )
    parser.add_argument(
        "--source-commit-message",
        default=DEFAULT_SOURCE_COMMIT_MESSAGE,
        help="Commit message for generated source-branch files.",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        publish(
            pages_branch=args.pages_branch,
            commit_message=args.commit_message,
            source_commit_message=args.source_commit_message,
        )
    except PublishError as exc:
        raise SystemExit(str(exc)) from exc
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
