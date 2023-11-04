#!/usr/bin/env python
# encoding: utf8

# Copyright 2023 D E Haynes

# This file is part of rotu.
# 
# Rotu is free software: you can redistribute it and/or modify it under the terms of the
# GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License,
# or (at your option) any later version.
# 
# Rotu is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU Affero General Public License for more details.
# 
# You should have received a copy of the GNU Affero General Public License along with Rotu.
# If not, see <https://www.gnu.org/licenses/>.

from collections import Counter
from collections import namedtuple
import pprint
import re
import textwrap
import tomllib
import unittest

from balladeer import Dialogue
from balladeer import Drama
from balladeer import Entity
from balladeer import Grouping
from balladeer import Loader
from balladeer import StoryBuilder
from balladeer import WorldBuilder

from speechmark import SpeechMark


class SpeechTables:

    Tree = namedtuple("Tree", ["block", "roles", "tables", "shot_path", "menu"])

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tree = None
        self.ol_matcher = re.compile("<ol>.*?<\\/ol>", re.DOTALL | re.MULTILINE)
        self.li_matcher = re.compile("<li id=\"(\\d+)\">", re.DOTALL | re.MULTILINE)
        self.pp_matcher = re.compile("<p[^>]*?>(.*?)<\\/p>", re.DOTALL)

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

    def get_option_map(self, block: str):
        list_block = self.ol_matcher.search(block)
        list_items = list(self.li_matcher.findall(list_block.group()))
        para_items = list(self.pp_matcher.findall(list_block.group()))
        return dict(
            {k: v for k, v in zip(para_items, list_items)},
            **{v: v for k, v in zip(para_items, list_items)}
        )

    def on_branching(self, entity: Entity, *args: tuple[Entity], **kwargs):
        identifier = kwargs.pop("identifier")
        path, shot_id, cue_index = identifier
        turn = StoryBuilder.Turn(**kwargs)
        _, block = turn.blocks[cue_index]
        menu = self.get_option_map(block)

        try:
            shots = self.follow_path(self.tree.tables, self.tree.shot_path)
            print(f"shots: {shots}")
        except AttributeError:
            # Branching is initiated from a scene file.
            # So shot_id can be used as an index into the shot sequence.
            self.tree = self.Tree(
                block=block,
                roles=turn.roles,
                tables=turn.scene.tables,
                shot_path=["_", shot_id],
                menu=menu
            )

    def on_returning(self, entity: Entity, *args: tuple[Entity], **kwargs):
        if self in args:
            self.tree.shot_path.pop(-1)
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
                print(f"text: {text}")
                yield Dialogue(text)


class ConversationTests(unittest.TestCase):

    class Conversation(SpeechTables, Drama):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.state = 0
            self.witness = Counter()

        def on_branching(self, entity: Entity, *args: tuple[Entity], **kwargs):
            self.witness["branching"] += 1
            super().on_branching(entity, *args, **kwargs)

        def on_returning(self, entity: Entity, *args: tuple[Entity], **kwargs):
            self.witness["returning"] += 1
            super().on_returning(entity, *args, **kwargs)

    class World(WorldBuilder):
        def build(self):
            yield from [
                Entity(name="Alan", type="Narrator"),
                Entity(name="Beth", type="Gossiper"),
            ]

    scene_toml_text = textwrap.dedent("""
    [ALAN]
    type = "Narrator"

    [BETH]
    type = "Gossiper"

    [CONVERSATION]
    type = "Conversation"

    [[_]]
    if.CONVERSATION.state = 0
    if.CONVERSATION.tree = false
    s='''
    <ALAN> What shall we do?
    '''

    [[_]]
    if.CONVERSATION.state = 1
    if.CONVERSATION.tree = false
    s='''
    <ALAN> Let's practise our conversation skills.
    <ALAN.branching> Maybe now's a good time to ask {BETH.name} a question.
        1. Ask about the weather
        2. Ask about pets
        3. Ask about football
    <ALAN> I'll let you carry on for a bit.
    '''

    [_.1]
    s='''
    <BETH> Well, you never know what's it's going to do next, do you?
    <BETH.returning> I've never seen anything like it!
    '''

    [_.2]
    s='''
    <BETH.branching> I've got two lovely cats.
        1. Ask about Charlie
        2. Ask about Doodles
    '''

    [_.2.1]
    s='''
    <BETH> Charlie is the elder cat. He's a Marmalade. Very laid back.
    '''

    [_.3]
    s='''
    <BETH> I don't know anything about football at all.
    '''

    [_.2.2]
    s='''
    <BETH> Oh my goodness, Doodles. Always up to mischief!
    '''

    [[_]]
    if.CONVERSATION.state = 2
    if.CONVERSATION.tree = false
    s='''
    <ALAN> OK. Conversation over.
    '''
    """)


    def setUp(self):
        scene_toml = Loader.read_toml(self.scene_toml_text)
        pprint.pprint(scene_toml)
        assets = Grouping.typewise([Loader.Scene(self.scene_toml_text, scene_toml, None, None, None)])
        world = self.World()
        self.story = StoryBuilder(assets=assets, world=world)
        self.story.drama = [self.Conversation(world=world)]
        self.assertIsInstance(self.story.context, self.Conversation)

    def test_no_command(self):
        n_turns = 4
        for n in range(n_turns):
            with self.story.turn() as turn:
                self.story.context.state = n
                options = self.story.context.options(self.story.context.ensemble)
                with self.subTest(n=n):
                    if n == 0:
                        shot_id, block = turn.blocks[0]
                        self.assertIn("What shall we do?", block)
                        self.assertEqual(0, self.story.context.witness["branching"])
                        self.assertIsNone(self.story.context.tree)
                    if n == 1:
                        shot_id, block = turn.blocks[0]
                        self.assertIn("What shall we do?", block)
                        self.assertEqual(0, self.story.context.witness["branching"])
                        self.assertIsNone(self.story.context.tree)
                    elif n == 2:
                        self.assertEqual(3, len(turn.blocks), turn.blocks)
                        self.assertIn("Let's practise", turn.blocks[0][1])
                        self.assertIn("I'll let you carry on", turn.blocks[2][1])
                        shot_id, block = turn.blocks[1]
                        self.assertIn("a good time to ask", block)

                        self.assertEqual(1, self.story.context.witness["branching"])
                        self.assertTrue(self.story.context.tree)
                        menu = self.story.context.tree.menu
                        self.assertTrue({str(i) for i in range(1, 4)}.issubset(set(menu.keys())))
                        self.assertIn("Ask about football", menu)
                    elif n == 3:
                        self.assertEqual(1, self.story.context.witness["branching"])
                        self.assertTrue(self.story.context.tree)
                        self.assertFalse(turn.blocks)

    def test_double_branch(self):
        n_turns = 5
        for n in range(n_turns):
            with self.story.turn() as turn:
                with self.subTest(n=n):
                    self.story.context.state = n
                    options = self.story.context.options(self.story.context.ensemble)
                    action = self.story.action("2")
                    if n == 0:
                        self.assertEqual(0, self.story.context.witness["branching"])
                        self.assertIsNone(self.story.context.tree)
                        self.assertIsNone(action)
                    if n == 1:
                        self.assertEqual(0, self.story.context.witness["branching"])
                        self.assertIsNone(self.story.context.tree)
                        self.assertIsNone(action)
                    elif n == 2:
                        fn, args, kwargs = action
                        self.assertEqual({"option": "2"}, kwargs)
                        self.assertEqual(1, self.story.context.witness["branching"])
                        self.assertTrue(self.story.context.tree)
                        self.assertEqual(3, len(turn.blocks), turn.blocks)
                        self.assertIn("Let's practise", turn.blocks[0][1])
                        self.assertIn("I'll let you carry on", turn.blocks[2][1])
                        shot_id, block = turn.blocks[1]
                        self.assertIn("a good time to ask", block)

                        self.assertEqual(1, self.story.context.witness["branching"])
                        self.assertTrue(self.story.context.tree)
                        menu = self.story.context.tree.menu
                        self.assertTrue({str(i) for i in range(1, 4)}.issubset(set(menu.keys())))
                        self.assertIn("Ask about football", menu)
                    elif n == 3:
                        fn, args, kwargs = action
                        self.assertEqual({"option": "2"}, kwargs)
                        self.assertEqual(2, self.story.context.witness["branching"])
                        self.assertTrue(self.story.context.tree)

                        self.assertEqual(1, len(turn.blocks), turn.blocks)
                        shot_id, block = turn.blocks[0]
                        self.assertIn("two lovely cats", block)
                    elif n == 4:
                        fn, args, kwargs = action
                        self.assertEqual({"option": "2"}, kwargs)
                        self.assertEqual(2, self.story.context.witness["branching"])
                        self.assertTrue(self.story.context.tree)

                        self.assertEqual(1, len(turn.blocks), turn.blocks)
                        shot_id, block = turn.blocks[0]
                        self.assertIn("Doodles. Always up to mischief!", block)
