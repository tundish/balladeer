# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import pathlib
import pkgutil
import sys

try:
    import balladeer
except ImportError:
    sys.path.append(str(pathlib.Path(__file__).parent.parent.parent))

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "Balladeer"
copyright = "2023, D E Haynes"
author = "D E Haynes"
release = pkgutil.resolve_name("balladeer.__version__")

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ["sphinx.ext.autodoc"]

templates_path = ["_templates"]
exclude_patterns = [
    "_build",
]


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme_path = ["../../../karma_sphinx_theme"]
html_theme = "karma_sphinx_theme"
html_static_path = ["_static"]
html_title = f"{project} {release}"
html_theme_options = {
    "navigation_depth": 2,
    "includehidden": True,
    "titles_only": False
}

autodoc_class_signature = "separated"
