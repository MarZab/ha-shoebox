"""Print a version's section of CHANGELOG.md, for the GitHub release text.

Usage: release_notes.py <version> [changelog]  (prints nothing when the version has no section)
"""

from __future__ import annotations

from pathlib import Path
import re
import sys


def notes(changelog: str, version: str) -> str:
    """The lines under "## <version>", up to the next "## " heading, without surrounding blanks."""
    match = re.search(rf"^## {re.escape(version)}[ \t]*\n(.*?)(?=^## |\Z)", changelog, re.M | re.S)
    if not match:
        return ""
    return re.sub(r"\n{3,}", "\n\n", match.group(1)).strip()


if __name__ == "__main__":
    path = Path(sys.argv[2] if len(sys.argv) > 2 else "CHANGELOG.md")
    if text := notes(path.read_text(), sys.argv[1]):
        print(text)
