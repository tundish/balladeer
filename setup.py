#!/usr/bin/env python
# encoding: UTF-8

import ast
from setuptools import setup
import os.path

__doc__ = open(
    os.path.join(os.path.dirname(__file__), "README.rst"),
    "r"
).read()

try:
    # For setup.py install
    from balladeer import __version__ as version
except ImportError:
    # For pip installations
    version = str(ast.literal_eval(
        open(os.path.join(
            os.path.dirname(__file__),
            "balladeer",
            "__init__.py"),
            "r"
        ).readlines()[0].split("=")[-1].strip()
    ))

setup(
    name="balladeer",
    version=version,
    description="Web-enabled interactive fiction in Python.",
    author="D E Haynes",
    author_email="tundish@gigeconomy.org.uk",
    url="https://github.com/tundish/balladeer",
    long_description=__doc__,
    long_description_content_type="text/x-rst",
    classifiers=[
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: GNU General Public License v3"
        " or later (GPLv3+)"
    ],
    packages=["balladeer", "balladeer.test"],
    package_data={
        "balladeer": [
            "doc/*.rst",
            "doc/_templates/*.css",
            "doc/html/*.html",
            "doc/html/*.js",
            "doc/html/_sources/*",
            "doc/html/_static/css/*",
            "doc/html/_static/font/*",
            "doc/html/_static/js/*",
            "doc/html/_static/*.css",
            "doc/html/_static/*.gif",
            "doc/html/_static/*.js",
            "doc/html/_static/*.png",
        ],
    },
    install_requires=[
        "docutils==0.18.1",
        "turberfield-catchphrase==0.25.0",
        "turberfield-dialogue==0.39.0",
        "turberfield-utils==0.39.0",
    ],
    extras_require={
        "dev": [
            "flake8",
            "twine",
            "wheel",
        ],
    },
    entry_points={},
    zip_safe=True,
)
