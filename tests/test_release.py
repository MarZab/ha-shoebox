from __future__ import annotations

from pathlib import Path
import subprocess
import sys

import pytest

sys.path.insert(0, str(Path(__file__).parents[1] / "tools/scripts"))

from release import ReleaseError, check_tree, next_version


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


def test_check_tree_refuses_dirty_tree_and_existing_tag(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def git(*args: str) -> None:
        subprocess.run(["git", *args], cwd=tmp_path, check=True, capture_output=True)

    git("init", "-q")
    (tmp_path / "a").write_text("a")
    git("add", "a")
    git("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "a")
    git("tag", "v1.0.0")
    monkeypatch.chdir(tmp_path)
    assert check_tree("v1.1.0") == []
    (tmp_path / "a").write_text("b")
    assert check_tree("v1.0.0") == [
        "the working tree has uncommitted changes",
        "tag v1.0.0 already exists",
    ]
