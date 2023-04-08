import time

from balladeer import Drama
from balladeer import Stateful
from balladeer import Story


class Bottles(Drama):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.population = [
            Stateful().set_state(1),
            Stateful().set_state(1),
            Stateful().set_state(1),
        ]

    @property
    def ensemble(self):
        return self.population

    @property
    def count(self):
        return len([i for i in self.population if i.state])


drama = Bottles()
drama.folder = ["song.rst"]
story = Story(context=drama)

while True:
    stop = not drama.count
    presenter = story.represent(strict=False)

    animation = next(
        filter(
            None,
            (
                presenter.animate(frame, dwell=presenter.dwell, pause=presenter.pause)
                for frame in presenter.frames
            ),
        )
    )

    for line, duration in story.render_frame_to_terminal(animation):
        print(line, "\n")
        time.sleep(duration)

    if stop:
        break
