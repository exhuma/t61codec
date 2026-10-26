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
    "michel_albert_sphinx",
]

exclude_patterns = ["_build"]

html_baseurl = "https://exhuma.github.io/t61codec/"
html_static_path = ["_static"]
html_theme_options = {
    "repo_url": "https://github.com/exhuma/t61codec",
    "repo_name": "exhuma/t61codec",
    "edit_uri": "blob/master/docs",
    "features": [
        "content.code.copy",
        "navigation.top",
        "toc.follow",
    ],
}
