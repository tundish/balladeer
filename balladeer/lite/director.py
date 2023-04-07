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


from collections.abc import Generator
from collections import Counter
from collections import defaultdict
import html
import pathlib
import re
import string

from speechmark import SpeechMark

from balladeer.lite.loader import Loader
from balladeer.lite.types import Entity


class Director:
    class Formatter(string.Formatter):
        def __init__(self, spmk, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.spmk = spmk

        def convert_field(self, value: str, conversion: str) -> str:
            if conversion != "a":
                return super().convert_field(value, conversion)
            else:
                return value.translate(self.spmk.escape_table)

    @staticmethod
    def specify_role(spec: dict) -> tuple[set, set, dict]:
        roles = set(filter(None, spec.get("roles", []) + [spec.get("role")]))
        types = set(filter(None, spec.get("types", []) + [spec.get("type")]))
        states = {k: set(v) for k, v in spec.get("states", {}).items()}
        try:
            key, value = spec["state"].split(".")
            states.setdefault(key, set()).add(value)
        except (KeyError, ValueError):
            pass

        return roles, states, types

    def specify_conditions(
        self, shot: dict
    ) -> Generator[tuple[str, tuple[set, set, dict]]]:
        for role, guard in shot.get("if", {}).items():
            yield role, self.specify_role(guard)

    def __init__(self, story, shot_key: str = "_", dlg_key: str = "s"):
        self.spmk = SpeechMark()
        self.fmtr = self.Formatter(self.spmk)
        self.counts = Counter()

        self.story = story
        self.shot_key = shot_key
        self.dlg_key = dlg_key
        self.bq_matcher = re.compile("<blockquote.*?<\\/blockquote>", re.DOTALL)
        self.tag_matcher = re.compile("<[^>]+?>")
        self.cite_matcher = re.compile(
            """
            (?P<head><cite.*?data-role=")   # Up until role attribute
            (?P<role>[^"]+?)                # Role attribute
            (?P<tail>"[^>]*?>)              # Until end of opening tag
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

    def rank_constraints(self, spec: dict) -> int:
        roles, states, types = Director.specify_role(spec)
        return sum(1 / len(v) for v in states.values()) + len(types) - len(roles)

    def lines(self, html5: str) -> list[str]:
        text = self.tag_matcher.sub("", html5)
        return list(filter(None, (i.strip() for i in text.splitlines())))

    def words(self, html5: str) -> list[str]:
        return " ".join(self.lines(html5)).split(" ")

    def edit(self, html5: str, roles: dict={}, path: pathlib.Path | str=None, index:int=0) -> Generator[str]:
        self.cast = roles.copy()
        for block in self.bq_matcher.findall(html5):
            html5 = self.cite_matcher.sub(self.edit_cite, block)

            attrs = self.attributes(html5)

            # TODO: Dispatch to a handler for fragment?
            if attrs.get("fragments", "").endswith("!"):
                list_block = self.ul_matcher.search(html5)
                list_items = list(self.li_matcher.findall(list_block.group()))
                ordinal = self.counts[(path, index)] % len(list_items)
                choice = list_items[ordinal].replace("<li>", "").replace("</li>", "")
                html5 = self.ul_matcher.sub(choice, html5)
                self.counts[(path, index)] += 1

            html5 = self.pp_matcher.sub(self.edit_para, html5)
            yield self.fmtr.format(html5, **self.cast)

    def edit_cite(self, match: re.Match) -> str:
        head, role, tail = [match.group(i) for i in ("head", "role", "tail")]
        try:
            entity = self.cast[role]
        except KeyError:
            return match.group()

        try:
            attr = f'" data-entity="{entity.names[0]}'
            text = entity.names[0].translate(self.spmk.escape_table)
            return f"{head}{role}{attr}{tail}{text}</cite>"
        except IndexError:
            return match.group()

    def edit_para(self, match: re.Match) -> str:
        content = match.group(1).strip()
        return content and f"<p>{content}</p>"

    def selection(self, scripts, ensemble: list[Entity] = [], roles=1):
        for scene in scripts:
            specs = self.specifications(scene.tables)
            roles = dict(self.roles(specs, ensemble))
            if len(roles) == len(specs):
                return scene, roles

    def specifications(self, toml: dict):
        return {
            k: v for k, v in toml.items() if isinstance(v, dict) and k != self.shot_key
        }

    def roles(self, specs: dict, ensemble: list[Entity]) -> dict[str, Entity]:
        specs = dict(
            sorted(
                specs.items(), key=lambda x: self.rank_constraints(x[1]), reverse=True
            )
        )
        pool = {i: set(specs.keys()) for i in ensemble}
        for role, spec in specs.items():
            roles, states, types = self.specify_role(spec)
            try:
                entity = next(
                    entity
                    for entity, jobs in pool.items()
                    if role in jobs
                    and (
                        not types
                        or entity.types.intersection(types)
                        or entity.__class__.__name__ in types
                    )
                    and all(
                        k in entity.states and entity.get_state(k).name in v
                        for k, v in states.items()
                    )
                )
            except StopIteration:
                continue
            else:
                pool[entity] = roles
                yield role, entity

    def rewrite(self, scene, roles: dict[str, Entity] = {}) -> str:
        shots = scene.tables.get(self.shot_key, [])
        for n, shot in enumerate(shots):
            conditions = dict(self.specify_conditions(shot))
            if self.allows(conditions, roles):
                text = shot.get(self.dlg_key, "")
                html5 = self.spmk.loads(text)
                edit = "\n".join(self.edit(html5, roles, path=scene.path, index=n))
                return "\n".join(i for i in edit.splitlines() if i.strip())
        else:
            return ""

    def allows(self, conditions: dict, cast: dict[str, Entity] = {}) -> bool:
        for role, (roles, states, types) in conditions.items():
            entity = cast[role]
            if (
                types
                and not types.issubset(entity.types)
                and entity.__class__.__name__ not in types
            ):
                return False
            for state, values in states.items():
                if entity.get_state(state).name not in values:
                    return False

        return True
