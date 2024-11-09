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
import textwrap
import unittest

from balladeer import Drama
from balladeer import Entity
from balladeer import Grouping
from balladeer import Loader
from balladeer import Prologue
from balladeer import SpeechTables
from balladeer import StoryBuilder
from balladeer import WorldBuilder


class InteractionTests(unittest.TestCase):

    class Interaction(SpeechTables, Drama):
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
                Entity(name="Beth", type="CatOwner"),
            ]

    scene_toml_text = textwrap.dedent("""
    [ALAN]
    type = "Narrator"

    [BETH]
    type = "CatOwner"

    [INTERACTION]
    type = "Interaction"

    [[_]]
    if.INTERACTION.state = 0
    if.INTERACTION.tree = false
    s='''
    <ALAN> What shall we do?
    '''

    [[_]]
    if.INTERACTION.state = 1
    if.INTERACTION.tree = false
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
    <BETH.branching> I've got three lovely cats.
        1. *Ask about Charlie*
        2. `Ask about Doodles`
        3. _Ask about Elektra_
    '''

    [_.2.1]
    s='''
    <BETH.returning@INTERACTION> Charlie is the elder cat. He's a Marmalade. Very laid back.
    '''

    [_.2.2]
    s='''
    <BETH.returning@INTERACTION> Oh my goodness, Doodles. Always up to mischief!
    '''

    [_.2.3]
    s='''
    <BETH.returning@INTERACTION> The thing about Elektra is, she's always somewhere else.
    '''

    [_.3]
    s='''
    <BETH> I don't know anything about football at all.
    '''

    [[_]]
    if.INTERACTION.state = 3
    if.INTERACTION.tree = false
    s='''
    <ALAN> OK. Interaction over.
    '''
    """)


    def setUp(self):
        scene_toml = Loader.read_toml(self.scene_toml_text)
        assets = Grouping.typewise([Loader.Scene(self.scene_toml_text, scene_toml, None, None, None)])
        world = self.World()
        self.story = StoryBuilder(assets=assets, world=world)
        self.story.drama = [self.Interaction(world=world)]
        self.assertIsInstance(self.story.context, self.Interaction)

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
                    elif n == 4:
                        action = self.story.action("1")
                        self.assertIsNone(action)
                        self.assertEqual(1, self.story.context.witness["branching"])
                        self.assertIsNone(self.story.context.tree)

                        self.assertEqual(1, len(turn.blocks), turn.blocks)
                        self.assertIn("Interaction over", turn.blocks[0][1])

    def test_single_branch(self):
        n_turns = 5
        for n in range(n_turns):
            with self.story.turn() as turn:
                with self.subTest(n=n):
                    self.story.context.state = n
                    options = self.story.context.options(self.story.context.ensemble)
                    if n == 0:
                        action = self.story.action("1")
                        self.assertEqual(0, self.story.context.witness["branching"])
                        self.assertIsNone(self.story.context.tree)
                        self.assertIsNone(action)
                    if n == 1:
                        action = self.story.action("1")
                        self.assertEqual(0, self.story.context.witness["branching"])
                        self.assertIsNone(self.story.context.tree)
                        self.assertIsNone(action)
                    elif n == 2:
                        action = self.story.action("1")
                        fn, args, kwargs = action
                        self.assertEqual({"option": "1"}, kwargs)
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
                        action = self.story.action("1")
                        self.assertIsNone(action)
                        self.assertEqual({"option": "1"}, kwargs)
                        self.assertEqual(1, self.story.context.witness["branching"])
                        self.assertIsNone(self.story.context.tree)

                        self.assertEqual(2, len(turn.blocks), turn.blocks)
                        shot_id, block = turn.blocks[0]
                        self.assertIn("you never know", block)
                    elif n == 4:
                        action = self.story.action("1")
                        self.assertIsNone(action)
                        self.assertEqual(1, self.story.context.witness["branching"])
                        self.assertIsNone(self.story.context.tree)

                        self.assertEqual(1, len(turn.blocks), turn.blocks)
                        self.assertIn("Interaction over", turn.blocks[0][1])

    def test_double_branch_with_returning(self):
        n_turns = 9
        for n in range(n_turns):
            with self.story.turn() as turn:
                with self.subTest(n=n):
                    self.story.context.state = n
                    options = self.story.context.options(self.story.context.ensemble)
                    if n == 0:
                        action = self.story.action("2")
                        self.assertEqual(0, self.story.context.witness["branching"])
                        self.assertIsNone(self.story.context.tree)
                        self.assertIsNone(action)
                    if n == 1:
                        action = self.story.action("2")
                        self.assertEqual(0, self.story.context.witness["branching"])
                        self.assertIsNone(self.story.context.tree)
                        self.assertIsNone(action)
                    elif n == 2:
                        action = self.story.action("2")
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
                        action = self.story.action("2")
                        fn, args, kwargs = action
                        self.assertEqual({"option": "2"}, kwargs)
                        self.assertEqual(2, self.story.context.witness["branching"])
                        self.assertTrue(self.story.context.tree)

                        self.assertEqual(1, len(turn.blocks), turn.blocks)
                        shot_id, block = turn.blocks[0]
                        self.assertIn("three lovely cats", block)
                        self.assertIn("<code>Ask about Doodles</code>", block)
                        self.assertFalse(any("<code>" in i for i in options), options)
                    elif n == 4:
                        action = self.story.action("2")
                        fn, args, kwargs = action
                        self.assertEqual({"option": "2"}, kwargs)
                        self.assertEqual(2, self.story.context.witness["branching"])
                        self.assertTrue(self.story.context.tree)

                        self.assertEqual(1, len(turn.blocks), turn.blocks)
                        shot_id, block = turn.blocks[0]
                        self.assertIn("Doodles. Always up to mischief!", block)
                    elif n == 5:
                        action = self.story.action("3")
                        fn, args, kwargs = action
                        self.assertEqual({"option": "3"}, kwargs)
                        self.assertEqual(3, self.story.context.witness["branching"])
                        self.assertTrue(self.story.context.tree)
                        self.assertEqual(2, len(turn.blocks), turn)
                        self.assertIn("three lovely cats", turn.blocks[0][1])
                        self.assertIn("<strong>Ask about Elektra</strong>", turn.blocks[0][1])
                        self.assertFalse(any("<strong>" in i for i in options), options)
                    elif n == 6:
                        action = self.story.action("1")
                        fn, args, kwargs = action
                        self.assertEqual({"option": "1"}, kwargs)
                        self.assertEqual(4, self.story.context.witness["branching"])
                        self.assertTrue(self.story.context.tree)
                        self.assertEqual(2, len(turn.blocks), turn.blocks)
                        self.assertIn("The thing about Elektra", turn.blocks[1][1])
                    elif n == 7:
                        action = self.story.action("1")
                        fn, args, kwargs = action
                        self.assertEqual({"option": "1"}, kwargs)
                        self.assertEqual(5, self.story.context.witness["branching"])
                        self.assertTrue(self.story.context.tree)
                        self.assertEqual(2, len(turn.blocks), turn.blocks)
                        self.assertIn("three lovely cats", turn.blocks[0][1])
                        self.assertIn("<em>Ask about Charlie</em>", turn.blocks[0][1])
                        self.assertFalse(any("<em>" in i for i in options), options)
                    elif n == 8:
                        action = self.story.action("1")
                        fn, args, kwargs = action
                        self.assertEqual({"option": "1"}, kwargs)
                        self.assertEqual(6, self.story.context.witness["branching"])
                        self.assertTrue(self.story.context.tree)
                        self.assertEqual(2, len(turn.blocks), turn.blocks)
                        self.assertIn("Charlie is the elder", turn.blocks[1][1])

    def test_generated_prologue(self):
        n_turns = 4
        for n in range(n_turns):
            drama = self.story.context
            drama.speech.append(Prologue(f"<>Turn number {n}"))
            with self.story.turn() as turn:
                self.story.context.state = n
                options = self.story.context.options(self.story.context.ensemble)
                with self.subTest(n=n):
                    if n == 0:
                        shot_id, block = turn.blocks[0]
                        self.assertIn("Turn number 0", block)
                        shot_id, block = turn.blocks[1]
                        self.assertIn("What shall we do?", block)
                        self.assertEqual(0, self.story.context.witness["branching"])
                        self.assertIsNone(self.story.context.tree)
                    if n == 1:
                        shot_id, block = turn.blocks[0]
                        self.assertIn("Turn number 1", block)
                        shot_id, block = turn.blocks[1]
                        self.assertIn("What shall we do?", block)
                        self.assertEqual(0, self.story.context.witness["branching"])
                        self.assertIsNone(self.story.context.tree)
                    elif n == 2:
                        shot_id, block = turn.blocks[0]
                        self.assertIn("Turn number 2", block)
                        self.assertEqual(4, len(turn.blocks), turn.blocks)
                        self.assertIn("Let's practise", turn.blocks[1][1])
                        shot_id, block = turn.blocks[2]
                        self.assertIn("a good time to ask", block)

                        self.assertEqual(1, self.story.context.witness["branching"])
                        self.assertTrue(self.story.context.tree)
                        menu = self.story.context.tree.menu
                        self.assertTrue({str(i) for i in range(1, 4)}.issubset(set(menu.keys())), menu)
                        self.assertIn("Ask about football", menu)

                        self.assertIn("I'll let you carry on", turn.blocks[3][1])
                    elif n == 3:
                        self.assertEqual(1, self.story.context.witness["branching"])
                        self.assertTrue(self.story.context.tree)
                        menu = self.story.context.tree.menu
                    elif n == 4:
                        action = self.story.action("1")
                        self.assertIsNone(action)
                        self.assertEqual(1, self.story.context.witness["branching"])
                        self.assertIsNone(self.story.context.tree)

                        self.assertEqual(1, len(turn.blocks), turn.blocks)
                        self.assertIn("Interaction over", turn.blocks[0][1])

    def test_generated_prologue_twice(self):
        n_turns = 4
        for n in range(n_turns):
            drama = self.story.context
            drama.speech.append(Prologue(f"<>Turn number {n}"))
            drama.speech.append(Prologue(f"<>Second Prologue object"))
            with self.story.turn() as turn:
                self.story.context.state = n
                options = self.story.context.options(self.story.context.ensemble)
                with self.subTest(n=n):
                    if n == 0:
                        shot_id, block = turn.blocks[0]
                        self.assertIn("Turn number 0", block)
                        shot_id, block = turn.blocks[1]
                        self.assertIn("Second Prologue", block)
                        shot_id, block = turn.blocks[2]
                        self.assertIn("What shall we do?", block)
                        self.assertEqual(0, self.story.context.witness["branching"])
                        self.assertIsNone(self.story.context.tree)
                    if n == 1:
                        shot_id, block = turn.blocks[0]
                        self.assertIn("Turn number 1", block)
                        shot_id, block = turn.blocks[1]
                        self.assertIn("Second Prologue", block)
                        shot_id, block = turn.blocks[2]
                        self.assertIn("What shall we do?", block)
                        self.assertEqual(0, self.story.context.witness["branching"])
                        self.assertIsNone(self.story.context.tree)
                    elif n == 2:
                        shot_id, block = turn.blocks[0]
                        self.assertIn("Turn number 2", block)
                        shot_id, block = turn.blocks[1]
                        self.assertIn("Second Prologue", block)
                        shot_id, block = turn.blocks[2]
                        self.assertEqual(5, len(turn.blocks), turn.blocks)
                        self.assertIn("Let's practise", block)
                        shot_id, block = turn.blocks[3]
                        self.assertIn("a good time to ask", block)

                        self.assertEqual(1, self.story.context.witness["branching"])
                        self.assertTrue(self.story.context.tree)
                        menu = self.story.context.tree.menu
                        self.assertTrue({str(i) for i in range(1, 4)}.issubset(set(menu.keys())), menu)
                        self.assertIn("Ask about football", menu)

                        self.assertIn("I'll let you carry on", turn.blocks[4][1])
                    elif n == 3:
                        self.assertEqual(1, self.story.context.witness["branching"])
                        self.assertTrue(self.story.context.tree)
                        menu = self.story.context.tree.menu
                    elif n == 4:
                        action = self.story.action("1")
                        self.assertIsNone(action)
                        self.assertEqual(1, self.story.context.witness["branching"])
                        self.assertIsNone(self.story.context.tree)

                        self.assertEqual(1, len(turn.blocks), turn.blocks)
                        self.assertIn("Interaction over", turn.blocks[0][1])

    def test_generated_prologue_multiple_cues(self):
        n_turns = 4
        for n in range(n_turns):
            drama = self.story.context
            drama.speech.append(Prologue(f"<>Turn number {n}\n<>Second cue"))
            with self.story.turn() as turn:
                self.story.context.state = n
                options = self.story.context.options(self.story.context.ensemble)
                with self.subTest(n=n):
                    if n == 0:
                        shot_id, block = turn.blocks[0]
                        self.assertIn("Turn number 0", block)
                        shot_id, block = turn.blocks[1]
                        self.assertIn("Second cue", block)
                        shot_id, block = turn.blocks[2]
                        self.assertIn("What shall we do?", block)
                        self.assertEqual(0, self.story.context.witness["branching"])
                        self.assertIsNone(self.story.context.tree)
                    if n == 1:
                        shot_id, block = turn.blocks[0]
                        self.assertIn("Turn number 1", block)
                        shot_id, block = turn.blocks[1]
                        self.assertIn("Second cue", block)
                        shot_id, block = turn.blocks[2]
                        self.assertIn("What shall we do?", block)
                        self.assertEqual(0, self.story.context.witness["branching"])
                        self.assertIsNone(self.story.context.tree)
                    elif n == 2:
                        shot_id, block = turn.blocks[0]
                        self.assertIn("Turn number 2", block)
                        shot_id, block = turn.blocks[1]
                        self.assertIn("Second cue", block)
                        shot_id, block = turn.blocks[2]
                        self.assertEqual(5, len(turn.blocks), turn.blocks)
                        self.assertIn("Let's practise", block)
                        shot_id, block = turn.blocks[3]
                        self.assertIn("a good time to ask", block)

                        self.assertEqual(1, self.story.context.witness["branching"])
                        self.assertTrue(self.story.context.tree)
                        menu = self.story.context.tree.menu
                        self.assertTrue({str(i) for i in range(1, 4)}.issubset(set(menu.keys())), menu)
                        self.assertIn("Ask about football", menu)

                        self.assertIn("I'll let you carry on", turn.blocks[4][1])
                    elif n == 3:
                        self.assertEqual(1, self.story.context.witness["branching"])
                        self.assertTrue(self.story.context.tree)
                        menu = self.story.context.tree.menu
                    elif n == 4:
                        action = self.story.action("1")
                        self.assertIsNone(action)
                        self.assertEqual(1, self.story.context.witness["branching"])
                        self.assertIsNone(self.story.context.tree)

                        self.assertEqual(1, len(turn.blocks), turn.blocks)
                        self.assertIn("Interaction over", turn.blocks[0][1])

