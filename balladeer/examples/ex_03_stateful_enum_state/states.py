from collections import namedtuple
import enum
import random

from balladeer import DataObject
from balladeer import Stateful

Build = namedtuple("Build", ["luck", "magic", "skill"])


class Caste(enum.Enum):
    mage = Build((5, 8), (7, 10), (3, 7))
    thief = Build((7, 10), (3, 6), (5, 7))
    warrior = Build((3, 6), (5, 8), (7, 10))

    def roll(self):
        return Build(*[random.randint(*i) for i in self.value])


class Actor(DataObject, Stateful):
    pass


player = Actor().set_state(Caste.warrior)
player.build = player.get_state(Caste).roll()

print(player.build)
