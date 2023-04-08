#!/usr/bin/env python3
#   encoding: utf-8

# This is part of the Balladeer library.
# Copyright (C) 2021 D E Haynes

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

import bisect
import re

from turberfield.catchphrase.mediator import Mediator
from turberfield.dialogue.model import Model
from turberfield.dialogue.types import Stateful


class Drama(Stateful, Mediator):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.validator = re.compile("[\\w ]+")
        self.prompt = "?"
        self.input_text = ""
        self.default_fn = None
        self.valid_states = [0]

    @property
    def ensemble(self):
        return []

    @property
    def turns(self):
        return len(self.history)

    def __call__(self, fn, *args, **kwargs):
        text, presenter, *_ = args
        # FIXME: Bring in Operation and test for paused.
        if presenter and (presenter.dwell or presenter.pause):
            self.valid_states = self.find_valid_states(presenter)

        return super().__call__(fn, *args, **kwargs)

    def build(self):
        return []

    def find_valid_states(self, presenter):
        return sorted(
            c.value
            for f in presenter.frames
            for c in f[Model.Condition]
            if c.object is self and c.format == "state" and isinstance(c.value, int)
        ) or [0]

    def next_states(self, n=1):
        fwd = min(
            bisect.bisect_right(self.valid_states, self.state) + n - 1,
            len(self.valid_states) - 1,
        )
        bck = max(0, bisect.bisect_left(self.valid_states, self.state) - n)
        rv = (self.valid_states[bck], self.valid_states[fwd])
        return rv

    def interlude(self, folder, index, *args, **kwargs):
        return {}

    def deliver(self, cmd, presenter):
        self.input_text = cmd
        fn, args, kwargs = self.interpret(
            self.match(cmd, context=presenter, ensemble=self.ensemble)
        )
        fn = fn or self.default_fn
        return fn and self(fn, *args, **kwargs)
