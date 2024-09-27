#!/usr/bin/env python3
#   encoding: utf-8

# This is part of the Balladeer library.
# Copyright (C) 2024 D E Haynes

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
#!/usr/bin/env python
# encoding: utf8

import pathlib
import unittest
from unittest.mock import Mock

from starlette.applications import Starlette
from starlette.datastructures import State
from starlette.requests import Request

from balladeer import Dialogue
from balladeer import Page
from balladeer import Presenter
from balladeer import Session
from balladeer import StoryBuilder


class ActionButtonTests(unittest.TestCase):

    @staticmethod
    def mock_request():
        request = Mock(spec=Request)
        request.app = Mock(spec=Starlette)
        request.app.state = Mock(spec=State)
        request.app.state.static = pathlib.Path(".")
        request.app.state.presenter = Presenter()
        return request

    class TestStory(StoryBuilder):
        pass

    def test_command_form(self):

        story = self.TestStory(
            Dialogue("<> Perhaps it's time to go to bed?"),
        )

        page = Page()
        request = self.mock_request()
        endpoint = Session(dict(type="http"), None, None)

        with story.turn() as turn:
            page = endpoint.compose(request, page, story, turn)
        lines = page.html.splitlines()

        command_form = next(
            (i for i in lines if i.startswith("<form") and 'name="ballad-command-form"' in i),
            None
        )
        self.assertTrue(command_form, lines)

    def test_code_implies_action(self):

        story = self.TestStory(
            Dialogue("<> Perhaps it's time to `go to bed`?"),
        )

        page = Page()
        request = self.mock_request()
        endpoint = Session(dict(type="http"), None, None)
        with story.turn() as turn:
            page = endpoint.compose(request, page, story, turn)
        lines = page.html.splitlines()

        command_form = next(
            (i for i in lines if i.startswith("<form") and 'name="ballad-command-form"' in i),
            None
        )
        self.assertTrue(command_form, lines)

        action_button = next(
            (i for i in lines if "<button" in i and 'form="ballad-action-form-go-to-bed"' in i),
            None
        )
        self.assertTrue(action_button, lines)
        action_form = next(
            (i for i in lines if i.startswith("<form") and 'id="ballad-action-form-go-to-bed"' in i),
            None
        )
        self.assertTrue(action_form, lines)
