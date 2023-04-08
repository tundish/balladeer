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
import sys
import textwrap
import unittest
import uuid

from balladeer.lite.types import Entity
from balladeer.lite.types import State

from balladeer.lite.loader import Loader


class SceneTests(unittest.TestCase):
    def test_one_scene(self):
        content = textwrap.dedent("""
            [[_]]

            s='''
            Text
            '''
        """)
        scene = Loader.read(content)
        self.assertIsInstance(scene, Loader.Scene)
        self.assertEqual(1, len(scene.tables.get("_")))

        self.assertEqual("Text\n", scene.tables["_"][0]["s"])

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
        scene = Loader.read(content)
        self.assertIsInstance(scene, Loader.Scene)
        self.assertEqual(2, len(scene.tables.get("_")))

        self.assertEqual("Text\n", scene.tables["_"][0]["s"])
        self.assertEqual("Text\n", scene.tables["_"][1]["s"])
