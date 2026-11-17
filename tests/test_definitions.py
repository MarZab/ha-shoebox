"""services.yaml, icons.json, translations and the registered actions describe the same things."""

from __future__ import annotations

import json
from pathlib import Path
import re
from typing import Any

import yaml

from custom_components.shoebox.errors import MESSAGES
from custom_components.shoebox.services import SERVICES

PACKAGE = Path(__file__).parents[1] / "custom_components/shoebox"


def load(name: str) -> Any:
    text = (PACKAGE / name).read_text()
    return yaml.safe_load(text) if name.endswith(".yaml") else json.loads(text)


def test_every_action_is_described_translated_and_has_an_icon() -> None:
    described = load("services.yaml")
    translated = load("translations/en.json")["services"]
    assert set(SERVICES) == set(described) == set(translated) == set(load("icons.json")["services"])
    for name, spec in described.items():
        assert set(spec["fields"]) == set(translated[name]["fields"]), name


def test_error_messages_match_the_translations() -> None:
    exceptions = load("translations/en.json")["exceptions"]
    assert {key: exceptions[key]["message"] for key in MESSAGES} == MESSAGES


def keys(tree: Any, prefix: str = "") -> set[str]:
    if not isinstance(tree, dict):
        return {prefix}
    return set().union(*(keys(v, f"{prefix}.{k}") for k, v in tree.items()))


def placeholders(tree: Any) -> dict[str, set[str]]:
    def walk(node: Any, prefix: str) -> dict[str, set[str]]:
        if isinstance(node, dict):
            return {
                k: v for key, sub in node.items() for k, v in walk(sub, f"{prefix}.{key}").items()
            }
        return {prefix: set(re.findall(r"\{(\w+)\}", node))}

    return walk(tree, "")


def test_slovenian_matches_english() -> None:
    en, sl = load("translations/en.json"), load("translations/sl.json")
    assert keys(sl) == keys(en)
    assert placeholders(sl) == placeholders(en)


def panel_texts() -> dict[str, dict[str, str]]:
    source = (PACKAGE / "frontend/i18n.js").read_text()
    languages = re.findall(r"^  (\w+): \{\n(.*?)^  \},", source, re.M | re.S)
    return {
        lang: dict(re.findall(r'^\s{4}(\w+): "((?:[^"\\]|\\.)*)",', body, re.M))
        for lang, body in languages
    }


def test_panel_languages_have_the_same_texts() -> None:
    texts = panel_texts()
    assert set(texts) == {"en", "sl"}
    assert texts["en"].keys() == texts["sl"].keys()
    for key, english in texts["en"].items():
        assert set(re.findall(r"\{(\w+)\}", english)) == set(
            re.findall(r"\{(\w+)\}", texts["sl"][key])
        ), key


def test_panel_uses_only_known_texts() -> None:
    code = "".join((PACKAGE / f"frontend/{n}").read_text() for n in ("shoebox-panel.js", "crop.js"))
    used = set(re.findall(r"""\bt\(\s*["'](\w+)["']""", code))
    assert used <= panel_texts()["en"].keys()
