"""Release Shoebox: bump the version in manifest.json, commit, tag, and push after confirmation.

Usage: release.py [VERSION | patch | minor | major | beta | rc | final] [--dry-run] [--yes]

Without an argument it shows the current version. Pre-releases use Home Assistant's style:
1.2.0b1, 1.2.0rc1. A stable version starts a beta or release candidate of the next minor version.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import subprocess
import sys

from packaging.version import InvalidVersion, Version

MANIFEST = Path("custom_components/shoebox/manifest.json")
KINDS = ("patch", "minor", "major", "beta", "rc", "final")


class ReleaseError(Exception):
    pass


def next_version(current: str, kind: str) -> str:
    """The version after `current` for a kind, or `kind` itself when it is a version."""
    now = Version(current)
    base = f"{now.major}.{now.minor}.{now.micro}"
    if kind not in KINDS:
        try:
            wanted = Version(kind)
        except InvalidVersion as err:
            raise ReleaseError(
                f"{kind} is neither a version nor one of {', '.join(KINDS)}"
            ) from err
        if wanted <= now:
            raise ReleaseError(f"{kind} is not newer than {current}")
        return str(wanted)
    stage, number = now.pre or (None, 0)
    if kind == "final":
        if stage is None:
            raise ReleaseError(f"{current} is already final")
        return base
    if kind in ("patch", "minor", "major"):
        if stage is not None:
            raise ReleaseError(
                f"{current} is a pre-release: release it with final, or continue with beta or rc"
            )
        if kind == "patch":
            return f"{now.major}.{now.minor}.{now.micro + 1}"
        if kind == "minor":
            return f"{now.major}.{now.minor + 1}.0"
        return f"{now.major + 1}.0.0"
    letter = "b" if kind == "beta" else "rc"
    if stage is None:
        return f"{now.major}.{now.minor + 1}.0{letter}1"
    if stage == letter:
        return f"{base}{letter}{number + 1}"
    if letter == "rc":
        return f"{base}rc1"
    raise ReleaseError(f"{current} is a release candidate: continue with rc or final")


def git(*args: str) -> str:
    return subprocess.run(["git", *args], check=True, capture_output=True, text=True).stdout.strip()


def check_tree(tag: str) -> list[str]:
    problems = []
    if git("status", "--porcelain"):
        problems.append("the working tree has uncommitted changes")
    if git("tag", "--list", tag):
        problems.append(f"tag {tag} already exists")
    return problems


def write_version(version: str) -> None:
    text = MANIFEST.read_text()
    MANIFEST.write_text(re.sub(r'"version": "[^"]*"', f'"version": "{version}"', text))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("target", nargs="?")
    parser.add_argument("--dry-run", action="store_true", help="show the plan, change nothing")
    parser.add_argument("--yes", action="store_true", help="do not ask before releasing")
    args = parser.parse_args()
    current = json.loads(MANIFEST.read_text())["version"]
    if args.target is None:
        print(f"Shoebox {current}")
        return 0
    try:
        version = next_version(current, args.target)
    except ReleaseError as err:
        print(f"error: {err}", file=sys.stderr)
        return 1
    tag = f"v{version}"
    branch = git("rev-parse", "--abbrev-ref", "HEAD")
    channel = "pre-release" if Version(version).is_prerelease else "full release (latest)"
    print(f"{current} -> {version}: manifest.json, commit 'Release {tag}', tag {tag}")
    print(f"push {branch} and {tag} to origin; GitHub publishes a {channel}")
    if f"## {version}" not in Path("CHANGELOG.md").read_text():
        print(f"warning: CHANGELOG.md has no '## {version}' section")
    if problems := check_tree(tag):
        print("\n".join(f"cannot release: {p}" for p in problems), file=sys.stderr)
        return 1
    if args.dry_run:
        return 0
    if not args.yes and (not sys.stdin.isatty() or input("Release? [y/N] ").strip().lower() != "y"):
        print("nothing changed")
        return 1
    write_version(version)
    git("commit", "--quiet", "-am", f"Release {tag}")
    git("tag", "--annotate", tag, "--message", f"Shoebox {version}")
    git("push", "--quiet", "origin", branch, tag)
    print(f"released {tag}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
