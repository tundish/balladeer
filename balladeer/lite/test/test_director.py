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

import copy
import enum
import textwrap
import unittest
import tomllib

from speechmark import SpeechMark

from balladeer.lite.director import Director
from balladeer.lite.types import Entity
from balladeer.lite.types import State


class EditTests(unittest.TestCase):
    def test_word_counter(self):
        text = textwrap.dedent(
            """
        <STAFF.proposing#3> What will you have, sir? The special is fish today.

            1. Order the Beef Wellington
            2. Go for the Shepherd's Pie
            3. Try the Dover Sole
        """
        ).strip()
        sm = SpeechMark()
        html = sm.loads(text)

        director = Director(story=None)
        self.assertEqual(5, len(director.lines(html)))
        self.assertEqual(24, len(director.words(html)))

    def test_rewriter_single_blocks(self):
        text = textwrap.dedent(
            """
        <FIGHTER_1>

            I don't like the way you use me, {FIGHTER_2.name}!

        """
        ).strip()
        director = Director(story=None)
        selection = {
            "FIGHTER_1": Entity(name="Biffy"),
            "FIGHTER_2": Entity(name="Bashy"),
        }

        sm = SpeechMark()
        html = sm.loads(text)
        edit = director.edit(html, selection)
        self.assertIn('data-role="FIGHTER_1"', edit)
        self.assertIn('data-entity="Biffy"', edit, html)
        self.assertIn(">Biffy</cite>", edit)
        self.assertIn("Bashy!", edit)

    def test_edit_extended_characters_unescaped(self):
        text = textwrap.dedent(
            """
        <FIGHTER_1>

            I don't like the way you use me, {FIGHTER_2.name}!

        """
        ).strip()
        director = Director(story=None)
        selection = {
            "FIGHTER_1": Entity(name="Bîffy"),
            "FIGHTER_2": Entity(name="Båshy"),
        }

        sm = SpeechMark()
        html = sm.loads(text)
        edit = director.edit(html, selection)
        self.assertIn('data-role="FIGHTER_1"', edit)
        self.assertIn('data-entity="Bîffy"', edit)
        self.assertIn("B&icirc;ffy</cite>", edit)
        self.assertIn("Båshy!", edit)

    def test_edit_extended_characters_escaped(self):
        text = textwrap.dedent(
            """
        <FIGHTER_1>

            I don't like the way you use me, {FIGHTER_2.name!a}!

        """
        ).strip()
        director = Director(story=None)
        selection = {
            "FIGHTER_1": Entity(name="Bîffy"),
            "FIGHTER_2": Entity(name="Båshy"),
        }

        sm = SpeechMark()
        html = sm.loads(text)
        edit = director.edit(html, selection)
        self.assertIn('data-role="FIGHTER_1"', edit)
        self.assertIn('data-entity="Bîffy"', edit)
        self.assertIn("B&icirc;ffy</cite>", edit)
        self.assertIn("B&aring;shy!", edit)

    def test_edit_multiple_blocks(self):
        text = textwrap.dedent(
            """
        <WEAPON.attacking@FIGHTER_2:shouts/slapwhack>

            _Whack!_

        <FIGHTER_2>

            Uuurrggh!

        """
        ).strip()
        director = Director(story=None)
        selection = {
            "WEAPON": Entity(name="Rusty"),
            "FIGHTER_2": Entity(name="Bashy"),
        }

        sm = SpeechMark()
        html = sm.loads(text)
        edit = director.edit(html, selection)
        self.assertIn('data-role="WEAPON"', edit)
        self.assertIn('data-entity="Rusty"', edit, html)
        self.assertIn(">Rusty</cite>", edit)

        self.assertIn('data-role="FIGHTER_2"', edit)
        self.assertIn('data-entity="Bashy"', edit, html)
        self.assertIn(">Bashy</cite>", edit)


class ConditionTests(unittest.TestCase):
    # FIXME: Entities compare equal
    class Rain(Entity):
        pass

    class Sleet(Entity):
        pass

    class Snow(Entity):
        pass

    class Weather(State, enum.Enum):
        quiet = 0
        stormy = 1

    content = textwrap.dedent(
        """
        # Metadata at the top
        author = "tundish"

        [WEATHER]
        types   =   ["Rain", "Snow"]
        states.Weather = ["stormy"]

        [[_]]
        s="Outside."

        [[_]]
        # Intense
        if.WEATHER.state = "Weather.stormy"

        s="<WEATHER> It's stormy!"

        [[_]]
        # Hushed
        if.WEATHER.state = "Weather.quiet"

        s="<WEATHER> It's quiet."

        [[_]]
        # Snow storm
        if.WEATHER.type = "Snow"

        s="<WEATHER> Flurry, flurry."

        [[_]]
        # Rainfall
        if.WEATHER.type = "Rain"

        s="<WEATHER> Pitter patter."

        """
    ).strip()

    def setUp(self):
        self.ensemble = [
            self.Rain().set_state(self.Weather.stormy),
            self.Sleet().set_state(self.Weather.stormy),
            self.Snow().set_state(self.Weather.quiet),
        ]

    def test_condition_evaluation_one(self):
        d = Director(None)
        scene = tomllib.loads(self.content)
        conditions = [
            dict(d.specify_conditions(shot)) for shot in scene.get(d.shot_key)
        ]
        self.assertEqual(5, len(conditions))

        specs = d.specifications(scene)

        roles = dict(d.roles(specs, self.ensemble))
        self.assertTrue(d.allows(conditions[0], roles))
        self.assertTrue(d.allows(conditions[1], roles))
        self.assertFalse(d.allows(conditions[2], roles))
        self.assertFalse(d.allows(conditions[3], roles))
        self.assertTrue(d.allows(conditions[4], roles))

    def test_condition_evaluation_two(self):
        self.ensemble[0].set_state(self.Weather.quiet)
        self.ensemble[1].set_state(self.Weather.stormy)
        self.ensemble[2].set_state(self.Weather.stormy)

        d = Director(None)
        scene = tomllib.loads(self.content)
        conditions = [
            dict(d.specify_conditions(shot)) for shot in scene.get(d.shot_key)
        ]
        self.assertEqual(5, len(conditions))

        specs = d.specifications(scene)

        self.assertEqual(3, len(self.ensemble))
        roles = dict(d.roles(specs, self.ensemble))
        self.assertTrue(roles, (self.ensemble, specs))
        self.assertTrue(d.allows(conditions[0], roles))
        self.assertTrue(d.allows(conditions[1], roles))
        self.assertFalse(d.allows(conditions[2], roles))
        self.assertTrue(d.allows(conditions[3], roles))
        self.assertFalse(d.allows(conditions[4], roles))

    def test_guard_conditions_single_state(self):
        content = textwrap.dedent(
            """
        [[_]]
        if.WEATHER.state = "Weather.stormy"

        """
        ).strip()
        scene = tomllib.loads(content)
        director = Director(None)
        shot = next(iter(scene.get(director.shot_key)))
        conditions = dict(director.specify_conditions(shot))
        self.assertIn("WEATHER", conditions)
        roles, states, types = conditions["WEATHER"]
        self.assertIn("Weather", states)
        self.assertIn("stormy", states["Weather"])

    def test_guard_conditions_multiple_states(self):
        content = textwrap.dedent(
            """
        [[_]]
        if.WEATHER.states.Weather = ["stormy", "misty"]

        """
        ).strip()
        scene = tomllib.loads(content)
        director = Director(None)
        shot = next(iter(scene.get(director.shot_key)))
        conditions = dict(director.specify_conditions(shot))
        self.assertIn("WEATHER", conditions)
        roles, states, types = conditions["WEATHER"]
        self.assertIn("Weather", states)
        self.assertIn("stormy", states["Weather"])
        self.assertIn("misty", states["Weather"])


class RoleTests(unittest.TestCase):
    @enum.unique
    class Aggression(State, enum.Enum):
        calm = 0
        angry = 1

    @enum.unique
    class Contentment(State, enum.Enum):
        sad = 0
        happy = 1

    @enum.unique
    class Location(State, enum.Enum):
        pub = 0
        pub_bar = 1
        pub_carpark = 2
        pub_snug = 3
        pub_toilets = 4

    def setUp(self):
        self.ensemble = [
            Entity(name="Biffy", types={"Animal", "Canine"}),
            Entity(name="Bashy", types={"Animal", "Feline"}),
            Entity(name="Rusty", type="Weapon"),
        ]

    def test_rank_constraints(self):
        roles = {
            "A": {},
            "B": {
                "state": "Switched.on",
            },
            "C": {
                "states": {
                    "Switched": ["on", "off"],
                }
            },
            "D": {
                "states": {
                    "Switched": ["on"],
                    "Spinning": ["clockwise"],
                },
            },
            "E": {
                "state": "Switched.on",
                "type": "Torch",
            },
            "F": {
                "state": "Switched.on",
                "types": ["Torch", "Desklight"],
            },
            "G": {
                "state": "Switched.on",
                "types": ["Desklight"],
            },
            "H": {
                "state": "Switched.on",
                "types": ["Torch", "Desklight"],
                "roles": ["B", "D"],
            },
        }
        ranks = [0, 1, 0.5, 2, 2, 3, 2, 1]
        d = Director(None)
        for n, (k, v) in enumerate(roles.items()):
            with self.subTest(role=k, spec=v):
                rank = d.rank_constraints(v)
                self.assertEqual(ranks[n], rank, d.specify_role(v))

    def test_role_with_single_required_state(self):
        text = textwrap.dedent(
            """
        [FIGHTER_1]
        states.Aggression = ["angry"]

        [FIGHTER_2]
        state = "Contentment.sad"

        [WEAPON]
        # A weapon which makes a noise in use.
        """
        )
        entities = {i.name: i for i in self.ensemble}
        entities["Biffy"].set_state(RoleTests.Contentment.sad)
        self.assertEqual(
            RoleTests.Contentment.sad,
            entities["Biffy"].get_state(RoleTests.Contentment),
        )
        entities["Bashy"].set_state(RoleTests.Aggression.angry)
        self.assertEqual(
            RoleTests.Aggression.angry,
            entities["Bashy"].get_state(RoleTests.Aggression),
        )
        scene = tomllib.loads(text)
        self.assertIsInstance(scene, dict)

        director = Director(None)
        rv = dict(director.roles(scene, self.ensemble))
        self.assertEqual(3, len(rv), rv)
        self.assertEqual(entities["Bashy"], rv["FIGHTER_1"])
        self.assertEqual(entities["Biffy"], rv["FIGHTER_2"])
        self.assertEqual(entities["Rusty"], rv["WEAPON"])

    def test_role_with_multiple_states(self):
        text = textwrap.dedent(
            """
        [FIGHTER_1]
        states.Location = ["pub_bar", "pub_toilets"]

        [FIGHTER_2]
        state = "Location.pub_bar"

        [WEAPON]
        # A weapon which makes a noise in use.
        """
        ).strip()
        entities = {i.name: i for i in self.ensemble}
        entities["Biffy"].set_state(RoleTests.Location.pub_bar)
        self.assertEqual(
            RoleTests.Location.pub_bar, entities["Biffy"].get_state(RoleTests.Location)
        )
        entities["Bashy"].set_state(RoleTests.Location.pub_toilets)
        self.assertEqual(
            RoleTests.Location.pub_toilets,
            entities["Bashy"].get_state(RoleTests.Location),
        )

        scene = tomllib.loads(text)
        self.assertIsInstance(scene, dict)

        director = Director(None)
        rv = dict(director.roles(scene, self.ensemble))
        self.assertEqual(3, len(rv), rv)
        self.assertEqual(entities["Bashy"], rv["FIGHTER_1"])
        self.assertEqual(entities["Biffy"], rv["FIGHTER_2"])
        self.assertEqual(entities["Rusty"], rv["WEAPON"])

    def test_roles_not_greedy(self):
        text = textwrap.dedent(
            """
        [CHARACTER_1]
        roles = ["CHARACTER_2"]

        [CHARACTER_2]

        """
        ).strip()
        scene = tomllib.loads(text)
        self.assertIsInstance(scene, dict)

        entities = {i.name: i for i in self.ensemble}

        director = Director(None)
        rv = dict(director.roles(scene, self.ensemble))
        self.assertEqual(2, len(rv), rv)
        self.assertEqual(entities["Bashy"], rv["CHARACTER_1"])
        self.assertEqual(entities["Biffy"], rv["CHARACTER_2"])


class LoopTests(unittest.TestCase):
    def setUp(self):
        self.script = textwrap.dedent(
        """
        [GUEST]

        [[_]]
        s='''
        <GUEST#!>

            + This, or
            + This, or
            + This, or
        '''
        """
        ).strip()
        self.ensemble = [Entity()]

    def test_attr_matcher(self):
        text = '<cite data-role="GUEST" data-fragments="#!">'
        d = Director(story=None)
        attrs = dict(d.attributes(text))
        self.assertIn("role", attrs)
        self.assertEqual("GUEST", attrs["role"], attrs)
        self.assertEqual("#!", attrs["fragments"])

    def test_bang_loop(self):
        d = Director(story=None)

        scene = tomllib.loads(self.script)
        specs = d.specifications(scene)
        roles = dict(d.roles(specs, self.ensemble))

        shot = next(iter(scene.get(d.shot_key, [])))
        text = shot.get(d.dlg_key, "")

        sm = SpeechMark()
        html5 = sm.loads(text)

        rv = d.edit(html5, roles)
        m = d.attr_matcher.match(rv)
        print(m)
        self.assertEqual(1, rv.count("<li>"), rv)
        self.assertEqual(1, rv.count("</li>"))


@unittest.skip("not yet")
class DirectiveTests(unittest.TestCase):
    def test_directive_handling(self):
        """
        <PHONE.announcing@GUEST,STAFF> Ring riiing!
        """
        # TODO: Mock Drama methods.
