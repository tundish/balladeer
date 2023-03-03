#!usr/bin/env python3
# encoding: utf-8

import importlib.resources
import pprint
import tomllib


def loader(package, resource=".", suffixes=[".dlg.toml"]):
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
                yield (resource, path, text, tables, error)

assets = loader("balladeer.lite")

def checker():
    # lower case the sections: S, IF, DO
    yield

for a in assets:
    pprint.pprint(a)
