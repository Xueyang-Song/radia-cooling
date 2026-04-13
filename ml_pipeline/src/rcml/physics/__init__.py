from __future__ import annotations

from rcml.physics.mock_backend import MockThinFilmBackend
from rcml.physics.wptherml_runner import WPThermlBackend


def build_backend(name: str):
    normalized = name.strip().lower()
    if normalized == "mock":
        return MockThinFilmBackend()
    if normalized == "wptherml":
        return WPThermlBackend()
    raise ValueError(f"Unsupported backend: {name}")