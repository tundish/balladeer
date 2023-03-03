#!usr/bin/env python3
# encoding: utf-8

from collections import defaultdict
from collections import namedtuple
import importlib.resources
import inspect
import pprint
import tomllib
import uuid

import markdown

# from turberfield.utils.assembly import Assembly


# turberfield.utils.misc
def group_by_type(items):
    rv = defaultdict(list)
    for i in items:
        rv[type(i)].append(i)
    return rv


# turberfield.dialogue.types
class EnumFactory:

    @classmethod
    def factory(cls, name=None, **kwargs):
        return cls[name]


# turberfield.dialogue.types
class DataObject:

    def __init__(self, *args, id=None, **kwargs):
        super().__init__(*args)
        self.id = id or uuid.uuid4()
        for k, v in kwargs.items():
            setattr(self, k, v)

    def __repr__(self):
        return "<{0}> {1}".format(type(self).__name__, vars(self))


# turberfield.dialogue.types
class Stateful:

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._states = {}

    @property
    def state(self):
        return self.get_state()

    @state.setter
    def state(self, value):
        return self.set_state(value)

    def set_state(self, *args):
        for value in args:
            self._states[type(value).__name__] = value
        return self

    def get_state(self, typ=int, default=0):
        return self._states.get(typ.__name__, default)


class Thing(DataObject, Stateful): pass


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
        entities = dict((k, t) for k, t in asset.tables if k != shot_key)
        shots = asset.tables.get(shot_key, [])
        return scene


assets = Loader.discover("balladeer.lite")


ensemble = [
    Thing(name="thing").set_state(0)
]


for a in assets:
    for i in ensemble:
        typ = Prompter.object_type_name(i)
        print(typ)

    asset = Loader.check(a)
    pprint.pprint(a.tables)
    casting = Prompter.select(asset, ensemble)
