#!/usr/bin/env python3
#   encoding: utf-8

# This is part of the Balladeer library.
# Copyright (C) 2022 D E Haynes

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
import re
import tomllib

import markdown


class Loader:

    Asset = namedtuple("Scene", ["text", "tables", "resource", "path", "error"], defaults=[None, None, None])

    def discover(package, resource=".", suffixes=[".dlg.toml"]):
        for path in importlib.resources.files(package).joinpath(resource).iterdir():
            if "".join(path.suffixes) in suffixes:
                with importlib.resources.as_file(path) as f:
                    text = f.read_text(encoding="utf8")
                    yield Loader.read(text)

    def read(text: str, resource="", path=None):
        try:
            tables = tomllib.loads(text)
            error = None
        except tomllib.TOMLDecodeError as e:
            tables = None
            error = e
        return Loader.Asset(text, tables, resource, path, error)

    def check(asset: Asset, shot_key):
        result = dict(shots=len(asset.tables.get(shot_key, [])))
        return asset, result
