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


import codecs
from collections.abc import Generator
from collections import ChainMap
from collections import Counter
from collections import defaultdict
import html
import itertools
import pathlib
import re
import string
import sys
import urllib.parse


from balladeer.lite.entity import Entity
from balladeer.lite.loader import Loader
from balladeer.lite.speech import Speech
from balladeer.lite.speech import Prologue
from balladeer.lite.speech import Dialogue
from balladeer.lite.speech import Epilogue
from balladeer.lite.types import Grouping


class Director:
    class Formatter(string.Formatter):
        def convert_field(self, value: str, conversion: str) -> str:
            if conversion == "e":
                return value.translate(Speech.processor.escape_table)
            elif conversion == "x":
                codec = codecs.lookup("rot13")
                rv, length = codec.decode(value)
                return rv
            else:
                return super().convert_field(value, conversion)

    @staticmethod
    def specify_role(spec: dict) -> tuple[set, set, dict, dict]:
        roles = set(filter(None, spec.get("roles", []) + [spec.get("role")]))
        types = set(filter(None, spec.get("types", []) + [spec.get("type")]))
        states = {k: set(v) for k, v in spec.get("states", {}).items()}
        attributes = {
            k: v for k, v in spec.items()
            if k not in ("role", "roles", "type", "types", "state", "states")
            and v in (True, False)
        }
        # TODO: Interpret strings inside parentheses as regex patterns
        try:
            key, value = spec["state"].split(".")
            states.setdefault(key, set()).add(value)
        except AttributeError:
            # Special case for integer state
            value = spec["state"]
            values = set([value]) if isinstance(value, int) else set(value)
            states["int"] = states.get("int", set()).union(values)
        except (KeyError, ValueError):
            pass

        return roles, states, types, attributes

    def __init__(
        self,
        shot_key: str = "_",
        dialogue_key: str = "s",
        pause: float = 1,
        dwell: float = 0.1,
        delay: float = 0,
        offer: float = None,
        **kwargs
    ):
        self.fmtr = self.Formatter()
        self.counts = Counter()
        self.notes = defaultdict(ChainMap)

        self.shot_key = shot_key
        self.dialogue_key = dialogue_key
        self.pause = pause
        self.dwell = dwell
        self.delay = delay
        self.offer = offer

        self.cast = None
        self.role = None

        self.safe_chars = set(string.ascii_letters + string.digits + "-")
        self.bq_matcher = re.compile("<blockquote.*?<\\/blockquote>", re.DOTALL)
        self.tag_matcher = re.compile("<[^>]+?>")
        self.cite_matcher = re.compile(
            """
            (?P<head><cite.*?data-role=")   # Up until role attribute
            (?P<role>[^"]+?)                # Role attribute
            (?P<tail>"[^>]*?)               # Until end of opening tag
            >                               # Close opening tag
            .*?</cite>                      # Text and closing tag
            """,
            re.VERBOSE,
        )
        self.attr_matcher = re.compile('data-([^=]+)=[^"]*"([^"]*)"')
        self.ul_matcher = re.compile("<ul>.*?<\\/ul>", re.DOTALL)
        self.li_matcher = re.compile("<li>.*?<\\/li>", re.DOTALL)
        self.pp_matcher = re.compile("<p>(.*?)<\\/p>", re.DOTALL)

    def attributes(self, text: str) -> dict[str, str]:
        return dict(self.attr_matcher.findall(text))

    def fragments(self, attrs: dict) -> str:
        # NOTE: Subject to change
        return html.unescape(attrs.get("fragments", "")).lstrip("#")

    def directives(self, attrs: dict) -> dict[str, list[str]]:
        lhs, _, rhs = html.unescape(attrs.get("directives", "")).partition("@")
        return {d: [i for i in rhs.split(",") if i] for d in lhs.split(".") if d}

    def mode(self, attrs: dict) -> tuple[str]:
        return tuple(
            i for i in html.unescape(attrs.get("mode", "")).lstrip(":").split("/") if i
        )

    def parameters(self, attrs: dict) -> dict:
        params = urllib.parse.parse_qs(html.unescape(attrs.get("parameters", "").lstrip("?")))
        try:
            offer = float(params.get("offer", [self.offer])[0])
            if offer < 0:
                offer = None
        except TypeError:
            offer = None

        return {
            "label": params.get("label", ""),
            "class": params.get("class", []),
            "style": params.get("style", []),
            "theme": params.get("theme"),
            "pause": float(params.get("pause", [self.pause])[0]),
            "dwell": float(params.get("dwell", [self.dwell])[0]),
            "delay": float(params.get("delay", [self.delay])[0]),
            "offer": offer,
        }

    def handle_fragments(self, html5, fragments: str, path: pathlib.Path | str, shot_id: int, cue_index: int):
        if not fragments:
            return html5
        elif fragments.isdigit():
            self.notes[(path, shot_id, cue_index)]["option"] = int(fragments)
        elif fragments.endswith("!"):
            list_block = self.ul_matcher.search(html5)
            list_items = list(self.li_matcher.findall(list_block.group()))
            ordinal = self.counts[(path, shot_id, cue_index)] % len(list_items)
            choice = list_items[ordinal].replace("<li>", "").replace("</li>", "")
            html5 = self.ul_matcher.sub(choice, html5)
            self.counts[(path, shot_id, cue_index)] += 1

        return html5

    def handle_directives(self, html5, directives: dict, path: pathlib.Path | str, shot_id: int, cue_index: int):
        directive_entry = [
            (
                directive,
                self.cast.get(self.role),
                tuple(filter(None, (self.cast.get(r) for r in roles))),
            )
            for directive, roles in directives.items()
        ]
        try:
            self.notes[(path, shot_id, cue_index)]["directives"].extend(directive_entry)
        except KeyError:
            self.notes[(path, shot_id, cue_index)]["directives"] = directive_entry
        return html5

    def handle_mode(self, html5, mode: list[str], path: pathlib.Path | str, shot_id: int, cue_index: int):
        if mode:
            self.notes[(path, shot_id, cue_index)]["mode"] = mode[0]
            self.notes[(path, shot_id, cue_index)]["media"] = [i for n, i in enumerate(mode) if n]

        return html5

    def handle_parameters(self, html5, parameters: dict, path: pathlib.Path | str, shot_id: int, cue_index: int):
        self.pause = parameters["pause"]
        self.dwell = parameters["dwell"]
        self.offer = parameters["offer"]
        self.notes[(path, shot_id, cue_index)]["style"] = parameters["style"]
        self.notes[(path, shot_id, cue_index)]["theme"] = parameters["theme"]
        self.notes[(path, shot_id, cue_index)]["offer"] = self.offer

        class_values = " ".join(parameters["class"])
        if class_values:
            html5 = html5.replace("<blockquote", f'<blockquote class="{class_values}"', 1)
        if parameters["label"]:
            label = "".join(i for i in "".join(parameters["label"]) if i in self.safe_chars)
            html5 = html5.replace("<blockquote", f'<blockquote id="{label}"', 1)

        return html5

    def rank_constraints(self, spec: dict) -> int:
        roles, states, types, attributes = self.specify_role(spec)
        return sum(1 / len(v) for v in states.values()) + len(types) + len(roles) + len(attributes)

    def edit(
        self,
        speech: Speech = Speech(),
        roles: dict = {},
        path: pathlib.Path | str = None,
        shot_id: int = 0,
    ) -> Generator[str]:
        self.cast = roles.copy()
        for cue_index, block in enumerate(self.bq_matcher.findall(speech.tags)):
            self.notes[(path, shot_id, cue_index)] = self.notes[(path, shot_id, cue_index)].new_child(
                pause=self.pause, duration=self.dwell, delay=self.delay
            )

            html5 = self.cite_matcher.sub(self.edit_cite, block)

            attrs = self.attributes(html5)

            parameters = self.parameters(attrs)
            html5 = self.handle_parameters(html5, parameters, path, shot_id, cue_index)

            fragments = self.fragments(attrs)
            html5 = self.handle_fragments(html5, fragments, path, shot_id, cue_index)

            mode = self.mode(attrs)
            html5 = self.handle_mode(html5, mode, path, shot_id, cue_index)

            directives = self.directives(attrs)
            html5 = self.handle_directives(html5, directives, path, shot_id, cue_index)

            html5 = self.pp_matcher.sub(self.edit_para, html5)

            yield self.fmtr.format(html5, **self.cast)

    def edit_cite(self, match: re.Match) -> str:
        key = list(self.notes)[-1]
        self.notes[key]["type"] = "cue"
        head, self.role, tail = [match.group(i) for i in ("head", "role", "tail")]
        try:
            entity = self.cast[self.role]
        except KeyError:
            return match.group()

        # TODO: New child for notes.
        delay = self.delay + self.pause
        try:
            attr = f'" data-entity="{entity.names[0]}'
            text = entity.names[0].translate(Speech.processor.escape_table)
            self.notes[key]["entity"] = entity
            self.notes[key]["role"] = self.role
            return (
                f'{head}{self.role}{attr}{tail} style="animation-delay: {delay:.2f}s;'
                f' animation-duration: {self.dwell:.2f}s">{text}</cite>'
            )
        except IndexError:
            return match.group()

    def edit_para(self, match: re.Match) -> str:
        content = match.group(1).strip()
        if not content:
            return ""

        words = Speech(content).words
        delay = self.delay + self.pause
        duration = self.dwell * len(words)
        self.delay = delay + duration

        key = list(self.notes)[-1]
        self.notes[key] = self.notes[key].new_child(
            pause=self.pause, duration=duration, delay=self.delay
        )
        return (
            f'<p style="animation-delay: {delay:.2f}s; animation-duration:'
            f' {duration:.2f}s">{content}</p>'
        )

    def roles(self, specs: dict, ensemble: list[Entity]) -> dict[str, Entity]:
        specs = dict(
            sorted(specs.items(), key=lambda x: self.rank_constraints(x[1]), reverse=True)
        )
        pool = {i: set(specs.keys()) for i in ensemble}
        for role, spec in specs.items():
            roles, states, types, attributes = self.specify_role(spec)
            try:
                entity = next(
                    entity
                    for entity, jobs in pool.items()
                    if role in jobs
                    and (
                        not types
                        or entity.types.issuperset(types)
                        or entity.__class__.__name__ in types
                    )
                    and all(
                        k in entity.states
                        and getattr(entity.get_state(k), "name", entity.get_state(k)) in v
                        for k, v in states.items()
                    )
                    and all(
                        bool(getattr(entity, k, not v)) == v
                        for k, v in attributes.items()
                    )
                )
            except StopIteration:
                continue
            else:
                pool[entity] = roles
                yield role, entity

    def specifications(self, toml: dict):
        return {k: v for k, v in toml.items() if isinstance(v, dict) and k != self.shot_key}

    def selection(self, scripts, ensemble: list[Entity] = []):
        for scene in scripts:
            specs = self.specifications(scene.tables)
            roles = dict(self.roles(specs, ensemble))
            if len(specs) and len(roles) == len(specs):
                return scene, specs, roles
        else:
            return Loader.Scene("", {}), {}, {}

    def allows(self, conditions: dict, cast: dict[str, Entity] = {}) -> bool:
        for role, (roles, states, types, attributes) in conditions.items():
            entity = cast[role]
            if (
                types
                and not types.issubset(entity.types)
                and entity.__class__.__name__ not in types
            ):
                return False
            for state, values in states.items():
                try:
                    key = entity.get_state(state).name
                except AttributeError:
                    key = entity.get_state(state)

                if key not in values:
                    return False

            for k, v in attributes.items():
                if bool(getattr(entity, k, not v)) != v:
                    return False

        return True

    def specify_conditions(self, shot: dict) -> Generator[tuple[str, tuple[set, set, dict]]]:
        for role, guard in shot.get("if", {}).items():
            yield role, self.specify_role(guard)

    def dialogue(self, scene: Loader.Scene, roles: dict) -> tuple[int, Dialogue]:
        shots = scene.tables.get(self.shot_key, [])
        for n, shot in enumerate(shots):
            conditions = dict(self.specify_conditions(shot))
            if self.allows(conditions, roles):
                text = shot.get(self.dialogue_key, "")
                yield n, Dialogue(text)

    def rewrite(
        self,
        scene: Loader.Scene = Loader.Scene("", {}),
        roles: dict[str, Entity] = {},
        speech: list[Speech] = [],
    ) -> Generator[tuple[int | None, str]]:
        n_shots = len(scene.tables.get(self.shot_key, [])) if scene else 0
        # Give each piece of programmatic speech an ordinal outside the range of the written scene
        shot_tuples = [
            (t, n_shots + n, s)
            for n, (t, s) in enumerate(
                (t, s) for t, v in Grouping.typewise(speech).items() for s in filter(None, v)
            )
        ]

        # Create a grouping of voiced programmatic speech
        spoken = Grouping(list)
        for t, n, s in shot_tuples:
            for b in self.edit(s, roles, path=None, shot_id=n):
                spoken[t].append((n, b))

        # Interleave programmatic and written dialogue
        spoken[Dialogue] = list(
            itertools.chain.from_iterable(
                itertools.zip_longest(
                    spoken.setdefault(Dialogue, []),
                    [
                        (n, html5)
                        for n, d in self.dialogue(scene, roles)
                        for html5 in self.edit(d, roles, path=scene.path, shot_id=n)
                    ],
                    fillvalue=Speech(),
                )
            )
        )

        self.delay = 0

        f = lambda x: x and x[1]
        yield from filter(f, spoken.get(Prologue, []))
        yield from filter(f, spoken.get(Dialogue, []))
        yield from filter(f, spoken.get(Epilogue, []))
