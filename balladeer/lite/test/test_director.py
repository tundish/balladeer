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

from speechmark import SpeechMark

from balladeer.lite.director import Director
from balladeer.lite.types import Entity
from balladeer.lite.types import State


class EditTests(unittest.TestCase):

    def test_word_counter(self):
        text = textwrap.dedent("""
        <STAFF.proposing#3> What will you have, sir? The special is fish today.

            1. Order the Beef Wellington
            2. Go for the Shepherd's Pie
            3. Try the Dover Sole
        """).strip()
        sm = SpeechMark()
        html = sm.loads(text)

        director = Director(story=None)
        self.assertEqual(5, len(director.lines(html)))
        self.assertEqual(24, len(director.words(html)))

    def test_rewriter_single_blocks(self):
        text = textwrap.dedent("""
        <FIGHTER_1>

            I don't like the way you use me, {FIGHTER_2.name}!

        """).strip()
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
        text = textwrap.dedent("""
        <FIGHTER_1>

            I don't like the way you use me, {FIGHTER_2.name}!

        """).strip()
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
        text = textwrap.dedent("""
        <FIGHTER_1>

            I don't like the way you use me, {FIGHTER_2.name!a}!

        """).strip()
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
        text = textwrap.dedent("""
        <WEAPON.attacking@FIGHTER_2:shouts/slapwhack>

            _Whack!_

        <FIGHTER_2>

            Uuurrggh!

        """).strip()
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


@unittest.skip("not yet")
class ConditionDirectiveTests(unittest.TestCase):

    class Rain(Entity): pass
    class Sleet(Entity): pass
    class Snow(Entity): pass

    class Weather(State, enum.Enum):
        quiet = 0
        stormy = 1

    content = textwrap.dedent(
        """

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

        [[__]]
        # Snow storm
        if.WEATHER.type = "Snow"

        s="<WEATHER> Flurry, flurry."

        [[__]]
        # Rainfall
        if.WEATHER.type = "Rain"

        s="<WEATHER> Pitter patter."

        """).strip()

    effects = [
        Rain().set_state(Weather.stormy),
        Sleet().set_state(Weather.stormy),
        Snow().set_state(Weather.quiet),
    ]

    def test_condition_evaluation_one(self):
        effects = [
            ConditionDirectiveTests.Rain().set_state(ConditionDirectiveTests.Weather.stormy),
            ConditionDirectiveTests.Sleet().set_state(ConditionDirectiveTests.Weather.stormy),
            ConditionDirectiveTests.Snow().set_state(ConditionDirectiveTests.Weather.quiet),
        ]

        script = SceneScript("inline", doc=SceneScript.read(self.content))
        selection = script.select(effects)
        self.assertTrue(all(selection.values()))
        script.cast(selection)
        model = script.run()
        conditions = [l for s, l in model if isinstance(l, Model.Condition)]
        self.assertEqual(4, len(conditions))

        self.assertTrue(Performer.allows(conditions[0]))
        self.assertFalse(Performer.allows(conditions[1]))
        self.assertFalse(Performer.allows(conditions[2]))
        self.assertTrue(Performer.allows(conditions[3]))

    def test_condition_evaluation_two(self):
        effects = [
            ConditionDirectiveTests.Rain().set_state(ConditionDirectiveTests.Weather.quiet),
            ConditionDirectiveTests.Sleet().set_state(ConditionDirectiveTests.Weather.stormy),
            ConditionDirectiveTests.Snow().set_state(ConditionDirectiveTests.Weather.stormy),
        ]

        script = SceneScript("inline", doc=SceneScript.read(self.content))
        selection = script.select(effects)
        self.assertTrue(all(selection.values()))
        script.cast(selection)
        model = script.run()
        conditions = [l for s, l in model if isinstance(l, Model.Condition)]
        self.assertEqual(4, len(conditions))

        self.assertTrue(Performer.allows(conditions[0]))
        self.assertFalse(Performer.allows(conditions[1]))
        self.assertTrue(Performer.allows(conditions[2]))
        self.assertFalse(Performer.allows(conditions[3]))


class SelectionTests(unittest.TestCase):

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
            Entity(name="Biffy", types=["Animal", "Canine"]),
            Entity(name="Bashy", types=["Animal", "Feline"]),
            Entity(name="Rusty", type="Weapon"),
        ]

    def test_rank_contstraints(self):
        roles = {
            "A": {
            },
            "B": {
            },
            "C": {
            },
            "D": {
            },
        }
        for k, v in roles.items():
            with self.subTest(role=k, spec=v):
                self.fail(Director.rank_constraints(v))

    def test_select_with_required_state(self):
        content = textwrap.dedent("""
            [FIGHTER_1]
            states.Aggression = ["angry"]

            [FIGHTER_2]
            states.Contentment = ["sad"]

            [WEAPON]
            # A weapon which makes a noise in use.
            """)
        cast = {i.name: i for i in self.ensemble}
        cast["Biffy"].set_state(SelectionTests.Contentment.sad)
        self.assertEqual(
            SelectionTests.Contentment.sad,
            cast["Biffy"].get_state(SelectionTests.Contentment)
        )
        cast["Bashy"].set_state(SelectionTests.Aggression.angry)
        self.assertEqual(
            SelectionTests.Aggression.angry,
            cast["Bashy"].get_state(SelectionTests.Aggression)
        )
        script = SceneScript("inline", doc=SceneScript.read(content))
        rv = list(script.select(ensemble).values())
        self.assertEqual(cast["Biffy"], rv[1])
        self.assertEqual(cast["Bashy"], rv[0])

    def test_select_with_hierarchical_state(self):

        content = textwrap.dedent("""
        [FIGHTER_1]
        states.Location = ["pub_bar", "pub_toilets"]

        [FIGHTER_2]
        states.Location = ["pub_bar"]

        [WEAPON]
        # A weapon which makes a noise in use.
        """).strip()
        cast = {i.name: i for i in self.ensemble}
        cast["Biffy"].set_state(SelectionTests.Location.pub_bar)
        self.assertEqual(
            SelectionTests.Location.pub_bar,
            cast["Biffy"].get_state(SelectionTests.Location)
        )
        cast["Bashy"].set_state(SelectionTests.Location.pub_toilets)
        self.assertEqual(
            SelectionTests.Location.pub_toilets,
            cast["Bashy"].get_state(SelectionTests.Location)
        )
        director = Director(None)
        script = SceneScript("inline", doc=SceneScript.read(content))
        rv = list(script.select(ensemble).values())
        self.assertEqual(self.cast["Biffy"], rv[0])
        self.assertEqual(cast["Bashy"], rv[1])

    def test_select_with_two_roles(self):
        content = textwrap.dedent("""
        [CHARACTER_1]
        roles = ["CHARACTER_2"]

        [CHARACTER_2]

        """).strip()
        ensemble = copy.deepcopy(PropertyDirectiveTests.personae[0:1])
        script = SceneScript("inline", doc=SceneScript.read(content))
        rv = list(script.select(ensemble, roles=2).values())
        self.assertEqual(ensemble[0], rv[0])
        self.assertEqual(ensemble[0], rv[1])


@unittest.skip("not yet")
class HTMLEscapingTests(unittest.TestCase):

    def test_escape_ampersand(self):
        content = textwrap.dedent("""
            Characters
            ==========

            Ampersand
            ---------

            Three pints of M&B please.

        """)
        script = SceneScript("inline", doc=SceneScript.read(content))
        model = script.run()
        line = model.shots[0].items[0]
        self.assertIn("M&amp;B", line.html)

    def test_escape_brackets(self):
        content = textwrap.dedent("""
            Characters
            ==========

            Greater
            -------

            3 > 1

            Less
            ----

            1 < 3

        """)
        script = SceneScript("inline", doc=SceneScript.read(content))
        model = script.run()
        for n, shot in enumerate(model.shots):
            with self.subTest(n=n):
                if n:
                    self.assertIn("1 &lt; 3", shot.items[0].html)
                else:
                    self.assertIn("3 &gt; 1", shot.items[0].html)

    def test_noescape_common_characters(self):
        content = textwrap.dedent("""
            Characters
            ==========

            Unchanged
            ---------

            !"*()+-:;'.,@#{}=~

        """)
        script = SceneScript("inline", doc=SceneScript.read(content))
        model = script.run()
        line = model.shots[0].items[0]
        self.assertNotIn("&", line.html)

    def test_escape_common_characters(self):
        content = textwrap.dedent("""
            Characters
            ==========

            Changed
            -------

            $%^©£

        """)
        script = SceneScript("inline", doc=SceneScript.read(content))
        model = script.run()
        line = model.shots[0].items[0]
        self.assertEqual(5, line.html.count("&"), line.html)


@unittest.skip("not yet")
class RstFeatureTests(unittest.TestCase):

    def test_bullet_lists(self):
        content = textwrap.dedent("""
            Scene
            =====

            Shot
            ----

            ABC.

            * Always
            * Be
            * Closing

        """)
        script = SceneScript("inline", doc=SceneScript.read(content))
        model = script.run()
        self.assertEqual(["Always", "Be", "Closing"], model.shots[-1].items[-1].text.splitlines())
        self.assertEqual(2, model.shots[-1].items[-1].html.count("ul>"))
        self.assertEqual(6, model.shots[-1].items[-1].html.count("li>"))

    def test_markup_body_text(self):
        content = textwrap.dedent("""
            Markup
            ======

            Emphasis
            --------

            I *keep* telling you.

            I :emphasis:`keep` telling you.

            Strong
            ------

            I **keep** telling you.

            I :strong:`keep` telling you.

            Preformat
            ---------

            I ``keep`` telling you.

            I :literal:`keep` telling you.
        """)
        script = SceneScript("inline", doc=SceneScript.read(content))
        model = script.run()
        for shot in model.shots:
            with self.subTest(shot_name=shot.name):
                self.assertTrue(all("keep" in line.text for line in shot.items))
                self.assertFalse(any("  " in line.text for line in shot.items), shot)
                if shot.name.startswith("em"):
                    self.assertTrue(all('<em class="text">' in line.html for line in shot.items)) 
                    self.assertTrue(all("</em>" in line.html for line in shot.items)) 
                elif shot.name.startswith("strong"):
                    self.assertTrue(all('<strong class="text">' in line.html for line in shot.items)) 
                    self.assertTrue(all("</strong>" in line.html for line in shot.items)) 
                elif shot.name.startswith("pre"):
                    self.assertTrue(all('<pre class="text">' in line.html for line in shot.items)) 
                    self.assertTrue(all("</pre>" in line.html for line in shot.items))

    def test_hyperlink_body_text(self):
        content = textwrap.dedent("""
            Hyperlinks
            ==========

            Standalone
            ----------

            See http://www.python.org for info.

            Embedded
            --------

            See the `Python site <http://www.python.org>`_ for info.

            Named
            -----

            See the `Python home page`_ for info.

            .. _Python home page: http://www.python.org

        """)
        script = SceneScript("inline", doc=SceneScript.read(content))
        model = script.run()
        for shot in model.shots:
            with self.subTest(shot_name=shot.name):
                self.assertFalse(any("  " in line.text for line in shot.items))
                self.assertTrue(all('<a href="http://www.python.org">' in i.html for i in shot.items), shot)

    def test_raw_html(self):
        content = textwrap.dedent("""
            Scene
            =====

            Shot
            ----

            I know what it needs...

            .. raw:: html

                <marquee>Puppies die when you do bad design</marquee>
        """)
        script = SceneScript("inline", doc=SceneScript.read(content))
        model = script.run()
        self.assertEqual(2, model.shots[-1].items[-1].html.count("marquee"))
        self.assertEqual(0, model.shots[-1].items[-1].text.count("marquee"))


class AdLibTests(unittest.TestCase):

    def setUp(self):
        text = textwrap.dedent("""
        <GUEST>

            + This, or
            + This, or
            + This, or

        """).strip()
        sm = SpeechMark()
        self.html = sm.loads(text)

    def test_adlib_off(self):
        director = Director(story=None, ad_lib=False)
        self.assertEqual(5, len(director.lines(self.html)))

    def test_adlib_on(self):
        director = Director(story=None, ad_lib=True)
        self.assertEqual(5, len(director.lines(self.html)))


@unittest.skip("not yet")
class DirectiveTests(unittest.TestCase):

    def test_directive_handling(self):
        """
        <PHONE.announcing@GUEST,STAFF> Ring riiing!
        """
        # TODO: Mock Drama methods.

