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

html_theme = "alabaster"
html_static_path = ["_static"]
html_title = f"{project} {release}"
html_theme_options = {
    "font_family": "Georgia, serif",
    "head_font_family": "Georgia, serif",
    "fixed_sidebar": True,
    "show_powered_by": True,
}
html_sidebars = {'**': ['globaltoc.html', 'github.html']}
# These folders are copied to the documentation's HTML output
html_static_path = ['_static']

# These paths are either relative to html_static_path
# or fully qualified paths (eg. https://...)
html_css_files = [
    "balladeer_doc_style.css",
]

pygments_style = "sphinx"
todo_include_todos = True

autodoc_class_signature = "separated"
