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


from collections import Counter
from collections import namedtuple
import re

from balladeer.lite.entity import Entity
from balladeer.lite.speech import Dialogue
from balladeer.lite.types import Turn


class SpeechTables:

    Tree = namedtuple("Tree", ["block", "roles", "tables", "shot_path", "menu"])

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tree = None
        self.ol_matcher = re.compile("<ol>.*?<\\/ol>", re.DOTALL | re.MULTILINE)
        self.li_matcher = re.compile("<li id=\"(\\d+)\">", re.DOTALL | re.MULTILINE)
        self.pp_matcher = re.compile("<p[^>]*?>(.*?)<\\/p>", re.DOTALL | re.MULTILINE)

    @staticmethod
    def follow_path(table, path: list):
        node = table
        for key in path:
            try:
                node = node[key]
            except KeyError:
                return
        else:
            return node

    @property
    def menu_options(self):
        try:
            return list(self.tree.menu.keys())
        except AttributeError:
            return []

    def get_option_mapping(self, block: str):
        list_block = self.ol_matcher.search(block)
        if list_block is None:
            return {}

        list_items = list(self.li_matcher.findall(list_block.group()))
        para_items = list(self.pp_matcher.findall(list_block.group()))
        return dict(
            {k: v for k, v in zip(para_items, list_items)},
            **{v: v for k, v in zip(para_items, list_items)}
        )

    def on_branching(self, entity: Entity, *args: tuple[Entity], **kwargs):
        identifier = kwargs.pop("identifier")
        path, shot_id, cue_index = identifier
        turn = Turn(**kwargs)
        _, block = turn.blocks[cue_index]
        menu = self.get_option_mapping(block)

        try:
            self.tree = self.tree._replace(block=block, menu=menu)
        except AttributeError:
            # Branching is initiated from a scene file.
            # So shot_id is the index into the shot sequence of the root of the tree.
            self.tree = self.Tree(
                block=block,
                roles=turn.roles,
                tables=turn.scene.tables,
                shot_path=["_", shot_id],
                menu=menu
            )

    def on_returning(self, entity: Entity, *args: tuple[Entity], **kwargs):
        if self in args:
            if len(self.tree.shot_path) > 2:
                self.tree.shot_path.pop(-1)
                shot = self.follow_path(self.tree.tables, self.tree.shot_path)
                text = shot.get("s", "")
                if text:
                    self.speech.append(Dialogue(text))
        else:
            self.tree = None

    def do_menu_option(self, this, text, director, *args, option: "menu_options", **kwargs):
        """
        {option}

        """
        key = self.tree.menu[option]
        shot = self.follow_path(
            self.tree.tables,
            self.tree.shot_path + [key]
        )

        if shot:
            conditions = dict(director.specify_conditions(shot))
            if director.allows(conditions, self.tree.roles):
                self.tree.shot_path.append(key)
                text = shot.get(director.dialogue_key, "")
                yield Dialogue(text)
