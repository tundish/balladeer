#!usr/bin/env python3
# encoding: utf-8

from collections import namedtuple
import importlib.resources
import pprint
import tomllib

import markdown


class Loader:

    Asset = namedtuple("Scene", ["resource", "path", "text", "tables", "error"])

    def discover(package, resource=".", suffixes=[".dlg.toml"]):
        for path in importlib.resources.files(package).joinpath(resource).iterdir():
            if "".join(path.suffixes) in suffixes:
                with importlib.resources.as_file(path) as f:
                    text = f.read_text(encoding="utf8")
                    try:
                        tables = tomllib.loads(text)
                        error = None
                    except tomllib.TOMLDecodeError as e:
                        tables = None
                        error = e
                    yield Loader.Asset(resource, path, text, tables, error)

    def check(asset: Asset):
        # lower case the sections: S, IF, DO
        return asset


class Prompter:

    def select(asset: Loader.Asset, ensemble: list=None, shot_key="_", dlg_key="-"):
        "From turberfield.dialogue.model.SceneScript"
        return {}

    def cast(asset: Loader.Asset, ensemble: list, shot_key="_", dlg_key="-"):
        entities = dict((k, t) for k, t in asset.tables if k != shot_key)
        return scene

    def update(asset: Loader.Asset, shot_key="_", dlg_key="-"):
        entities = dict((k, t) for k, t in asset.tables if k != shot_key)
        shots = asset.tables.get(shot_key, [])
        return scene

assets = Loader.discover("balladeer.lite")

for a in assets:
    asset = Loader.check(a)
    pprint.pprint(a.tables)
    casting = Prompter.select(asset)
