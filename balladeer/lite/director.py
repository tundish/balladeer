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


class Director:
    #   TODO: Director detects media files for preload, prefetch.
    #   Think of hex grid map. Get resources for neighbours.
    #   So every Location declares resources to a Stage?

    @staticmethod
    def constraint_count(entity):
        n = 1 if "type" in entity else 0
        return len(entity.get("states", [])) + n

    def __init__(self, story, shot_key="_", dlg_key="D"):
        self.story = story
        self.shot_key = shot_key
        self.dlg_key = dlg_key

    def selection(self, scripts, ensemble=[], roles=1):
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
                key=lambda x: self.constraint_count(x[1]), reverse=True
            ))
            cast = {k: lookup.get(role["type"]).pop() for k, role in roles.items() if "type" in role}
            return scene, cast

    def rewrite(self, scene, selection: dict={}):
        # TODO: replace/retain <cite data-role="FIGHTER_1">FIGHTER_1</cite>
        shots = scene.tables.get(self.shot_key, [])
        for shot in shots:
            dialogue = shot.get(self.dlg_key, "")
            shot[self.dlg_key] = dialogue.format(**selection)
            yield shot

    def allows(self, shot):
        return True
