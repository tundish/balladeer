#!usr/bin/env python3
# encoding: utf-8

import importlib.resources
import tomllib


def loader(package, resource=".", suffixes=[".dlg.toml"]):
    for path in importlib.resources.files(package).joinpath(resource).iterdir():
        if "".join(path.suffixes) in suffixes:
            with importlib.resources.as_file(path) as f:
                text = f.read_text(encoding="utf8")
                yield (resource, path, tomllib.loads(text))

assets = loader("balladeer.lite")
print(*list(assets), sep="\n")
