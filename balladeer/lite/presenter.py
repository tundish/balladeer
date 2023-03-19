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


from collections import defaultdict
from collections import namedtuple
import importlib.resources
import inspect
import pathlib
import pprint
import tomllib
import uuid


from balladeer.lite.director import Director
from balladeer.lite.loader import Loader
from balladeer.lite.types import group_by_type
from balladeer.lite.types import Thing


class Presenter:
    """
    Wrap xhtml with animation div.
    """
    pass


class Prompter:

    @staticmethod
    def object_type_name(obj):
        return f"{obj.__class__.__module__}.{obj.__class__.__name__}"

    def select(asset: Loader.Asset, ensemble: list=None, shot_key="_", dlg_key="-"):
        "From turberfield.dialogue.model.SceneScript"
        ensemble = ensemble or []
        entities = dict((k, t) for k, t in asset.tables.items() if k != shot_key)

        pool = {Prompter.object_type_name(v[0]): v for t, v in group_by_type(ensemble).items() if v}
        print(pool)
        return {}

    def cast(asset: Loader.Asset, ensemble: list, shot_key="_", dlg_key="-"):
        entities = dict((k, t) for k, t in asset.tables if k != shot_key)
        return scene

    def update(asset: Loader.Asset, shot_key="_", dlg_key="-"):
        entities = dict((k, t) for k, t in asset.tables.items() if k != shot_key)
        shots = asset.tables.get(shot_key, [])
        return scene


assets = Loader.discover("balladeer.lite")


ensemble = [
    Thing(name="thing").set_state(0)
]

if __name__ == "__main__":
    for i in ensemble:
        typ = Prompter.object_type_name(i)
        # print(typ)

    for a in assets:
        asset, result = Parser.check(a, shot_key="_")
        pprint.pprint(a.tables)
        casting = Prompter.select(asset, ensemble)
