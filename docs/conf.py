import os
import sys
from datetime import date

sys.path.insert(0, os.path.abspath("../src"))

project = "t61codec"
copyright = f"2019-{date.today().year}, Michel Albert"
author = "Michel Albert"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.doctest",
    "sphinx.ext.viewcode",
    "sphinx_copybutton",
]

templates_path = ["_templates"]
exclude_patterns = ["_build"]

html_theme = "furo"
html_static_path = ["_static"]
