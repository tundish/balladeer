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

import dataclasses
import enum
import json
import random
import re
from typing import Type
import uuid

from balladeer.lite.speech import Speech
from balladeer.lite.types import State


@dataclasses.dataclass(kw_only=True, unsafe_hash=True)
class Entity:
    """
    All parameters are optional. Without any, you'll get
    an anonymous Entity which is unique by virtue
    of its `uid`:

    >>> Entity()
    Entity(names=[], types=set(), states={}, uid=UUID('76f72aba-056c-4d84-9da0-7e8c8451cf7e'), links=set(), sketch='', aspect='', revert='')

    As a convenience you can pass an Entity a single
    `name` argument, but note how this is stored in
    the `names` attribute of the created object:

    >>> Entity(name="Anna")
    Entity(names=['Anna'], types=set(), states={}, uid=UUID('0797bd07-9cdc-47c0-9cae-f6cae5d69ded'), links=set(), sketch='', aspect='', revert='')

    Of course, you can do this:

    >>> Entity(names=["Bob", "Robert"])
    Entity(names=['Bob', 'Robert'], types=set(), states={}, uid=UUID('bc8ba6bf-565e-4588-97cc-337dd54bdc31'), links=set(), sketch='', aspect='', revert='')

    Entity `type` works the same way, except the supporting structure is a *set*. The declared types
    of an entity should all be strings:

    >>> Entity(name="Chuck", type="Squirrel")
    Entity(names=['Chuck'], types={'Squirrel'}, states={}, uid=UUID('5aab38be-3147-4647-a635-c999943ff017'), links=set(), sketch='', aspect='', revert='')

    >>> Entity(name="Chuck", types={"Squirrel", "Cartoon"})
    Entity(names=['Chuck'], types={'Squirrel', 'Cartoon'}, states={}, uid=UUID('a468f8e5-1372-45a1-8795-dab5be51902a'), links=set(), sketch='', aspect='', revert='')

    Entity objects have a `links` attribute, which allows you to associate one Entity with another.

    >>> a, b = (Entity(), Entity())
    >>> a.links.add(b.uid)
    Entity(names=[], types=set(), states={}, uid=UUID('e594b6ad-88df-4199-9694-18acc788b81d'), links={UUID('aa66771b-5ba6-40fe-857d-d7c57099a013')}, sketch='', aspect='', revert='')

    To delete a link:

    >>> a.links.discard(b.uid)

    There are three :py:class:`~balladeer.lite.speech.Speech` attributes, which you can modify at any time:

    aspect
        Here you can record this entity's most recent mood or disposition.

    revert
        This is a backup for a previous `aspect`, so you can revert to it after a temporary change.

    sketch
        This is a piece of speech which should be *always true*
        of the entity object. It will be processed as a
        `string with format specifiers
        <file:///home/boss/Documents/python-3.10.5-docs-html/library/string.html#formatstrings>`_.
        It may contain named arguments to reference `names`, `aspect`, etc.

    """
    name: dataclasses.InitVar = ""
    names: list = dataclasses.field(default_factory=list, compare=False)

    type: dataclasses.InitVar = ""
    types: set = dataclasses.field(default_factory=set, compare=False)

    states: dict = dataclasses.field(default_factory=dict, compare=False)

    uid: uuid.UUID = dataclasses.field(default_factory=uuid.uuid4)
    links: set = dataclasses.field(default_factory=set, compare=False)

    sketch: Speech = dataclasses.field(default_factory=Speech, compare=False)
    aspect: Speech = dataclasses.field(default_factory=Speech, compare=False)
    revert: Speech = dataclasses.field(default_factory=Speech, compare=False)

    def __post_init__(self, name, type):
        # Unfortunately the builtin 'type' can't be used here
        if name and not isinstance(name, property):
            self.names.insert(0, name)
        if type and not isinstance(type, property):
            try:
                self.types.add(type.__name__)
            except AttributeError:
                self.types.add(type)

    def __deepcopy__(self, memo):
        return self.__class__(
            names=self.names.copy(),
            types=self.types.copy(),
            states=self.states.copy(),
            links=self.links.copy(),
            sketch=self.sketch,
            aspect=self.aspect,
        )

    def __eq__(self, other):
        if not self.names:
            return self.uid == other.uid

        try:
            return set(self.names).union(self.types) == set(other.names).union(other.types)
        except AttributeError:
            return False

    class Encoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, enum.Enum):
                return {"name": obj.name, "value": obj.value}

            data = dataclasses.asdict(obj)
            data["uid"] = str(data["uid"])
            data["types"] = sorted(data.get("types", []))
            data["links"] = sorted((str(i) for i in data.get("links", [])))
            return data

    @property
    def name(self) -> str:
        "Return a random choice of the object's declared names."
        return random.choice(self.names or [""])

    @property
    def description(self) -> str:
        "Return a description of the object based on its `sketch` and other attributes"
        return self.sketch.format(self, **dataclasses.asdict(self))

    def set_state(self, *args: tuple[State | int]):
        """
        Set a state value on the object.

        >>> entity = Entity()
        >>> entity.set_state(Politics.ind)
        Entity(names=[], types=set(), states={'Politics': <Politics.ind: ['Independent']>}, uid=UUID('4f02535e-b386-400c-9297-350fd73cd6fa'), links=set(), sketch='', aspect='', revert='')

        As a special case, an argument of type `int` is also considered a state value:

        >>> entity = Entity()
        >>> entity.set_state(12)
        Entity(names=[], types=set(), states={'int': 12}, uid=UUID('4f02535e-b386-400c-9297-350fd73cd6fa'), links=set(), sketch='', aspect='', revert='')

        You may supply multiple state values to this method.

        >>> entity = Entity()
        >>> entity.set_state(Politics.ind, 12)
        Entity(names=[], types=set(), states={'Politics': <Politics.ind: ['Independent']>, 'int': 12}, uid=UUID('4f02535e-b386-400c-9297-350fd73cd6fa'), links=set(), sketch='', aspect='', revert='')

        The return value is the entity object, allowing a declarative style of state assignment as follows:

        >>> entity = Entity().set_state(Politics.ind, 12)

        """
        for arg in args:
            self.states[type(arg).__name__] = arg
        return self

    def get_state(self, typ: State | str = int):
        """
        Get a state by type or type name.

        >>> entity.get_state(Politics)
        <Politics.ind: ['Independent']>

        >>> entity.get_state("Politics")
        <Politics.ind: ['Independent']>

        >>> entity.get_state(int)
        12

        >>> entity.get_state("int")
        12

        This method returns `None` if the state type is not set on the object.

        """
        try:
            return self.states.get(typ.__name__)
        except AttributeError:
            return self.states.get(typ)
        else:
            return None

    @property
    def state(self):
        """
        This property provides an alternative idiom when allocating a single state:

        >>> entity.state = Politics.ind

        When used to access state, it will return integer state only:

        >>> entity.state
        12

        """
        return self.get_state()

    @state.setter
    def state(self, value):
        return self.set_state(value)

