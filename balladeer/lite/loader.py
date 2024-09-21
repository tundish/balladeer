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
from typing import Mapping

from balladeer.lite.types import Grouping
from busker.stager import Stager


class Loader:
    Asset = namedtuple("Asset", ["resource", "path", "type", "stats"], defaults=[None, None])
    Scene = namedtuple(
        "Scene",
        ["text", "tables", "resource", "path", "stats"],
        defaults=[None, None, None],
    )
    Storage = namedtuple("Storage", ["resource", "path", "stats"], defaults=[None])
    Staging = namedtuple("Staging", ["text", "data", "resource", "path", "stats"], defaults=[None, None, None])
    Structure = namedtuple("Structure", ["text", "data", "resource", "path", "stats"], defaults=[None, None, None])

    @staticmethod
    def discover(
        package: [Package | Path],
        resource=".",
        suffixes={
            ".db": Storage,
            ".scene.toml": Scene,
            ".stage.toml": Staging,
            ".toml": Structure,
        },
        avoid=["tmp", "__pycache__", "node_modules"],
        ignore=[re.compile("^test_.*")],
    ):
        if isinstance(package, Path):
            paths = list(package.iterdir()) if package.is_dir() else [package]
        else:
            paths = list(importlib.resources.files(package).joinpath(resource).iterdir())

        for path in paths:
            if path.is_dir() and path.name in avoid:
                continue
            elif path.is_dir():
                yield from Loader.discover(path, resource, suffixes, avoid, ignore)
            elif any(i.match(path.name) for i in ignore):
                continue

            typ, _ = mimetypes.guess_type(path)
            if typ and typ != "text/x-python":
                with importlib.resources.as_file(path) as f:
                    yield Loader.Asset(resource, path, typ, f.stat())

            typ = suffixes.get("".join(path.suffixes))
            if typ in (Loader.Scene, Loader.Structure):
                with importlib.resources.as_file(path) as f:
                    text = f.read_text(encoding="utf8")
                    data = Loader.read_toml(text)
                    yield typ(text, data, resource, path, f.stat())
            elif typ == Loader.Staging:
                with importlib.resources.as_file(path) as f:
                    text = f.read_text(encoding="utf8")
                    data = next(Stager.load(text))
                    yield typ(text, data, resource, path, f.stat())
            elif typ:
                with importlib.resources.as_file(path) as f:
                    yield typ(resource, path, f.stat())

    @staticmethod
    def ignore_style(asset: Asset, *args) -> bool:
        if any(i in str(asset.path) for i in args):
            return True
        return "style" not in str(asset.path)

    @staticmethod
    def stage(assets: Grouping[str, list[Asset]], *args, predicate=None) -> Grouping[str, list[Asset]]:
        assert isinstance(assets, Mapping), type(assets)
        predicate = predicate or Loader.ignore_style

        rv = assets.copy()
        for key in assets:
            rv[key] = [i for i in assets[key] if predicate(i, *args)]

        return rv

    @staticmethod
    def read_toml(text: str, resource="", path=None):
        try:
            return tomllib.loads(text)
        except tomllib.TOMLDecodeError as e:
            return {}
