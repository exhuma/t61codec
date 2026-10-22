"""
Run the documentation examples as doctests.
"""

import doctest
from pathlib import Path

import t61codec

ROOT = Path(__file__).parent.parent


def test_readme_examples() -> None:
    """
    Ensure the interactive examples in README.rst hold.
    """
    result = doctest.testfile(str(ROOT / "README.rst"), module_relative=False)

    assert result.attempted > 0
    assert result.failed == 0


def test_module_docstring_examples() -> None:
    """
    Ensure the interactive examples in the module docstrings hold.
    """
    result = doctest.testmod(t61codec)

    assert result.attempted > 0
    assert result.failed == 0
