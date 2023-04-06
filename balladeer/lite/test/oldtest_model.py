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

from turberfield.dialogue.performer import Performer
from balladeer.lite.types import DataObject
from balladeer.lite.types import EnumFactory
from balladeer.lite.types import Stateful
from balladeer.lite.types import Player


@unittest.skip("Reference only.")
class SceneTests(unittest.TestCase):
    def test_one_scene(self):
        content = textwrap.dedent(
            """
            Scene
            =====

            Shot
            ----

            Text
        """
        )
        script = SceneScript("inline", doc=SceneScript.read(content))
        script.cast(script.select([]))
        model = list(script.run())
        shot, line = next(iter(model))
        self.assertEqual("scene", shot.scene)
        self.assertEqual("shot", shot.name)

    def test_multi_scene(self):
        content = textwrap.dedent(
            """
            Scene 1
            =======

            Shot 1
            ------

            Text

            Scene 2
            =======

            Shot 2
            ------

            Text
        """
        )
        script = SceneScript("inline", doc=SceneScript.read(content))
        script.cast(script.select([]))
        model = list(script.run())
        shot, line = next(iter(model))
        self.assertEqual("scene 1", shot.scene)
        self.assertEqual("shot 1", shot.name)

    def test_duplicate_shot(self):
        content = textwrap.dedent(
            """
            Scene 1
            =======

            Shot
            ----

            Text

            Scene 2
            =======

            Shot
            ----

            Text
        """
        )
        script = SceneScript("inline", doc=SceneScript.read(content))
        script.cast(script.select([]))
        model = list(script.run())
        shot, line = next(iter(model))
        self.assertEqual("scene 1", shot.scene)
        self.assertEqual("shot", shot.name)

    def test_duplicate_scene(self):
        content = textwrap.dedent(
            """
            Scene
            =====

            Shot 1
            ------

            Text

            Scene
            =====

            Shot 1
            ------

            Text
        """
        )
        script = SceneScript("inline", doc=SceneScript.read(content))
        script.cast(script.select([]))
        model = list(script.run())
        shot, line = next(iter(model))
        self.assertEqual("scene", shot.scene)
        self.assertEqual("shot 1", shot.name)

    def test_shot_duplicates_scene(self):
        content = textwrap.dedent(
            """
            Scene 1
            =======

            Shot 1
            ------

            Text

            Scene 2
            =======

            Scene 1
            -------

            Text
        """
        )
        script = SceneScript("inline", doc=SceneScript.read(content))
        script.cast(script.select([]))
        model = list(script.run())
        shot, line = next(iter(model))
        self.assertEqual("scene 1", shot.scene)
        self.assertEqual("shot 1", shot.name)


class PropertyDirectiveTests(unittest.TestCase):
    personae = [
        Player(name="Prof William Fuzzer Q.A Testfixture"),
        Player(name="Ms Anna Conda"),
        Player(name="A Big Hammer"),
        object(),
    ]

    def test_dialogue_at_level_0(self):
        content = textwrap.dedent(
            """
            .. entity:: P

            [P]_

                You can call me |P_NICKNAME|.

            .. |P_NICKNAME| property:: P.nickname
            """
        )
        script = SceneScript("inline", doc=SceneScript.read(content))
        script.cast(script.select([self.personae[0]]))
        model = list(script.run())
        shot, line = next(iter(model))
        self.assertIs(None, shot.scene)
        self.assertIs(None, shot.name)
        self.assertIn(line.text, ("You can call me Fuzzer.", "You can call me Q.A."))

    def test_dialogue_at_level_1(self):
        content = textwrap.dedent(
            """
            .. entity:: P

            Scene
            =====

            [P]_

                You can call me |P_NICKNAME|.

            .. |P_NICKNAME| property:: P.nickname
            """
        )
        script = SceneScript("inline", doc=SceneScript.read(content))
        script.cast(script.select([self.personae[0]]))
        model = list(script.run())
        self.assertFalse(model)

    def test_speaker_reset_by_shot(self):
        content = textwrap.dedent(
            """
            .. entity:: P

            Scene
            ~~~~~

            One
            ---

            [P]_

                I'm speaking.

            Two
            ---

            Not any more.
            """
        )
        script = SceneScript("inline", doc=SceneScript.read(content))
        script.cast(script.select([self.personae[0]]))
        model = script.run()
        one, two = list(model)
        self.assertTrue(one[1].persona)
        self.assertIsNone(two[1].persona)

    def test_speaker_reset_by_dedent(self):
        content = textwrap.dedent(
            """
            .. entity:: P

            Scene
            ~~~~~

            One
            ---

            [P]_

                I'm speaking.

                Still speaking.

            Not any more.
            """
        )
        script = SceneScript("inline", doc=SceneScript.read(content))
        script.cast(script.select([self.personae[0]]))
        model = script.run()
        one, two, three = list(model)
        self.assertTrue(one[1].persona)
        self.assertTrue(two[1].persona)
        self.assertIsNone(three[1].persona, three)

    def test_property_getter(self):
        content = textwrap.dedent(
            """
            .. entity:: P

            Scene
            ~~~~~

            Shot
            ----

            [P]_

                Hi, I'm |P_FIRSTNAME|.

            |P_SURNAME|.

            .. |P_FIRSTNAME| property:: P.name.firstname
            .. |P_SURNAME| property:: P.name.surname
            """
        )
        script = SceneScript("inline", doc=SceneScript.read(content))
        script.cast(script.select([self.personae[0]]))
        model = iter(script.run())
        shot, line = next(model)
        self.assertEqual("scene", shot.scene)
        self.assertEqual("shot", shot.name)
        self.assertEqual("Hi, I'm William.", line.text)
        shot, line = next(model)
        self.assertFalse(line.persona, line)

    def test_property_getter_format(self):
        content = textwrap.dedent(
            """
            .. entity:: P

            Scene
            ~~~~~

            Shot
            ----

            [P]_

                Hi, I'm |P_FIRSTNAME|.

            |P_SURNAME|.

            .. |P_FIRSTNAME| property:: P.name.firstname[0]
            .. |P_SURNAME| property:: P.name.surname
            """
        )
        script = SceneScript("inline", doc=SceneScript.read(content))
        script.cast(script.select([self.personae[0]]))
        model = iter(script.run())
        shot, line = next(model)
        self.assertEqual("scene", shot.scene)
        self.assertEqual("shot", shot.name)
        self.assertEqual("Hi, I'm W.", line.text)
        shot, line = next(model)
        self.assertFalse(line.persona, line)

    def test_property_getter_indent(self):
        content = textwrap.dedent(
            """
            .. entity:: P

            Scene
            ~~~~~

            Shot
            ----

            [P]_

                Hi, I'm |P_FIRSTNAME|.

                |P_SURNAME|.

            .. |P_FIRSTNAME| property:: P.name.firstname
            .. |P_SURNAME| property:: P.name.surname
            """
        )
        script = SceneScript("inline", doc=SceneScript.read(content))
        script.cast(script.select([self.personae[0]]))
        model = iter(script.run())
        shot, line = next(model)
        self.assertEqual("scene", shot.scene)
        self.assertEqual("shot", shot.name)
        self.assertEqual("Hi, I'm William.", line.text)
        self.assertTrue(line.persona)
        shot, line = next(model)
        self.assertTrue(line.persona, line)

    def test_property_getter_fields(self):
        content = textwrap.dedent(
            """
            .. |VERSION| property:: turberfield.dialogue.__version__

            :copyright: 2017
            :version: |VERSION|

            """
        )
        script = SceneScript("inline", doc=SceneScript.read(content))
        script.cast(script.select([self.personae[0]]))
        model = script.run()
        metadata = dict(model.metadata)
        self.assertIn("copyright", metadata)
        self.assertIn("version", metadata)
        self.assertEqual(2, metadata["version"].count("."), metadata)

    def test_nickname_getter(self):
        content = textwrap.dedent(
            """
            .. entity:: P

            Scene
            ~~~~~

            Shot
            ----

            [P]_

                You can call me |P_NICKNAME|.

            .. |P_NICKNAME| property:: P.nickname
            """
        )
        script = SceneScript("inline", doc=SceneScript.read(content))
        script.cast(script.select([self.personae[0]]))
        model = list(script.run())
        shot, line = next(iter(model))
        self.assertEqual("scene", shot.scene)
        self.assertEqual("shot", shot.name)
        self.assertIn(line.text, ("You can call me Fuzzer.", "You can call me Q.A."))

    def test_property_setter_enum(self):
        content = textwrap.dedent(
            """
            .. entity:: P

            Scene
            ~~~~~

            Shot
            ----

            .. property:: P.state turberfield.dialogue.test.test_model.SelectTests.Aggression.calm

            """
        )
        ensemble = copy.deepcopy(PropertyDirectiveTests.personae)
        script = SceneScript("inline", doc=SceneScript.read(content))
        script.cast(script.select([ensemble[0]]))
        model = script.run()
        p = next(l for s, l in model if isinstance(l, Model.Property))
        self.assertEqual("state", p.attr)
        self.assertEqual(str(SelectTests.Aggression.calm), str(p.val))
        setattr(p.object, p.attr, p.val)

    def test_property_setter_integer(self):
        content = textwrap.dedent(
            """
            .. entity:: P

            Scene
            ~~~~~

            Shot
            ----

            .. property:: P.state 3

            """
        )
        ensemble = copy.deepcopy(PropertyDirectiveTests.personae)
        script = SceneScript("inline", doc=SceneScript.read(content))
        script.cast(script.select([ensemble[0]]))
        model = script.run()
        p = next(l for s, l in model if isinstance(l, Model.Property))
        self.assertEqual("state", p.attr)
        self.assertEqual(3, p.val)

    def test_property_setter_bad_substitution(self):
        content = textwrap.dedent(
            """
            .. entity:: P

            Scene
            ~~~~~

            Shot
            ----

            .. property:: P.state |S_ID|

            """
        )
        ensemble = copy.deepcopy(PropertyDirectiveTests.personae)
        script = SceneScript("inline", doc=SceneScript.read(content))
        script.cast(script.select([ensemble[0]]))
        model = script.run()
        p = next(l for s, l in model if isinstance(l, Model.Property))
        self.assertEqual("state", p.attr)
        self.assertIs(None, p.val)

    def test_property_setter_good_substitution(self):
        content = textwrap.dedent(
            """
            .. entity:: P
            .. entity:: S

            .. |S_ID| property:: S.id.int

            Scene
            ~~~~~

            Shot
            ----

            .. property:: P.state |S_ID|

            """
        )
        ensemble = copy.deepcopy(PropertyDirectiveTests.personae)
        script = SceneScript("inline", doc=SceneScript.read(content))
        script.cast(script.select(ensemble))
        model = script.run()
        p = [l for s, l in model if isinstance(l, Model.Property)][-1]
        self.assertEqual("state", p.attr)
        self.assertIsInstance(p.val, int)

    def test_property_setter_object(self):
        content = textwrap.dedent(
            """
            .. entity:: P
            .. entity:: S

            Scene
            ~~~~~

            Shot
            ----

            .. property:: P.id S.id

            """
        )
        ensemble = copy.deepcopy(PropertyDirectiveTests.personae)
        script = SceneScript("inline", doc=SceneScript.read(content))
        script.cast(script.select(ensemble))
        model = script.run()
        p = [l for s, l in model if isinstance(l, Model.Property)][-1]
        self.assertEqual(ensemble[0], p.object)
        self.assertEqual("id", p.attr)
        self.assertIsInstance(p.val, uuid.UUID)
        self.assertEqual(p.val, ensemble[1].id)


@unittest.skipIf(
    "discover" in sys.argv,
    (
        "Testing condition directive: "
        "Needs ~/py3.5/bin/python -m unittest turberfield.dialogue.test.test_model"
    ),
)
class ConditionDirectiveTests(unittest.TestCase):
    class Rain(Stateful):
        pass

    class Sleet(Stateful):
        pass

    class Snow(Stateful):
        pass

    class Weather(EnumFactory, enum.Enum):
        quiet = 0
        stormy = 1

    content = textwrap.dedent(
        """
        .. entity:: WEATHER
           :types: turberfield.dialogue.test.test_model.ConditionDirectiveTests.Rain
                   turberfield.dialogue.test.test_model.ConditionDirectiveTests.Snow
           :states: turberfield.dialogue.test.test_model.ConditionDirectiveTests.Weather.stormy

        A stormy night
        ~~~~~~~~~~~~~~

        Outside.

        Intense
        -------

        .. condition:: WEATHER.state
                       turberfield.dialogue.test.test_model.ConditionDirectiveTests.Weather.stormy

        [WEATHER]_

            It's stormy!

        Hushed
        ------

        .. condition:: WEATHER.state.name quiet

        [WEATHER]_

            It's quiet.

        Snow storm
        ----------

        .. condition:: WEATHER.__class__
                       turberfield.dialogue.test.test_model.ConditionDirectiveTests.Snow

        [WEATHER]_

            Flurry, flurry.

        Rainfall
        --------

        .. condition:: WEATHER.__class__
                       turberfield.dialogue.test.test_model.ConditionDirectiveTests.Rain

        [WEATHER]_

            Pitter patter.
        """
    )

    effects = [
        Rain().set_state(Weather.stormy),
        Sleet().set_state(Weather.stormy),
        Snow().set_state(Weather.quiet),
    ]

    def test_condition_evaluation_one(self):
        effects = [
            ConditionDirectiveTests.Rain().set_state(
                ConditionDirectiveTests.Weather.stormy
            ),
            ConditionDirectiveTests.Sleet().set_state(
                ConditionDirectiveTests.Weather.stormy
            ),
            ConditionDirectiveTests.Snow().set_state(
                ConditionDirectiveTests.Weather.quiet
            ),
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
            ConditionDirectiveTests.Rain().set_state(
                ConditionDirectiveTests.Weather.quiet
            ),
            ConditionDirectiveTests.Sleet().set_state(
                ConditionDirectiveTests.Weather.stormy
            ),
            ConditionDirectiveTests.Snow().set_state(
                ConditionDirectiveTests.Weather.stormy
            ),
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


class ConditionSyntaxTests(unittest.TestCase):
    def test_exact_matching(self):
        content = textwrap.dedent(
            """
            .. entity:: WHATEVER

            Test exact
            ~~~~~~~~~~

            One
            ---

            .. condition:: WHATEVER.value 1

            One.

            Two
            ---

            .. condition:: WHATEVER.value 2

            Two.

        """
        )
        script = SceneScript("inline", doc=SceneScript.read(content))
        selection = script.select([DataObject(value=1)])
        self.assertTrue(all(selection.values()))
        script.cast(selection)
        model = script.run()
        conditions = [l for s, l in model if isinstance(l, Model.Condition)]
        self.assertEqual(2, len(conditions))

        self.assertTrue(Performer.allows(conditions[0]))
        self.assertFalse(Performer.allows(conditions[1]))

    def test_regex_matching_attribute(self):
        content = textwrap.dedent(
            """
            .. entity:: WHATEVER

            Test exact
            ~~~~~~~~~~

            Odd
            ---

            .. condition:: WHATEVER.value ([13579])

            Odd.

            Even
            ----

            .. condition:: WHATEVER.value ([02468])

            Even.

        """
        )
        obj = DataObject(value=1)
        script = SceneScript("inline", doc=SceneScript.read(content))
        selection = script.select([obj])
        self.assertTrue(all(selection.values()))
        script.cast(selection)
        model = script.run()
        conditions = [l for s, l in model if isinstance(l, Model.Condition)]
        self.assertEqual(2, len(conditions))

        self.assertTrue(Performer.allows(conditions[0]), conditions[0])
        self.assertFalse(Performer.allows(conditions[1]))

        obj.value = 2
        self.assertFalse(Performer.allows(conditions[0]), conditions[0])
        self.assertTrue(Performer.allows(conditions[1]))

    def test_regex_matching_state(self):
        content = textwrap.dedent(
            """
            .. entity:: WHATEVER

            Test exact
            ~~~~~~~~~~

            Even
            ----

            .. condition:: WHATEVER.state ([02468])

            Even.

            Odd
            ---

            .. condition:: WHATEVER.state ([13579])

            Odd.

        """
        )
        obj = Stateful()
        script = SceneScript("inline", doc=SceneScript.read(content))
        selection = script.select([obj])
        self.assertTrue(all(selection.values()))
        script.cast(selection)
        model = script.run()
        conditions = [l for s, l in model if isinstance(l, Model.Condition)]
        self.assertEqual(2, len(conditions))

        self.assertTrue(Performer.allows(conditions[0]), conditions[0])
        self.assertFalse(Performer.allows(conditions[1]))

        obj.state = 1
        self.assertFalse(Performer.allows(conditions[0]), conditions[0])
        self.assertTrue(Performer.allows(conditions[1]))


class SelectTests(unittest.TestCase):
    @enum.unique
    class Aggression(EnumFactory, enum.Enum):
        calm = 0
        angry = 1

    @enum.unique
    class Contentment(EnumFactory, enum.Enum):
        sad = 0
        happy = 1

    @enum.unique
    class Location(EnumFactory, enum.Enum):
        pub = 0
        pub_bar = 1
        pub_carpark = 2
        pub_snug = 3
        pub_toilets = 4

    def test_select_with_required_state(self):
        content = textwrap.dedent(
            """
            .. entity:: FIGHTER_1
               :states: turberfield.dialogue.test.test_model.SelectTests.Aggression.angry

            .. entity:: FIGHTER_2
               :states: turberfield.dialogue.test.test_model.SelectTests.Contentment.sad

            .. entity:: WEAPON

               A weapon which makes a noise in use. 
            """
        )
        ensemble = copy.deepcopy(PropertyDirectiveTests.personae)
        ensemble[0].set_state(SelectTests.Contentment.sad)
        self.assertEqual(
            SelectTests.Contentment.sad, ensemble[0].get_state(SelectTests.Contentment)
        )
        ensemble[1].set_state(SelectTests.Aggression.angry)
        self.assertEqual(
            SelectTests.Aggression.angry, ensemble[1].get_state(SelectTests.Aggression)
        )
        script = SceneScript("inline", doc=SceneScript.read(content))
        rv = list(script.select(ensemble).values())
        self.assertEqual(ensemble[0], rv[1])
        self.assertEqual(ensemble[1], rv[0])

    def test_select_with_hierarchical_state(self):
        content = textwrap.dedent(
            """
            .. entity:: FIGHTER_1
               :states: turberfield.dialogue.test.test_model.SelectTests.Location.pub

            .. entity:: FIGHTER_2
               :states: turberfield.dialogue.test.test_model.SelectTests.Location.pub

            .. entity:: WEAPON

               A weapon which makes a noise in use. 
            """
        )
        ensemble = copy.deepcopy(PropertyDirectiveTests.personae)
        ensemble[0].set_state(SelectTests.Location.pub_bar)
        self.assertEqual(
            SelectTests.Location.pub_bar, ensemble[0].get_state(SelectTests.Location)
        )
        ensemble[1].set_state(SelectTests.Location.pub_toilets)
        self.assertEqual(
            SelectTests.Location.pub_toilets,
            ensemble[1].get_state(SelectTests.Location),
        )
        script = SceneScript("inline", doc=SceneScript.read(content))
        rv = list(script.select(ensemble).values())
        self.assertEqual(ensemble[0], rv[0])
        self.assertEqual(ensemble[1], rv[1])

    def test_select_with_integer_state(self):
        content = textwrap.dedent(
            """
            .. entity:: FIGHTER_1
               :states: 1

            .. entity:: FIGHTER_2
               :states: 2

            .. entity:: WEAPON

               A weapon which makes a noise in use.
            """
        )
        ensemble = copy.deepcopy(PropertyDirectiveTests.personae)
        ensemble[0].set_state(2)
        self.assertEqual(2, ensemble[0].get_state())
        ensemble[1].set_state(1)
        self.assertEqual(1, ensemble[1].get_state())
        script = SceneScript("inline", doc=SceneScript.read(content))
        rv = list(script.select(ensemble).values())
        self.assertEqual(ensemble[0], rv[1])
        self.assertEqual(ensemble[1], rv[0])

    def test_select_with_herarchical_integer_state(self):
        content = textwrap.dedent(
            """
            .. entity:: FIGHTER_1
               :states: 3

            .. entity:: FIGHTER_2
               :states: 3

            .. entity:: WEAPON

               A weapon which makes a noise in use.
            """
        )
        ensemble = copy.deepcopy(PropertyDirectiveTests.personae)
        ensemble[0].set_state(31)
        self.assertEqual(31, ensemble[0].get_state())
        ensemble[1].set_state(32)
        self.assertEqual(32, ensemble[1].get_state())
        script = SceneScript("inline", doc=SceneScript.read(content))
        rv = list(script.select(ensemble).values())
        self.assertEqual(ensemble[0], rv[0])
        self.assertEqual(ensemble[1], rv[1])

    def test_select_with_unfulfilled_state(self):
        content = textwrap.dedent(
            """
            .. entity:: FIGHTER_1
               :states: turberfield.dialogue.test.test_model.SelectTests.Aggression.angry

            .. entity:: FIGHTER_2
               :states: turberfield.dialogue.test.test_model.SelectTests.Contentment.sad

            .. entity:: WEAPON

               A weapon which makes a noise in use. 
            """
        )
        ensemble = copy.deepcopy(PropertyDirectiveTests.personae)
        ensemble[0].set_state(SelectTests.Contentment.sad)
        self.assertEqual(
            SelectTests.Contentment.sad, ensemble[0].get_state(SelectTests.Contentment)
        )
        ensemble[1].set_state(SelectTests.Contentment.sad)
        self.assertEqual(
            SelectTests.Contentment.sad, ensemble[1].get_state(SelectTests.Contentment)
        )
        script = SceneScript("inline", doc=SceneScript.read(content))
        rv = list(script.select(ensemble).values())
        self.assertIsNone(rv[0])
        self.assertEqual(ensemble[0], rv[1])

    def test_select_with_two_roles(self):
        content = textwrap.dedent(
            """
            .. entity:: CHARACTER_1
               :roles: CHARACTER_2

            .. entity:: CHARACTER_2

            """
        )
        ensemble = copy.deepcopy(PropertyDirectiveTests.personae[0:1])
        script = SceneScript("inline", doc=SceneScript.read(content))
        rv = list(script.select(ensemble, roles=2).values())
        self.assertEqual(ensemble[0], rv[0])
        self.assertEqual(ensemble[0], rv[1])


class HTMLEscapingTests(unittest.TestCase):
    def test_escape_ampersand(self):
        content = textwrap.dedent(
            """
            Characters
            ==========

            Ampersand
            ---------

            Three pints of M&B please.

        """
        )
        script = SceneScript("inline", doc=SceneScript.read(content))
        model = script.run()
        line = model.shots[0].items[0]
        self.assertIn("M&amp;B", line.html)

    def test_escape_brackets(self):
        content = textwrap.dedent(
            """
            Characters
            ==========

            Greater
            -------

            3 > 1

            Less
            ----

            1 < 3

        """
        )
        script = SceneScript("inline", doc=SceneScript.read(content))
        model = script.run()
        for n, shot in enumerate(model.shots):
            with self.subTest(n=n):
                if n:
                    self.assertIn("1 &lt; 3", shot.items[0].html)
                else:
                    self.assertIn("3 &gt; 1", shot.items[0].html)

    def test_noescape_common_characters(self):
        content = textwrap.dedent(
            """
            Characters
            ==========

            Unchanged
            ---------

            !"*()+-:;'.,@#{}=~

        """
        )
        script = SceneScript("inline", doc=SceneScript.read(content))
        model = script.run()
        line = model.shots[0].items[0]
        self.assertNotIn("&", line.html)

    def test_escape_common_characters(self):
        content = textwrap.dedent(
            """
            Characters
            ==========

            Changed
            -------

            $%^©£

        """
        )
        script = SceneScript("inline", doc=SceneScript.read(content))
        model = script.run()
        line = model.shots[0].items[0]
        self.assertEqual(5, line.html.count("&"), line.html)


class RstFeatureTests(unittest.TestCase):
    def test_bullet_lists(self):
        content = textwrap.dedent(
            """
            Scene
            =====

            Shot
            ----

            ABC.

            * Always
            * Be
            * Closing

        """
        )
        script = SceneScript("inline", doc=SceneScript.read(content))
        model = script.run()
        self.assertEqual(
            ["Always", "Be", "Closing"], model.shots[-1].items[-1].text.splitlines()
        )
        self.assertEqual(2, model.shots[-1].items[-1].html.count("ul>"))
        self.assertEqual(6, model.shots[-1].items[-1].html.count("li>"))

    def test_markup_body_text(self):
        content = textwrap.dedent(
            """
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
        """
        )
        script = SceneScript("inline", doc=SceneScript.read(content))
        model = script.run()
        for shot in model.shots:
            with self.subTest(shot_name=shot.name):
                self.assertTrue(all("keep" in line.text for line in shot.items))
                self.assertFalse(any("  " in line.text for line in shot.items), shot)
                if shot.name.startswith("em"):
                    self.assertTrue(
                        all('<em class="text">' in line.html for line in shot.items)
                    )
                    self.assertTrue(all("</em>" in line.html for line in shot.items))
                elif shot.name.startswith("strong"):
                    self.assertTrue(
                        all('<strong class="text">' in line.html for line in shot.items)
                    )
                    self.assertTrue(
                        all("</strong>" in line.html for line in shot.items)
                    )
                elif shot.name.startswith("pre"):
                    self.assertTrue(
                        all('<pre class="text">' in line.html for line in shot.items)
                    )
                    self.assertTrue(all("</pre>" in line.html for line in shot.items))

    def test_hyperlink_body_text(self):
        content = textwrap.dedent(
            """
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

        """
        )
        script = SceneScript("inline", doc=SceneScript.read(content))
        model = script.run()
        for shot in model.shots:
            with self.subTest(shot_name=shot.name):
                self.assertFalse(any("  " in line.text for line in shot.items))
                self.assertTrue(
                    all(
                        '<a href="http://www.python.org">' in i.html for i in shot.items
                    ),
                    shot,
                )

    def test_raw_html(self):
        content = textwrap.dedent(
            """
            Scene
            =====

            Shot
            ----

            I know what it needs...

            .. raw:: html

                <marquee>Puppies die when you do bad design</marquee>
        """
        )
        script = SceneScript("inline", doc=SceneScript.read(content))
        model = script.run()
        self.assertEqual(2, model.shots[-1].items[-1].html.count("marquee"))
        self.assertEqual(0, model.shots[-1].items[-1].text.count("marquee"))
