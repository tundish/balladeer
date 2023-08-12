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


import copy
import enum
import operator
import pathlib
import shutil
import sqlite3
import sys
import tempfile
import textwrap
import unittest
import uuid

from balladeer.lite.entity import Entity
from balladeer.lite.types import State

from balladeer.lite.loader import Loader
from balladeer.lite.types import Grouping


class LoaderTests(unittest.TestCase):

    def setUp(self):
        self.path = pathlib.Path(tempfile.mkdtemp(prefix="balladeer-", suffix="-test"))

    def tearDown(self):
        shutil.rmtree(self.path)

    def test_single_scene(self):
        text = textwrap.dedent("""
        [NARRATOR]
        type = "Narrator"
        """)
        self.path.joinpath("test.scene.toml").write_text(text)
        assets = list(Loader.discover(self.path))
        self.assertEqual(1, len(assets))
        self.assertIsInstance(assets[0], Loader.Scene)

    def test_sqlite_database(self):
        path = self.path.joinpath("test.db")
        con = sqlite3.connect(path)
        con.close()

        assets = list(Loader.discover(self.path))
        self.assertEqual(1, len(assets))
        self.assertIsInstance(assets[0], Loader.Storage)

    def test_toml_file(self):
        text = textwrap.dedent("""
        [DB]
        host = "localhost"
        port = 5432
        """)
        self.path.joinpath("config.toml").write_text(text)
        assets = list(Loader.discover(self.path))
        self.assertEqual(1, len(assets))
        self.assertIsInstance(assets[0], Loader.Structure)

        self.assertEqual(5432, assets[0].data["DB"]["port"])

    def test_style_files(self):
        styles = {
            ("basics.css",): "cite {color: red;}",
            ("style-gallery.css",): "cite {color: green;}",
            ("styles", "cover.css"): "cite {color: blue;}",
            ("styles", "gallery.css"): "cite {color: black;}",
        }
        self.path.joinpath("styles").mkdir()
        for paths, text in styles.items():
            self.path.joinpath(*paths).write_text(text)

        assets = Grouping.typewise(Loader.discover(self.path))
        self.assertEqual(4, len(assets["text/css"]), assets)

        for n, selection in enumerate(((), ("cover",), ("gallery",), ("cover", "gallery"))):
            with self.subTest(n=n, selection=selection):
                staged = Loader.stage(assets, *selection)
                self.assertIsInstance(staged, Grouping)
                self.assertTrue(next(i for i in staged["text/css"] if i.path.name == "basics.css"), False)
                self.assertEqual(len(staged.each), 1 + selection.count("cover") + 2 * selection.count("gallery"))


class SceneTests(unittest.TestCase):
    def test_one_scene(self):
        content = textwrap.dedent("""
            [[_]]

            s='''
            Text
            '''
        """)
        data = Loader.read_toml(content)
        self.assertIsInstance(data, dict)
        self.assertEqual(1, len(data.get("_")))

        self.assertEqual("Text\n", data["_"][0]["s"])

    def test_multi_scene(self):
        content = textwrap.dedent("""
            [[_]]

            s='''
            Text
            '''

            [[_]]

            s='''
            Text
            '''
        """)
        data = Loader.read_toml(content)
        self.assertIsInstance(data, dict)
        self.assertEqual(2, len(data.get("_")))

        self.assertEqual("Text\n", data["_"][0]["s"])
        self.assertEqual("Text\n", data["_"][1]["s"])
