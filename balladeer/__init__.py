import datetime
import importlib.metadata

try:
    import tomllib
except ImportError:
    import tomli as tomllib


try:
    __version__ = importlib.metadata.version("balladeer")
except importlib.metadata.PackageNotFoundError:
    __version__ = datetime.date.today().strftime("%Y.%m.%d") + "+local_repository"

"""
from balladeer.classic.drama import Drama
from balladeer.classic.gesture import Gesture
from balladeer.classic.gesture import Hand
from balladeer.classic.gesture import Head
from balladeer.classic.speech import Article
from balladeer.classic.speech import Name
from balladeer.classic.speech import Phrase
from balladeer.classic.speech import Pronoun
from balladeer.classic.speech import Verb
from balladeer.classic.story import Story
from balladeer.classic.types import Fruition
from balladeer.classic.types import Grouping
from balladeer.classic.types import Named
from balladeer.classic.types import World
"""
