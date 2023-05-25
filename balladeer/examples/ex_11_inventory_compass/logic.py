import enum
from itertools import repeat
import random

from turberfield.dialogue.model import SceneScript
from turberfield.dialogue.types import EnumFactory
from turberfield.dialogue.types import DataObject
from turberfield.dialogue.types import Stateful

@enum.unique
class Location(EnumFactory, enum.Enum):
    foyer = 0
    bar = 1
    cloakroom_floor = 2
    cloakroom_space = 3
    cloakroom_hook = 4

class Narrator(Stateful):
    pass

class Cloak(Stateful):
    pass

class Prize(Stateful, DataObject):
    pass


ensemble = [
    Narrator().set_state(Location.foyer),
    Cloak().set_state(Location.foyer).set_state(1),
    Prize(message="You win!")
]


def parse_command(cmd):
    try:
        return cmd.strip().split(" ")[-1][0].lower()
    except (AttributeError, IndexError):
        return None


def interaction(folder, index, ensemble, cmd="", log=None, loop=None):
    narrator, cloak, prize, *others = ensemble
    locn = narrator.get_state(Location)
    action = None
    if locn == Location.foyer:
        while action not in ("s", "w", "q"):
            action = parse_command(cmd or input("Enter a command: "))
        if action == "s":
            narrator.set_state(Location.bar)
            if cloak.get_state(Location) == locn:
                prize.set_state(0)
            else:
                prize.set_state(1)
        elif action == "w":
            narrator.set_state(Location.cloakroom_space)
            cloak.set_state(1)
        else:
            return None
    elif locn == Location.bar:
        while action != "n":
            action = parse_command(cmd or input("Enter a command: "))

        narrator.set_state(Location.foyer)
        prize.message = prize.message.replace(
            random.choice(prize.message), " ", 1
        )
        prize.set_state(0)
    elif locn == Location.cloakroom_space:
        while action not in ("c", "h", "e"):
            action = parse_command(cmd or input("Enter a command: "))
        if action == "c":
            if cloak.get_state(Location) == Location.cloakroom_space:
                cloak.set_state(Location.cloakroom_floor)
            else:
                cloak.set_state(Location.cloakroom_space)
        elif action == "h":
            cloak.set_state(Location.cloakroom_hook)
        else:
            narrator.set_state(Location.foyer)
            if cloak.get_state(Location) != locn:
                cloak.set_state(0)

    if cloak.get_state(Location) == locn:
        cloak.set_state(narrator.get_state(Location))
        cloak.set_state(1)

    return folder.metadata


references = ensemble + [Location]

folder = SceneScript.Folder(
    pkg=__name__,
    description="The 'Hello World' of text games.",
    metadata={},
    paths=["foyer.rst", "bar.rst", "cloakroom.rst"],
    interludes=repeat(interaction)
)
