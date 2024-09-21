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
from collections import deque
import copy
import itertools
import textwrap
import tomllib
import unittest

from balladeer.examples.ex_10_animate_media.main import Story as Story_10
from balladeer.examples.ex_10_animate_media.main import World as World_10
from balladeer.lite.compass import MapBuilder
from balladeer.lite.compass import Transit
from balladeer.lite.drama import Drama
from balladeer.lite.entity import Entity
from balladeer.lite.loader import Loader
from balladeer.lite.speech import Dialogue
from balladeer.lite.storybuilder import StoryBuilder
from balladeer.lite.types import Grouping
from balladeer.lite.types import Page
from balladeer.lite.world import WorldBuilder


class StoryTests(unittest.TestCase):

    def tearDown(self):
        themes = [i for i in Page.themes.keys() if i != "default"]
        for theme in themes:
            del Page.themes[theme]

    def test_simple_turns(self):
        story = StoryBuilder(
            Dialogue("<> Knock, knock."),
            Dialogue("<> Who's there?"),
        )
        self.assertIsInstance(story.context.speech, deque)
        for n in range(3):
            with self.subTest(n=n), story.turn() as turn:
                if n < 2:
                    self.assertTrue(turn.blocks, turn)
                else:
                    self.assertFalse(turn.blocks, turn)

    def test_story_copy_drama(self):
        a = StoryBuilder(
            Dialogue("<> Knock, knock."),
            Dialogue("<> Who's there?"),
        )
        b = copy.deepcopy(a)
        self.assertNotEqual(a.uid, b.uid, vars(a))
        self.assertNotEqual(a.director, b.director, vars(a.director))

        # Side effect: each drama generates its active set
        self.assertTrue([i.options([]) for i in a.drama])
        self.assertTrue([i.options([]) for i in b.drama])

        for drama in a.drama:
            with self.subTest(a=a, b=b, drama=drama):
                self.assertNotIn(drama, b.drama)
                self.assertFalse(
                    any(set(drama.active).intersection(set(i.active)) for i in b.drama)
                )

        for a_d, b_d in zip(a.drama, b.drama):
            with self.subTest(a_d=a_d, b_d=b_d):
                self.assertNotEqual(a_d.uid, b_d.uid)

    def test_story_copy_map(self):
        witness = dict()

        class Map(MapBuilder):
            def build(self):
                nonlocal witness
                witness[self] = True
                yield Transit().set_state(self.exit.a, self.into.b)
                yield Transit().set_state(self.exit.b, self.into.a)

        class World(WorldBuilder):
            def build(self):
                nonlocal witness
                witness[self] = bool(self.map)
                yield Entity()
                yield Entity()
                yield Entity()

        class Story(StoryBuilder):
            def build(self):
                nonlocal witness
                witness[self] = bool(self.world.map)
                yield Drama()

        spots = {
            "a": ["A", "a"],
            "b": ["B", "b"],
        }
        m = Map(spots)
        w = World(map=m)
        a = Story(world=w)
        b = copy.deepcopy(a)

        self.assertEqual(3, len(a.world.entities))
        for entity in a.world.entities:
            with self.subTest(a=a, b=b, entity=entity):
                self.assertFalse(any(entity.names is i.names for i in b.world.entities))
                self.assertFalse(any(entity.states is i.states for i in b.world.entities))
                self.assertFalse(any(entity.types is i.types for i in b.world.entities))

        self.assertTrue(a.world.map)
        self.assertTrue(b.world.map)
        self.assertIs(a.world.map.spot, b.world.map.spot)
        self.assertIs(a.world.map.exit, b.world.map.exit)
        self.assertIs(a.world.map.into, b.world.map.into)
        self.assertIs(a.world.map.home, b.world.map.home)

        for transit in a.world.map.transits:
            with self.subTest(a=a, b=b, transit=transit):
                self.assertFalse(any(transit.names is i.names for i in b.world.map.transits))
                self.assertFalse(any(transit.states is i.states for i in b.world.map.transits))
                self.assertFalse(any(transit.types is i.types for i in b.world.map.transits))

        self.assertEqual(6, len(witness), witness)
        self.assertTrue(all(witness.values()), witness)

    def test_theme(self):
        page = Page()
        page.themes["a"] = {"ink": {}}
        page.themes["b"] = {"ink": {"gravity": "blue"}}
        page.themes["c"] = {"ink": {"gravity": "crimson"}}
        story = StoryBuilder(
            Dialogue("<?theme=b&theme=a> Knock, knock."),
            Dialogue("<?theme=b&theme=c> Who's there?"),
        )
        for n in range(2):
            with self.subTest(n=n, m=len(story.director.notes[(None, 0)].maps)):
                with story.turn() as turn:
                    theme_spec = list(story.director.notes.values())[-1].get("theme")
                    self.assertIsInstance(theme_spec, list)
                    settings = story.settings(*theme_spec, themes=page.themes)
                    self.assertIsInstance(settings, dict)
                    self.assertTrue(settings)
                    self.assertIn("ink", settings)
                    self.assertTrue(
                        set(settings["ink"]).issubset(
                            {
                                "gravity", "shadows",
                                "lolight", "midtone",
                                "hilight", "washout",
                                "glamour"
                            }
                        )
                    )
                    if n == 0:
                        self.assertEqual("blue", settings["ink"]["gravity"])
                    else:
                        self.assertEqual("crimson", settings["ink"]["gravity"])


class ExampleTests(unittest.TestCase):
    def test_cartoon_fight(self):
        content = textwrap.dedent('''
            [FIGHTER_1]
            state = 1

            [FIGHTER_2]
            type = "Animal"
            state = 1

            [WEAPON]
            type = "Weapon"
            roles = ["FIGHTER_1"]
            state = 1

            [[_]]

            s="""
            <FIGHTER_1>

                I don't like the way you use me, {FIGHTER_2.name}!

            <WEAPON.attacking@FIGHTER_2:shouts/slapwhack?offer=1>

                _Whack!_

            <FIGHTER_2?offer=1>

                Uuurrggh!
            """

            ''').strip()

        scene = Loader.Scene(content, Loader.read_toml(content))
        story = Story_10(config={}, assets=Grouping.typewise([scene]), world=World_10())
        specs = story.director.specifications(scene.tables)
        self.assertEqual(story.director.rank_constraints(specs["FIGHTER_1"]), 1, specs)
        self.assertEqual(story.director.rank_constraints(specs["FIGHTER_2"]), 2, specs)
        self.assertEqual(story.director.rank_constraints(specs["WEAPON"]), 3, specs)

        for n in range(3):
            with self.subTest(n=n, m=len(story.director.notes[(None, 0)].maps)):
                notes = story.director.notes[(None, 0)]

                with story.turn() as turn:
                    roles = dict(story.director.roles(specs, story.context.ensemble))
                    if not n:
                        self.assertTrue(turn.blocks, notes)
                        self.assertEqual(3, len(roles), roles)
                    elif n == 1:
                        self.assertTrue(turn.blocks, notes)
                        self.assertEqual(2, len(roles), roles)
                        rewriter = story.director.rewrite(scene, roles)
                        self.assertRaises(KeyError, list, rewriter)
                    elif n == 2:
                        self.assertFalse(turn.blocks, notes)


class ConversationExample:

    scene_toml_text = textwrap.dedent("""
    [ALAN]
    type = "Narrator"

    [BETH]
    type = "Gossiper"

    [CONVERSATION]
    type = "Conversation"

    [[_]]
    s='''
    <ALAN.testing> Let's practise our conversation skills.
    '''

    [[_]]
    # if.CONVERSATION.tree = false
    s='''
    <ALAN.branching> Maybe now's a good time to ask {BETH.name} a question.
        1. Talk about the weather
        2. Mention the football
        3. Ask after the family
    '''

    [[_.1]]
    s='''
    <BETH> Well, you never know what's it's going to do next, do you?
    '''

    [[_.2]]
    s='''
    <BETH.branching> I've got two lovely cats.
        1. Ask about Charlie
        2. Ask about Doodles
    '''

    [[_.2.1]]
    s='''
    <BETH> Charlie is the elder cat. He's a Marmalade. Very laid back.
    '''

    [[_.3]]
    s='''
    <BETH> I don't know anything about football at all.
    '''

    [[_.2.2]]
    s='''
    <BETH> Oh my goodness, Doodles. Always up to mischief!
    '''

    [[_]]
    s='''
    <ALAN> OK. Conversation over.
    '''
    """)

    class Conversation(Drama):

        def __init__(self, *args, config=None, world=None, **kwargs):
            super().__init__(*args, config=config, world=world, **kwargs)
            self.witness = Counter()

        def on_testing(self, entity: Entity, *args: tuple[Entity], **kwargs):
            self.witness["testing"] += 1

        def on_branching(self, entity: Entity, *args: tuple[Entity], **kwargs):
            self.witness["branching"] += 1

    class World(WorldBuilder):
        def build(self):
            yield from [
                Entity(name="Alan", type="Narrator"),
                Entity(name="Beth", type="Gossiper"),
            ]


class ConversationTests(ConversationExample, unittest.TestCase):
    def setUp(self):
        scene_toml = Loader.read_toml(self.scene_toml_text)
        assets = Grouping.typewise([Loader.Scene(self.scene_toml_text, scene_toml, None, None, None)])
        world = self.World()
        self.story = StoryBuilder(assets=assets, world=world)
        self.story.drama = [self.Conversation(world=world)]
        self.assertIsInstance(self.story.context, self.Conversation)

    def test_directives(self):
        for i in range(4):
            with self.story.turn() as turn:
                for n, block in turn.blocks:
                    if n == 0:
                        self.assertIn("conversation skills", block)
                    elif n == 1:
                        self.assertIn("the football", block)

        self.assertEqual(4, self.story.context.witness["testing"])
        self.assertEqual(4, self.story.context.witness["branching"])
