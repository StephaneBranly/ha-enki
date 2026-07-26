"""Test configuration."""

from pathlib import Path
import sys
from types import ModuleType


# Import integration modules without loading Home Assistant's integration setup.
enki_package = ModuleType("custom_components.enki")
enki_package.__path__ = [
    str(Path(__file__).parents[1] / "custom_components" / "enki")
]
sys.modules["custom_components.enki"] = enki_package
