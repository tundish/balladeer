import time

from balladeer import Drama
from balladeer import Stateful
from balladeer import Story


class Bottles(Drama):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bottles = [
            Stateful().set_state(1),
            Stateful().set_state(1),
            Stateful().set_state(1),
        ]

    @property
    def ensemble(self):
        return self.bottles

    @property
    def unbroken(self):
        return len([i for i in self.bottles if i.state])


drama = Bottles()
drama.folder = ["song.rst"]
story = Story(context=drama)

while drama.unbroken:
    presenter = story.represent()
    for frame in filter(None, presenter.frames):

        animation = presenter.animate(
            frame, dwell=presenter.dwell, pause=presenter.pause
        )
        if not animation: continue

        for line, duration in story.render_frame_to_terminal(animation):
            print(line, "\n")
            time.sleep(duration)
