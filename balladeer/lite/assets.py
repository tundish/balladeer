#!usr/bin/env python3
# encoding: utf-8

import importlib.resources

f = [importlib.resources.as_file(p) for p in importlib.resources.files("balladeer.lite").joinpath(".").iterdir()]
print(*list(f), sep="\n")
