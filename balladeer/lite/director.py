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
            if conversion != "s":
                return super().convert_field(value, conversion)
            else:
                return value.translate(self.spmk.escape_table)

    @staticmethod
    def rank_constraints(entity: Entity):
        n = 1 if "type" in entity else 0
        return len(entity.get("states", [])) + n

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
        self.cast = None

    def edit_cite(self, match: re.Match):
        head, role, tail = [match.group(i) for i in ("head", "role", "tail")]
        try:
            entity = self.cast[role]
        except KeyError:
            return match.group()

        attr = f'" data-entity="{entity.names[0]}"'
        text = entity.names[0].translate(self.spmk.escape_table)
        return f"{head}{role}{attr}{tail}{text}</cite>"

    def lines(self, html5: str) -> list:
        text = self.tag_matcher.sub("", html5)
        return list(filter(None, (i.strip() for i in text.splitlines())))

    def words(self, html5: str) -> list:
        return " ".join(self.lines(html5)).split(" ")

    def edit(self, html5: str, selection: dict) -> str:
        self.cast = selection.copy()
        html5 = self.cite_matcher.sub(self.edit_cite, html5)
        return self.fmtr.format(html5, **self.cast)

    def selection(self, scripts, ensemble: list[Entity]=[], roles=1):
        """
        Pick appropriate dialogue files. 
        First selection comes from the Drama.

        This code understands types, roles, states.

        See turberfield-dialogue/turberfield/dialogue/model
        """
        lookup = defaultdict(set)
        for entity in ensemble:
            try:
                lookup[entity.__class__.__name__].add(entity)  # Classic
            except TypeError:
                # eg: SimpleNamespace is unhashable
                pass

            if hasattr(entity, "type"):
                lookup[entity.type].add(entity) # Lite

        for scene in scripts:
            roles = dict(sorted(
                ((k, v) for k, v in scene.tables.items() if k != self.shot_key),
                key=lambda x: self.rank_constraints(x[1]), reverse=True
            ))
            cast = {k: lookup.get(role["type"]).pop() for k, role in roles.items() if "type" in role}
            return scene, cast

    def rewrite(self, scene, selection: dict[str, Entity]={}):
        shots = scene.tables.get(self.shot_key, [])
        for shot in shots:
            dialogue = shot.get(self.dlg_key, "")
            shot[self.dlg_key] = self.edit(dialogue, selection)
            yield shot

    def allows(self, shot):
        return True
