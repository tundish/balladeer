#!/usr/bin/env python3
#   encoding: utf-8

# This is part of the Balladeer library.
# Copyright (C) 2023 D E Haynes

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from collections import namedtuple
import importlib.resources
from importlib.resources import Package
import mimetypes
from pathlib import Path
import re
import tomllib


class Loader:
    Asset = namedtuple("Asset", ["resource", "path", "type", "stats"], defaults=[None, None])
    Scene = namedtuple(
        "Scene",
        ["text", "tables", "resource", "path", "stats"],
        defaults=[None, None, None],
    )
    Storage = namedtuple("Storage", ["resource", "path", "stats"], defaults=[None])

    @staticmethod
    def discover(
        package: [Package | Path],
        resource=".",
        suffixes={
            ".db": Storage,
            ".scene.toml": Scene,
        },
        avoid=["__pycache__", "node_modules"],
        ignore=[re.compile("^test_.*")],
    ):
        if isinstance(package, Path):
            paths = list(package.iterdir()) if package.is_dir() else [package]
        else:
            paths = list(importlib.resources.files(package).joinpath(resource).iterdir())

        for path in paths:
            if path.is_dir() and path.name not in avoid:
                yield from Loader.discover(path, resource, suffixes, avoid, ignore)
            elif any(i.match(path.name) for i in ignore):
                continue

            typ, _ = mimetypes.guess_type(path)
            if typ and typ != "text/x-python":
                with importlib.resources.as_file(path) as f:
                    yield Loader.Asset(resource, path, typ, f.stat())

            typ = suffixes.get("".join(path.suffixes))
            if typ is Loader.Scene:
                with importlib.resources.as_file(path) as f:
                    text = f.read_text(encoding="utf8")
                    yield Loader.read(text, resource=resource, path=path)
            elif typ:
                with importlib.resources.as_file(path) as f:
                    yield typ(resource=resource, path=path)

    @staticmethod
    def read(text: str, resource="", path=None):
        try:
            tables = tomllib.loads(text)
            stats = {}
        except tomllib.TOMLDecodeError as e:
            tables = {}
            stats = e
        return Loader.Scene(text, tables, resource, path, stats)
