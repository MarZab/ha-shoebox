from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
import subprocess
import sys

import pytest

sys.path.insert(0, str(Path(__file__).parents[1] / "tools/scripts"))

from release import ReleaseError, check_tree, next_version, publish


@pytest.mark.parametrize(
    ("current", "kind", "expected"),
    [
        ("1.2.3", "patch", "1.2.4"),
        ("1.2.3", "minor", "1.3.0"),
        ("1.2.3", "major", "2.0.0"),
        ("1.2.3", "beta", "1.3.0b1"),
        ("1.3.0b1", "beta", "1.3.0b2"),
        ("1.3.0b2", "rc", "1.3.0rc1"),
        ("1.3.0rc1", "rc", "1.3.0rc2"),
        ("1.2.3", "rc", "1.3.0rc1"),
        ("1.3.0rc2", "final", "1.3.0"),
        ("1.3.0b1", "final", "1.3.0"),
        ("1.2.3", "1.5.0", "1.5.0"),
        ("1.3.0b1", "1.3.0", "1.3.0"),
    ],
)
def test_next_version(current: str, kind: str, expected: str) -> None:
    assert next_version(current, kind) == expected


def test_an_unreleased_version_can_be_released_as_it_is() -> None:
    assert next_version("0.1.0", "0.1.0", released=False) == "0.1.0"
    with pytest.raises(ReleaseError, match="not newer"):
        next_version("0.1.0", "0.1.0", released=True)


@pytest.mark.parametrize(
    ("current", "kind", "message"),
    [
        ("1.2.3", "final", "already final"),
        ("1.3.0b1", "patch", "pre-release"),
        ("1.3.0rc1", "beta", "release candidate"),
        ("1.2.3", "1.2.3", "not newer"),
        ("1.2.3", "1.0.0", "not newer"),
        ("1.2.3", "soon", "neither a version"),
    ],
)
def test_next_version_refuses(current: str, kind: str, message: str) -> None:
    with pytest.raises(ReleaseError, match=message):
        next_version(current, kind)


def repo(path: Path, remote: Path | None) -> Callable[..., str]:
    def git(*args: str) -> str:
        return subprocess.run(
            ["git", *args], cwd=path, check=True, capture_output=True, text=True
        ).stdout.strip()

    path.mkdir()
    git("init", "-q", "-b", "main")
    git("config", "user.name", "t")
    git("config", "user.email", "t@t")
    (path / "custom_components/shoebox").mkdir(parents=True)
    (path / "custom_components/shoebox/manifest.json").write_text('{"version": "1.0.0"}')
    git("add", ".")
    git("commit", "-qm", "a")
    if remote:
        git("remote", "add", "origin", str(remote))
    return git


def test_check_tree_refuses_dirty_tree_existing_tag_and_no_remote(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    subprocess.run(["git", "init", "-q", "--bare", str(tmp_path / "remote")], check=True)
    git = repo(tmp_path / "work", tmp_path / "remote")
    git("tag", "v1.0.0")
    monkeypatch.chdir(tmp_path / "work")
    assert check_tree("v1.1.0") == []
    (tmp_path / "work/custom_components/shoebox/manifest.json").write_text("{}")
    git("remote", "remove", "origin")
    assert check_tree("v1.0.0") == [
        "the working tree has uncommitted changes",
        "tag v1.0.0 already exists",
        "origin cannot be reached (git remote add origin <url>?)",
    ]


def test_a_failed_push_leaves_no_commit_or_tag(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    git = repo(tmp_path / "work", tmp_path / "gone")  # a remote that does not exist
    head = git("rev-parse", "HEAD")
    monkeypatch.chdir(tmp_path / "work")
    with pytest.raises(subprocess.CalledProcessError):
        publish("1.1.0", "v1.1.0", "main")
    assert (git("rev-parse", "HEAD"), git("tag", "--list"), git("status", "--porcelain")) == (
        head,
        "",
        "",
    )
