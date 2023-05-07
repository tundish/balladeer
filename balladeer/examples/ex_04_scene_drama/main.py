#!/usr/bin/env python3
#   encoding: utf-8

from balladeer.lite.app import quick_start
from balladeer.lite.drama import Drama
from balladeer.lite.speech import Dialogue
from balladeer.lite.story import StoryBuilder


class Wall(Drama):
    def do_bottle(self, this, text, director, *args, **kwargs):
        """
        bottle
        break | break bottle

        """
        try:
            self.state = max(0, self.state - 1)
            yield Dialogue(
                """
                <>  And if one green bottle should *accidentally* fall,
                There'll be...
                """
            )

        except IndexError:
            pass

    def do_look(self, this, text, director, *args, **kwargs):
        """
        look

        """
        yield Dialogue("<> Singing...")


class Story(StoryBuilder):
    title = "Balladeer Example: Scene and Drama"
    def build(self):
        yield Wall(world=self.world, config=self.config).set_state(10)


if __name__ == "__main__":
    quick_start(__file__)
