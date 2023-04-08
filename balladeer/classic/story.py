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

from turberfield.catchphrase.presenter import Presenter
from turberfield.catchphrase.render import Action
from turberfield.catchphrase.render import Parameter
from turberfield.catchphrase.render import Renderer
from turberfield.catchphrase.render import Settings
from turberfield.dialogue.types import DataObject


class Story(Renderer, DataObject):
    def __init__(self, cfg=None, context=None, **kwargs):
        super().__init__(**kwargs)

        # TODO: Settings -> Theme
        # ballad-ink-washout, etc
        self.definitions = {
            "catchphrase-colour-washout": "hsl(50, 0%, 100%, 1.0)",
            "catchphrase-colour-shadows": "hsl(202.86, 100%, 4.12%)",
            "catchphrase-colour-midtone": "hsl(203.39, 96.72%, 11.96%)",
            "catchphrase-colour-hilight": "hsl(203.06, 97.3%, 56.47%)",
            "catchphrase-colour-glamour": "hsl(353.33, 96.92%, 12.75%)",
            "catchphrase-colour-gravity": "hsl(293.33, 96.92%, 12.75%)",
            "catchphrase-reveal-extends": "both",
        }
        self.settings = Settings(**self.definitions)
        self.drama = {} if not context else [context]

    @property
    def actions(self):
        yield Action(
            "cmd",
            None,
            "/{0.id.hex}/cmd/",
            [self],
            "post",
            [Parameter("cmd", False, self.context.validator, [self.context.prompt], ">")],
            "Enter",
        )

    @property
    def context(self):
        return next(iter(self.drama), None)

    def refresh_target(self, url):
        refresh_state = getattr(self.settings, "catchphrase-states-refresh", "inherit").lower()
        if refresh_state == "none":
            return None
        elif refresh_state == "inherit":
            return url
        else:
            return refresh_state

    def represent(self, *args, facts=None, previous=None, factory=Presenter, **kwargs):
        rv = self.context.interlude(
            self.context.folder, previous and previous.index, previous and previous.ensemble
        )
        presenter = factory.build_presenter(
            self.context.folder,
            *args,
            facts=facts or rv,
            ensemble=self.context.ensemble + [self.context, self.settings],
            **kwargs,
        )
        if presenter and not (presenter.dwell or presenter.pause):
            setattr(self.settings, "catchphrase-reveal-extends", "none")
            setattr(self.settings, "catchphrase-states-scrolls", "scroll")
        else:
            setattr(self.settings, "catchphrase-reveal-extends", "both")
            setattr(self.settings, "catchphrase-states-scrolls", "visible")

        return presenter
