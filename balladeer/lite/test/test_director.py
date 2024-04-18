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

from balladeer.lite.director import Director
from balladeer.lite.entity import Entity
from balladeer.lite.speech import Speech
from balladeer.lite.speech import Prologue
from balladeer.lite.speech import Dialogue
from balladeer.lite.speech import Epilogue
from balladeer.lite.types import State


class EditTests(unittest.TestCase):
    def test_word_counter(self):
        text = textwrap.dedent("""
        <STAFF.proposing#3> What will you have, sir? The special is fish today.

            1. Order the Beef Wellington
            2. Go for the Shepherd's Pie
            3. Try the Dover Sole
        """).strip()
        speech = Speech(text)

        director = Director()
        self.assertEqual(5, len(speech.lines))
        self.assertEqual(24, len(speech.words))

        rv = "\n".join(director.edit(speech))
        self.assertFalse("<p>\n\n</p>" in rv, rv)

    def test_animate_cite_tag(self):
        text = textwrap.dedent("""
        <FIGHTER_1>

            I don't like the way you use me, {FIGHTER_2.name}!

        """).strip()
        director = Director()
        selection = {
            "FIGHTER_1": Entity(name="Biffy"),
            "FIGHTER_2": Entity(name="Bashy"),
        }

        speech = Speech(text)
        edit = "\n".join(director.edit(speech, selection))
        match = director.cite_matcher.search(edit)
        self.assertTrue(match)
        self.assertIn("animation-delay", match.group())
        self.assertIn("animation-duration", match.group())

    def test_edit_single_blocks(self):
        text = textwrap.dedent("""
        <FIGHTER_1>

            I don't like the way you use me, {FIGHTER_2.name}!

        """).strip()
        director = Director()
        selection = {
            "FIGHTER_1": Entity(name="Biffy"),
            "FIGHTER_2": Entity(name="Bashy"),
        }

        speech = Speech(text)
        edit = "\n".join(director.edit(speech, selection))
        self.assertIn('data-role="FIGHTER_1"', edit)
        self.assertIn('data-entity="Biffy"', edit, speech)
        self.assertIn(">Biffy</cite>", edit)
        self.assertIn("Bashy!", edit)

    def test_edit_extended_characters_unescaped(self):
        text = textwrap.dedent("""
        <FIGHTER_1>

            I don't like the way you use me, {FIGHTER_2.name}!

        """).strip()
        director = Director()
        selection = {
            "FIGHTER_1": Entity(name="Bîffy"),
            "FIGHTER_2": Entity(name="Båshy"),
        }

        speech = Speech(text)
        edit = "\n".join(director.edit(speech, selection))
        self.assertIn('data-role="FIGHTER_1"', edit)
        self.assertIn('data-entity="Bîffy"', edit)
        self.assertIn("B&icirc;ffy</cite>", edit)
        self.assertIn("Båshy!", edit)

    def test_edit_extended_characters_escaped(self):
        text = textwrap.dedent("""
        <FIGHTER_1>

            I don't like the way you use me, {FIGHTER_2.name!e}!

        """).strip()
        director = Director()
        selection = {
            "FIGHTER_1": Entity(name="Bîffy"),
            "FIGHTER_2": Entity(name="Båshy"),
        }

        speech = Speech(text)
        edit = "\n".join(director.edit(speech, selection))
        self.assertIn('data-role="FIGHTER_1"', edit)
        self.assertIn('data-entity="Bîffy"', edit)
        self.assertIn("B&icirc;ffy</cite>", edit)
        self.assertIn("B&aring;shy!", edit)

    def test_edit_multiple_blocks(self):
        text = textwrap.dedent("""
        <WEAPON.attacking@FIGHTER_2:shouts/slapwhack>

            _Whack!_

        <FIGHTER_2>

            Uuurrggh!

        """).strip()
        director = Director()
        selection = {
            "WEAPON": Entity(name="Rusty"),
            "FIGHTER_2": Entity(name="Bashy"),
        }

        speech = Speech(text)
        edit = "\n".join(director.edit(speech, selection))
        self.assertIn('data-role="WEAPON"', edit)
        self.assertIn('data-entity="Rusty"', edit, speech)
        self.assertIn(">Rusty</cite>", edit)

        self.assertIn('data-role="FIGHTER_2"', edit)
        self.assertIn('data-entity="Bashy"', edit, speech)
        self.assertIn(">Bashy</cite>", edit)


class IntegerConditionTests(unittest.TestCase):
    def test_single_state_selector(self):
        ensemble = [Entity().set_state(1)]
        content = textwrap.dedent("""
        [ENTITY]
        state = 1

        [[_]]

        """).strip()

        d = Director()
        scene = tomllib.loads(content)
        conditions = [dict(d.specify_conditions(shot)) for shot in scene.get(d.shot_key)]

        specs = d.specifications(scene)

        roles = dict(d.roles(specs, ensemble))
        self.assertTrue(d.allows(conditions[0], roles))

    def test_single_state_condition(self):
        ensemble = [Entity().set_state(1)]
        content = textwrap.dedent("""
        [ENTITY]

        [[_]]
        if.ENTITY.state = 0

        [[_]]
        if.ENTITY.state = 1

        """).strip()

        d = Director()
        scene = tomllib.loads(content)
        conditions = [dict(d.specify_conditions(shot)) for shot in scene.get(d.shot_key)]
        self.assertEqual(2, len(conditions))

        specs = d.specifications(scene)

        roles = dict(d.roles(specs, ensemble))
        self.assertFalse(d.allows(conditions[0], roles))
        self.assertTrue(d.allows(conditions[1], roles))

    def test_multi_state_selector(self):
        ensemble = [Entity().set_state(1)]
        content = textwrap.dedent("""
        [ENTITY]
        states.int = [0, 2, 4, 6]

        [[_]]

        """).strip()

        d = Director()
        scene = tomllib.loads(content)
        conditions = [dict(d.specify_conditions(shot)) for shot in scene.get(d.shot_key)]

        specs = d.specifications(scene)

        roles = dict(d.roles(specs, ensemble))
        self.assertTrue(d.allows(conditions[0], roles))

    def test_multi_state_condition(self):
        ensemble = [Entity().set_state(1)]
        content = textwrap.dedent("""
        [ENTITY]

        [[_]]
        if.ENTITY.states.int = [0, 2, 4, 6]

        [[_]]
        if.ENTITY.states.int = [1, 3, 5]

        """).strip()

        d = Director()
        scene = tomllib.loads(content)
        conditions = [dict(d.specify_conditions(shot)) for shot in scene.get(d.shot_key)]
        self.assertEqual(2, len(conditions))

        specs = d.specifications(scene)

        roles = dict(d.roles(specs, ensemble))
        self.assertFalse(d.allows(conditions[0], roles))
        self.assertTrue(d.allows(conditions[1], roles))

    def test_multi_implicit_state_selector(self):
        ensemble = [Entity().set_state(1)]
        content = textwrap.dedent("""
        [ENTITY]
        state = [0, 2, 4, 6]

        [[_]]

        """).strip()

        d = Director()
        scene = tomllib.loads(content)
        conditions = [dict(d.specify_conditions(shot)) for shot in scene.get(d.shot_key)]

        specs = d.specifications(scene)

        roles = dict(d.roles(specs, ensemble))
        self.assertTrue(d.allows(conditions[0], roles))

    def test_multi_implicit_state_condition(self):
        ensemble = [Entity().set_state(1)]
        content = textwrap.dedent("""
        [ENTITY]

        [[_]]
        if.ENTITY.state = [0, 2, 4, 6]

        [[_]]
        if.ENTITY.state = [1, 3, 5]

        """).strip()

        d = Director()
        scene = tomllib.loads(content)
        conditions = [dict(d.specify_conditions(shot)) for shot in scene.get(d.shot_key)]
        self.assertEqual(2, len(conditions))

        specs = d.specifications(scene)

        roles = dict(d.roles(specs, ensemble))
        self.assertFalse(d.allows(conditions[0], roles))
        self.assertTrue(d.allows(conditions[1], roles))


class EnumConditionTests(unittest.TestCase):
    class Rain(Entity):
        pass

    class Sleet(Entity):
        pass

    class Snow(Entity):
        pass

    class Weather(State, enum.Enum):
        quiet = 0
        stormy = 1

    content = textwrap.dedent("""
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

        """).strip()

    def setUp(self):
        self.ensemble = [
            self.Rain().set_state(self.Weather.stormy),
            self.Sleet().set_state(self.Weather.stormy),
            self.Snow().set_state(self.Weather.quiet),
        ]

    def test_condition_evaluation_one(self):
        d = Director()
        scene = tomllib.loads(self.content)
        conditions = [dict(d.specify_conditions(shot)) for shot in scene.get(d.shot_key)]
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

        d = Director()
        scene = tomllib.loads(self.content)
        conditions = [dict(d.specify_conditions(shot)) for shot in scene.get(d.shot_key)]
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
        content = textwrap.dedent("""
        [[_]]
        if.WEATHER.state = "Weather.stormy"

        """).strip()
        scene = tomllib.loads(content)
        director = Director()
        shot = next(iter(scene.get(director.shot_key)))
        conditions = dict(director.specify_conditions(shot))
        self.assertIn("WEATHER", conditions)
        roles, states, types, attributes = conditions["WEATHER"]
        self.assertIn("Weather", states)
        self.assertIn("stormy", states["Weather"])

    def test_guard_conditions_multiple_states(self):
        content = textwrap.dedent("""
        [[_]]
        if.WEATHER.states.Weather = ["stormy", "misty"]

        """).strip()
        scene = tomllib.loads(content)
        director = Director()
        shot = next(iter(scene.get(director.shot_key)))
        conditions = dict(director.specify_conditions(shot))
        self.assertIn("WEATHER", conditions)
        roles, states, types, attributes = conditions["WEATHER"]
        self.assertIn("Weather", states)
        self.assertIn("stormy", states["Weather"])
        self.assertIn("misty", states["Weather"])

    def test_boolean_attribute_true_pos(self):
        content = textwrap.dedent("""
        [ENTITY]

        [[_]]
        if.ENTITY.attr = true

        """).strip()
        for value in (True, "a", 1, [1], dict(a=1)):
            with self.subTest(value=value):
                for i in self.ensemble:
                    i.attr = value

                d = Director()
                scene = tomllib.loads(content)
                conditions = [dict(d.specify_conditions(shot)) for shot in scene.get(d.shot_key)]
                self.assertEqual(1, len(conditions))

                specs = d.specifications(scene)

                self.assertEqual(3, len(self.ensemble))
                roles = dict(d.roles(specs, self.ensemble))
                self.assertTrue(roles, (self.ensemble, specs))
                self.assertTrue(d.allows(conditions[0], roles))

    def test_boolean_attribute_false_neg(self):
        content = textwrap.dedent("""
        [ENTITY]

        [[_]]
        if.ENTITY.attr = false

        """).strip()
        for value in (True, "a", 1, [1], dict(a=1)):
            with self.subTest(value=value):
                for i in self.ensemble:
                    i.attr = value

                d = Director()
                scene = tomllib.loads(content)
                conditions = [dict(d.specify_conditions(shot)) for shot in scene.get(d.shot_key)]
                self.assertEqual(1, len(conditions))

                specs = d.specifications(scene)

                self.assertEqual(3, len(self.ensemble))
                roles = dict(d.roles(specs, self.ensemble))
                self.assertTrue(roles, (self.ensemble, specs))
                self.assertFalse(d.allows(conditions[0], roles))

    def test_boolean_attribute_false_pos(self):
        content = textwrap.dedent("""
        [ENTITY]

        [[_]]
        if.ENTITY.attr = false

        """).strip()
        for value in (False, "", 0, [], dict()):
            with self.subTest(value=value):
                for i in self.ensemble:
                    i.attr = value

                d = Director()
                scene = tomllib.loads(content)
                conditions = [dict(d.specify_conditions(shot)) for shot in scene.get(d.shot_key)]
                self.assertEqual(1, len(conditions))

                specs = d.specifications(scene)

                self.assertEqual(3, len(self.ensemble))
                roles = dict(d.roles(specs, self.ensemble))
                self.assertTrue(roles, (self.ensemble, specs))
                self.assertTrue(d.allows(conditions[0], roles))

    def test_boolean_attribute_true_neg(self):
        content = textwrap.dedent("""
        [ENTITY]

        [[_]]
        if.ENTITY.attr = true

        """).strip()
        for value in (False, "", 0, [], dict()):
            with self.subTest(value=value):
                for i in self.ensemble:
                    i.attr = value

                d = Director()
                scene = tomllib.loads(content)
                conditions = [dict(d.specify_conditions(shot)) for shot in scene.get(d.shot_key)]
                self.assertEqual(1, len(conditions))

                specs = d.specifications(scene)

                self.assertEqual(3, len(self.ensemble))
                roles = dict(d.roles(specs, self.ensemble))
                self.assertTrue(roles, (self.ensemble, specs))
                self.assertFalse(d.allows(conditions[0], roles))


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

    def test_all_types_required(self):
        text = """
        [CHIMERA]
        types = ["Canine", "Feline"]

        """
        scene = tomllib.loads(text)
        self.assertIsInstance(scene, dict)

        director = Director()
        rv = dict(director.roles(scene, self.ensemble))
        self.assertFalse(rv)

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
        ranks = [0, 1, 0.5, 2, 2, 3, 2, 5]
        d = Director()
        for n, (k, v) in enumerate(roles.items()):
            with self.subTest(role=k, spec=v):
                rank = d.rank_constraints(v)
                self.assertEqual(ranks[n], rank, d.specify_role(v))

    def test_role_with_single_required_state(self):
        text = textwrap.dedent("""
        [FIGHTER_1]
        states.Aggression = ["angry"]

        [FIGHTER_2]
        state = "Contentment.sad"

        [WEAPON]
        # A weapon which makes a noise in use.
        """)
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

        director = Director()
        rv = dict(director.roles(scene, self.ensemble))
        self.assertEqual(3, len(rv), rv)
        self.assertEqual(entities["Bashy"], rv["FIGHTER_1"])
        self.assertEqual(entities["Biffy"], rv["FIGHTER_2"])
        self.assertEqual(entities["Rusty"], rv["WEAPON"])

    def test_role_with_multiple_states(self):
        text = textwrap.dedent("""
        [FIGHTER_1]
        states.Location = ["pub_bar", "pub_toilets"]

        [FIGHTER_2]
        state = "Location.pub_bar"

        [WEAPON]
        # A weapon which makes a noise in use.
        """).strip()
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

        director = Director()
        rv = dict(director.roles(scene, self.ensemble))
        self.assertEqual(3, len(rv), rv)
        self.assertEqual(entities["Bashy"], rv["FIGHTER_1"])
        self.assertEqual(entities["Biffy"], rv["FIGHTER_2"])
        self.assertEqual(entities["Rusty"], rv["WEAPON"])

    def test_roles_are_greedy(self):
        text = textwrap.dedent("""
        [CHARACTER_1]
        roles = ["CHARACTER_2"]

        [CHARACTER_2]

        """).strip()
        scene = tomllib.loads(text)
        self.assertIsInstance(scene, dict)

        entities = {i.name: i for i in self.ensemble}

        director = Director()
        rv = dict(director.roles(scene, self.ensemble))
        self.assertEqual(2, len(rv), rv)
        self.assertEqual(entities["Biffy"], rv["CHARACTER_1"])
        self.assertEqual(entities["Biffy"], rv["CHARACTER_2"])


class ParametersTests(unittest.TestCase):
    def test_paragraph_reveal(self):
        text = textwrap.dedent("""
            <?pause=3&dwell=0.4>

            Above, there is the sound of footsteps.

            Of snagging on a threadbare carpet.

            Then shuffling down the ancient stairs.

            """).strip()

        speech = Speech(text)

        d = Director()
        rv = "\n".join(d.edit(speech))
        self.assertEqual(3, rv.count("animation-delay"), rv)
        self.assertEqual(3, rv.count("animation-duration"), rv)

    def test_offer_empty_before_param(self):
        text = textwrap.dedent("""
            <?offer=&pause=0.5>

            Which way? Take your time.

            1. Go North
            2. Go East

            """).strip()

        speech = Speech(text)

        d = Director()
        rv = "\n".join(d.edit(speech))
        self.assertIn("offer", d.notes[(None, 0, 0)])
        self.assertEqual(None, d.notes[(None, 0, 0)]["offer"])
        self.assertIn("delay", d.notes[(None, 0, 0)])
        self.assertAlmostEqual(2.4, d.notes[(None, 0, 0)]["delay"])

    def test_offer_negative(self):
        text = textwrap.dedent("""
            <?offer=1>
            <?offer=-1>

            Which way? Take your time.

            1. Go North
            2. Go East

            """).strip()

        speech = Speech(text)

        d = Director()
        rv = "\n".join(d.edit(speech))
        self.assertIn("offer", d.notes[(None, 0, 0)])
        self.assertEqual(1.0, d.notes[(None, 0, 0)]["offer"])
        self.assertIn("offer", d.notes[(None, 0, 1)])
        self.assertEqual(None, d.notes[(None, 0, 1)]["offer"])
        self.assertIn("delay", d.notes[(None, 0, 1)])
        self.assertAlmostEqual(3.9, d.notes[(None, 0, 1)]["delay"])

    def test_offer_value(self):
        text = textwrap.dedent("""
            <?offer=12#2>

            Which way? You have only a few seconds to decide.

            1. Go North
            2. Go East (default)

            """).strip()

        speech = Speech(text)

        d = Director()
        rv = "\n".join(d.edit(speech))
        self.assertIn("offer", d.notes[(None, 0, 0)])
        self.assertEqual(12, d.notes[(None, 0, 0)]["offer"])
        self.assertIn("option", d.notes[(None, 0, 0)])
        self.assertEqual(2, d.notes[(None, 0, 0)]["option"])

    def test_label_legal(self):
        speech = Speech("<?label=hello-world>Hello, world!")
        d = Director()
        rv = "\n".join(d.edit(speech))
        self.assertTrue(rv.startswith('<blockquote id="hello-world" '), rv)

    def test_label_illegal(self):
        speech = Speech("<?label=_h.e/l?l,o-w+o:r;l^d>Hello, world!")
        d = Director()
        rv = "\n".join(d.edit(speech))
        self.assertTrue(rv.startswith('<blockquote id="hello-world" '), rv)

    def test_class_single(self):
        speech = Speech("<?class=warning>Watch out!")
        d = Director()
        rv = "\n".join(d.edit(speech))
        self.assertTrue(rv.startswith('<blockquote class="warning" '))

    def test_class_multi(self):
        speech = Speech("<?class=urgent&class=warning>Watch out!")
        d = Director()
        rv = "\n".join(d.edit(speech))
        self.assertTrue(rv.startswith('<blockquote class="urgent warning" '), rv)

    def test_style_single(self):
        speech = Speech("<?style=gallery>")
        d = Director()
        rv = "\n".join(d.edit(speech))
        notes = next(iter(d.notes.values()), None)
        self.assertIn("style", notes, notes)
        self.assertIsInstance(notes["style"], list)

    def test_theme_single(self):
        speech = Speech("<?theme=grey>Another gloomy day!")
        d = Director()
        rv = "\n".join(d.edit(speech))
        notes = next(iter(d.notes.values()), None)
        self.assertIn("theme", notes, notes)
        self.assertIsInstance(notes["theme"], list)


class FormatterTests(unittest.TestCase):
    def test_standard_formats(self):
        formatter = Director.Formatter()
        rv = formatter.format("{0:0=6.3f}", 1.2)
        self.assertEqual(rv, "01.200")

    def test_entity_conversion(self):
        formatter = Director.Formatter()
        rv = formatter.format("{0!e}", "<D&D/>")
        self.assertEqual(rv, "&lt;D&amp;D/&gt;")

    def test_rot13_conversion(self):
        formatter = Director.Formatter()
        val = "rot13"
        val = formatter.format("{0!x}", val)
        self.assertEqual(val, "ebg13")
        val = formatter.format("{0!x}", val)
        self.assertEqual(val, "rot13")


class LoopTests(unittest.TestCase):
    def setUp(self):
        self.script = textwrap.dedent("""
        [GUEST]

        [[_]]
        s='''
        <GUEST#!>

            + This, or
            + This, or
            + This, or
        '''
        """).strip()
        self.ensemble = [Entity()]

    def test_attr_matcher(self):
        text = '<cite data-role="GUEST" data-fragments="#!">'
        d = Director()
        attrs = d.attributes(text)
        self.assertIn("role", attrs)
        self.assertEqual("GUEST", attrs["role"], attrs)
        self.assertEqual("#!", attrs["fragments"])

    def test_bang_loop(self):
        d = Director()

        scene = tomllib.loads(self.script)
        specs = d.specifications(scene)
        roles = dict(d.roles(specs, self.ensemble))

        shot = next(iter(scene.get(d.shot_key, [])))
        text = shot.get(d.dialogue_key, "")

        speech = Speech(text)

        rv = "\n".join(d.edit(speech, roles))
        self.assertEqual(0, rv.count("<li>"), rv)
        self.assertEqual(0, rv.count("</li>"))
        self.assertEqual(1, rv.count("This, or"))
        self.assertEqual(1, d.counts[(None, 0, 0)])


class DirectiveTests(unittest.TestCase):
    def test_directive_handling(self):
        script = textwrap.dedent('''
            [GUEST]

            [STAFF]

            [PHONE]

            [[_]]
            s="""
            <PHONE.announcing@GUEST,STAFF> Ring riiing!

            """
            ''').strip()

        scene = tomllib.loads(script)
        ensemble = [Entity(), Entity(), Entity()]

        d = Director()
        specs = d.specifications(scene)
        roles = dict(d.roles(specs, ensemble))

        shot = next(iter(scene.get(d.shot_key, [])))
        text = shot.get(d.dialogue_key, "")
        speech = Speech(text)

        rv = "\n".join(d.edit(speech, roles))

        self.assertIn((None, 0, 0), d.notes)
        self.assertEqual(1.2, d.notes[(None, 0, 0)]["delay"])

        self.assertIn("directives", d.notes[(None, 0, 0)])
        self.assertEqual(
            [("announcing", roles["PHONE"], (roles["GUEST"], roles["STAFF"]))],
            d.notes[(None, 0, 0)]["directives"],
        )


class ModeTests(unittest.TestCase):
    def test_audio_media_in_multiple_blocks(self):
        text = textwrap.dedent("""
        <WEAPON.attacking@FIGHTER_2:shouts/slapwhack>

            _Whack!_

        <FIGHTER_2>

            Uuurrggh!

        """).strip()
        d = Director()
        selection = {
            "WEAPON": Entity(name="Rusty"),
            "FIGHTER_2": Entity(name="Bashy"),
        }

        speech = Speech(text)
        edit = "\n".join(d.edit(speech, selection))
        self.assertIn("media", d.notes[(None, 0, 0)])
        self.assertEqual(["slapwhack"], d.notes[(None, 0, 0)]["media"])


class RewriteTests(unittest.TestCase):
    def setUp(self):
        self.roles = {
            "GUEST": Entity(name="Alan"),
            "STAFF": Entity(name="Beth"),
        }

    def test_empty_rewrite(self):
        d = Director()
        rv = list(d.rewrite())
        self.assertFalse(rv)

    def test_speech_rewrite(self):
        d = Director()
        rv = list(
            d.rewrite(roles=self.roles, speech=[Prologue("<GUEST> I'd like to order a taxi.")])
        )
        self.assertEqual(1, len(rv))
        self.assertIsInstance(rv[0], tuple)
        self.assertEqual(2, len(rv[0]))
        self.assertIn('data-entity="Alan"', rv[0][1])
        self.assertIn(">Alan</cite>", rv[0][1])

    def test_multi_speech_rewrite(self):
        d = Director()
        rv = list(
            d.rewrite(
                roles=self.roles,
                speech=[
                    Dialogue("<GUEST> I'd like to order a taxi, please."),
                    Epilogue("<STAFF> Certainly. Going to?"),
                    Prologue("<STAFF> Can I help you, sir?"),
                ],
            )
        )
        self.assertEqual(3, len(rv))

        self.assertIsInstance(rv[0], tuple)
        self.assertEqual(2, len(rv[0]))
        self.assertIn('data-entity="Beth"', rv[0][1])
        self.assertIn(">Beth</cite>", rv[0][1])
        self.assertIn("help", rv[0][1])

        self.assertIsInstance(rv[1], tuple)
        self.assertEqual(2, len(rv[1]))
        self.assertIn('data-entity="Alan"', rv[1][1])
        self.assertIn(">Alan</cite>", rv[1][1])
        self.assertIn("taxi", rv[1][1])

        self.assertIsInstance(rv[2], tuple)
        self.assertEqual(2, len(rv[2]))
        self.assertIn('data-entity="Beth"', rv[2][1])
        self.assertIn(">Beth</cite>", rv[2][1])
        self.assertIn("Going", rv[2][1])

    def test_multi_speech_notes(self):
        d = Director()
        rv = list(
            d.rewrite(
                roles=self.roles,
                speech=[
                    Dialogue("""
                        <STAFF> Can I help you, sir?
                    """),
                    Dialogue("""
                        <GUEST> I'd like to order a taxi, please.

                        For eight o' clock.

                    """),
                    Dialogue("""
                        <STAFF> Certainly. Going to?
                    """),
                ],
            )
        )

        self.assertEqual(3, len(d.notes))

        for n in range(len(rv)):
            with self.subTest(n=n):
                note = d.notes[(None, n, 0)]
                maps = [i for i in note.maps if i]
                self.assertIn("entity", maps[-1])
                self.assertIn("role", maps[-1])
                self.assertIn("pause", maps[-1])
                self.assertIn("duration", maps[-1])
                self.assertIn("delay", maps[-1])
                self.assertEqual("cue", maps[-1]["type"])
                if n == 1:
                    self.assertEqual(3, len(maps))
                else:
                    self.assertEqual(2, len(maps))

        self.assertEqual(3, len(rv))
