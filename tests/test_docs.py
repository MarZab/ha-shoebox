"""Relative links in the README and docs/ point to files and headings that exist."""

from __future__ import annotations

from pathlib import Path
import re

import pytest

ROOT = Path(__file__).parents[1]
PAGES = [ROOT / "README.md", ROOT / "AGENTS.md", *sorted((ROOT / "docs").glob("*.md"))]
LINK = re.compile(r"\]\(([^)\s]+)\)")


def anchors(page: Path) -> set[str]:
    """GitHub's heading anchors: lower case, punctuation dropped, spaces as hyphens."""
    headings = re.findall(r"^#+ (.+)$", page.read_text(), re.M)
    return {re.sub(r"[^\w\- ]", "", h.lower()).replace(" ", "-") for h in headings}


@pytest.mark.parametrize("page", PAGES, ids=lambda p: p.name)
def test_links_resolve(page: Path) -> None:
    for target in LINK.findall(page.read_text()):
        if target.startswith(("http://", "https://")):
            continue
        path, _, anchor = target.partition("#")
        linked = (page.parent / path).resolve() if path else page
        assert linked.exists(), f"{page.name}: {target}"
        if anchor:
            assert anchor in anchors(linked), f"{page.name}: {target}"
