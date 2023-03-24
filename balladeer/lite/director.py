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

    def __init__(self, shot_key="_", dlg_key="-"):
        self.shot_key = shot_key
        self.dlg_key = dlg_key

    def select(self, scripts, ensemble=[], roles=1):
        """
        Pick appropriate dialogue files. 
        First selection comes from the Drama.

        This code understands types, roles, states.

        See turberfield-dialogue/turberfield/dialogue/model
        """
        lookup = defaultdict(set)
        for entity in ensemble:
            lookup[entity.__class__.__name__] = entity

        for scene in scripts:
            entities = dict(sorted(
                ((k, v) for k, v in scene.tables.items() if k != self.shot_key),
                key=lambda x: self.constraint_count(x[1]), reverse=True
            ))
            print(entities)
            shots = scene.tables.get(self.shot_key, [])
            return scene

    @staticmethod
    def cast():
        """
        Returns a mapping of roles to entities.

        Assists in processing the 'do' clause.

        """

    @staticmethod
    def prompt(directives):
        """
        Evaluate 'if' clauses.
        Apply formatting to dialogue.

        """
