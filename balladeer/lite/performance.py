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
from collections.abc import Callable
import difflib
import enum
import inspect
import itertools
import string

from balladeer.lite.entity import Entity
from balladeer.lite.types import Grouping


class Performance:
    discard = ("a", "an", "any", "her", "his", "my", "some", "the", "their")

    @staticmethod
    def unpack_annotation(name, annotation, ensemble, parent=None):
        if isinstance(annotation, str) and parent:
            f = string.Formatter()
            annotation, _ = f.get_field(f"0.{annotation}", [parent], {})

        if not isinstance(annotation, list):
            terms = [annotation]
        else:
            terms = annotation

        for t in terms:
            if isinstance(t, type):
                if issubclass(t, enum.Enum):
                    yield from (
                        (name, i)
                        for i in t
                        for v in ([i.value] if isinstance(i.value, str) else i.value)
                    )
                else:
                    yield from ((name, i) for i in ensemble if isinstance(i, t))
            else:
                yield (name, t)

    @staticmethod
    def parse_tokens(text, preserver=".", discard=None):
        discard = discard or set()
        return [
            i.strip()
            for i in text.rstrip(preserver).lower().split()
            if i not in discard or text.endswith(preserver)
        ]

    @staticmethod
    def expand_commands(method, ensemble=[], parent=None):
        """
        Read a method's docstring and expand it to create all possible matching
        command phrases. Calculate the corresponding keyword arguments.

        Generates pairs of each command with a 2-tuple; (method, keyword arguments).

        """
        doc = method.func.__doc__ if hasattr(method, "func") else method.__doc__ or ""
        terms = list(
            filter(None, (i.strip() for line in doc.splitlines() for i in line.split("|")))
        )
        params = list(
            itertools.chain(
                list(Performance.unpack_annotation(p.name, p.annotation, ensemble, parent))
                for p in inspect.signature(method, follow_wrapped=True).parameters.values()
                if p.annotation != inspect.Parameter.empty
            )
        )
        cartesian = [dict(i) for i in itertools.product(*params)]
        for term in terms:
            tokens = Performance.parse_tokens(term, discard=Performance.discard)
            for prod in cartesian:
                try:
                    yield (" ".join(tokens).format(**prod).lower(), (method, prod))
                except (AttributeError, IndexError, KeyError) as e:
                    continue

    def __call__(self, fn, *args, **kwargs):
        yield from fn(fn, *args, **kwargs)

    def options(
        self, ensemble: list[Entity], prefix="do_"
    ) -> Grouping[str, list[tuple[Callable, dict[str, Entity]]]]:
        if not hasattr(self, "active"):
            self.active = dict(
                (i, set())
                for i in (getattr(self, name) for name in dir(self) if name.startswith(prefix))
                if isinstance(i, Callable)
            )

        rv = Grouping(list)
        for fn, commands in self.active.items():
            commands.clear()
            for k, v in self.expand_commands(fn, ensemble, parent=self):
                commands.add(k)
                rv[k].append(v)
        return rv

    def pick(self, options):
        return next(iter(options), (None,) * 3)

    def actions(self, text, context=None, ensemble=[], prefix="do_", cutoff=0.95):
        options = self.options(ensemble, prefix=prefix)

        tokens = self.parse_tokens(text, discard=self.discard)
        matches = difflib.get_close_matches(
            " ".join(tokens), options, cutoff=cutoff
        ) or difflib.get_close_matches(text.strip(), options, cutoff=cutoff)
        try:
            yield from ((fn, [text, context], kwargs) for fn, kwargs in options[matches[0]])
        except (IndexError, KeyError):
            yield (None, [text, context], {})
