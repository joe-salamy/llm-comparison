from __future__ import annotations

import importlib.util
import subprocess
import sys
import types
from pathlib import Path


def load_publisher_module() -> types.ModuleType:
    script_path = Path(__file__).resolve().parents[1] / "update-gh-pages.py"
    spec = importlib.util.spec_from_file_location("update_gh_pages", script_path)
    if spec is None or spec.loader is None:
        raise AssertionError("could not load update-gh-pages.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=repo,
        check=True,
        encoding="utf-8",
        stdout=subprocess.PIPE,
    )
    return result.stdout.strip()


def write_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def create_source_repo(repo: Path, remote: Path) -> None:
    git(repo.parent, "init", "-b", "main", repo.name)
    git(repo, "config", "user.email", "test@example.com")
    git(repo, "config", "user.name", "Test User")

    public_sources = {
        "public/index.html": "<h1>report</h1>\n",
        "data/results.csv": "model,score\nA,1\n",
        "src/llm_comparison/compare_models.py": "print('compare')\n",
        "src/llm_comparison/compare_models_core.py": "CORE = True\n",
        "src/llm_comparison/compare_models_template.py": "TEMPLATE = True\n",
        "README.md": "# Project\n",
        ".gitignore": "__pycache__/\n",
    }
    for relative_path, content in public_sources.items():
        write_file(repo / relative_path, content)

    write_file(repo / "data/input.txt", "private input\n")
    write_file(repo / "tests/test_private.py", "def test_private(): pass\n")

    git(repo, "add", ".")
    git(repo, "commit", "-m", "Initial source")

    git(remote.parent, "init", "--bare", remote.name)
    git(repo, "remote", "add", "origin", str(remote))


def test_status_paths_returns_renamed_destination_once() -> None:
    publisher = load_publisher_module()

    assert publisher.status_paths(
        [
            " M public/index.html",
            "R  old/results.csv -> data/results.csv",
            " M public/index.html",
        ]
    ) == ["public/index.html", "data/results.csv"]


def test_publish_writes_only_public_files_and_returns_to_source_branch(
    tmp_path: Path,
) -> None:
    publisher = load_publisher_module()
    repo = tmp_path / "repo"
    remote = tmp_path / "origin.git"
    create_source_repo(repo, remote)

    publisher.publish(repo_root=repo)

    assert git(repo, "branch", "--show-current") == "main"
    assert set(git(repo, "ls-tree", "--name-only", "gh-pages").splitlines()) == {
        ".gitignore",
        "README.md",
        "compare_models.py",
        "compare_models_core.py",
        "compare_models_template.py",
        "index.html",
        "results.csv",
    }
    assert git(remote, "branch", "--list", "gh-pages") == "gh-pages"
