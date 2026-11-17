"""services.yaml, icons.json, translations and the registered actions describe the same things."""

from __future__ import annotations

import json
from pathlib import Path
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
