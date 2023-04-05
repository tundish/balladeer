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


from collections import defaultdict
import html
import re
import string

from speechmark import SpeechMark

from balladeer.lite.types import Entity


class Director:
    #   TODO: Director detects media files for preload, prefetch.
    #   Think of hex grid map. Get resources for neighbours.
    #   So every Entity declares resources to a Stage?

    class Formatter(string.Formatter):

        def __init__(self, spmk, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.spmk = spmk

        def convert_field(self, value, conversion):
            if conversion != "a":
                return super().convert_field(value, conversion)
            else:
                return value.translate(self.spmk.escape_table)

    @staticmethod
    def specify_role(spec: dict) -> tuple:
        roles = set(filter(None, spec.get("roles", []) + [spec.get("role")]))
        types = set(filter(None, spec.get("types", []) + [spec.get("type")]))
        states = {k: set(v) for k, v in spec.get("states", {}).items()}
        try:
            key, value = spec["state"].split(".")
            states.setdefault(key, set()).add(value)
        except (KeyError, ValueError):
            pass

        return roles, states, types

    def specify_conditions(self, shot: dict) -> tuple:
        for role, guard in shot.get("if", {}).items():
            print(f"Role: {role}, G: {guard} => {self.specify_role(guard)}")
            yield role, self.specify_role(guard)

    def __init__(self, story, shot_key="_", dlg_key="s"):
        self.spmk = SpeechMark()
        self.fmtr = self.Formatter(self.spmk)

        self.story = story
        self.shot_key = shot_key
        self.dlg_key = dlg_key
        self.tag_matcher = re.compile("<[^>]+?>")
        self.cite_matcher = re.compile(
        """
        (?P<head><cite.*?data-role=")   # Up until role attribute
        (?P<role>[^"]+?)                # Role attribute
        (?P<tail>"[^>]*?>)              # Until end of opening tag
        .*?</cite>                      # Text and closing tag
        """, re.VERBOSE
        )

    def rank_constraints(self, spec: dict) -> int:
        roles, states, types = Director.specify_role(spec)
        return sum(1 / len(v) for v in states.values()) + len(types) - len(roles)

    def lines(self, html5: str) -> list:
        text = self.tag_matcher.sub("", html5)
        return list(filter(None, (i.strip() for i in text.splitlines())))

    def words(self, html5: str) -> list:
        return " ".join(self.lines(html5)).split(" ")

    def edit(self, html5: str, roles: dict) -> str:
        self.cast = roles.copy()
        html5 = self.cite_matcher.sub(self.edit_cite, html5)
        return self.fmtr.format(html5, **self.cast)

    def edit_cite(self, match: re.Match):
        head, role, tail = [match.group(i) for i in ("head", "role", "tail")]
        try:
            entity = self.cast[role]
        except KeyError:
            return match.group()

        attr = f'" data-entity="{entity.names[0]}'
        text = entity.names[0].translate(self.spmk.escape_table)
        return f"{head}{role}{attr}{tail}{text}</cite>"

    def selection(self, scripts, ensemble: list[Entity]=[], roles=1):
        for scene in scripts:
            specs = self.specifications(scene.tables)
            roles = dict(self.roles(specs, ensemble))
            if len(roles) == len(specs):
                return scene, roles

    def specifications(self, toml: dict):
        return {
            k: v
            for k, v in toml.items()
            if isinstance(v, dict)
            and k != self.shot_key
        }

    def roles(self, specs: dict, ensemble: list[Entity]) -> dict:
        specs = dict(sorted(
            specs.items(),
            key=lambda x: self.rank_constraints(x[1]), reverse=True
        ))
        pool = {i: set(specs.keys()) for i in ensemble}
        for role, spec in specs.items():
            roles, states, types = self.specify_role(spec)
            try:
                entity = next(
                    entity
                    for entity, jobs in pool.items()
                    if role in jobs and (
                        not types
                        or entity.types.intersection(types)
                        or entity.__class__.__name__ in types
                    )
                    and all(
                        k in entity.states
                        and entity.get_state(k).name in v
                        for k, v in states.items()
                    )
                )
            except StopIteration:
                continue
            else:
                pool[entity] = roles
                yield role, entity

    def rewrite(self, scene, roles: dict[str, Entity]={}):
        shots = scene.tables.get(self.shot_key, [])
        for shot in shots:
            # TODO: Evaluate conditions for shot
            if self.allows(shot):
                text = shot.get(self.dlg_key, "")
                html5 = self.spmk.loads(text)
                yield self.edit(html5, roles)

    def allows(self, shot, roles: dict[str, Entity]={}):
        criteria = dict(self.specify_conditions(shot))
        print(f"Criteria {criteria}")
        for role, (roles, states, types) in criteria.items():
            entity = roles[role]
            print(f"Entity: {entity} Role: {role} states:  {states}, types: {types}")
            if types and not types.issubset(entity.types):
                return False
            for state, values in states.items():
                if entity.get_state(state).name not in values:
                    return False
                

        return True

    def compare(self, key: str, pattern: [str, re.Pattern]):
        pass
