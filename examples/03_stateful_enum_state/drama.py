import time

from balladeer import Drama
from balladeer import Fruition
from balladeer import Stateful
from balladeer import Story


class Bottles(Drama):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.population = [
            Stateful().set_state(Fruition.inception),
            Stateful().set_state(Fruition.inception),
            Stateful().set_state(Fruition.inception),
        ]

    @property
    def ensemble(self):
        return self.population

    @property
    def unbroken(self):
        return len(
            [i for i in self.population if i.get_state(Fruition) == Fruition.inception]
        )


drama = Bottles()
drama.folder = ["song.rst", "end.rst"]
story = Story(context=drama)

presenter = None
while True:
    stop = not drama.unbroken
    presenter = story.represent(previous=presenter)

    for animation in filter(None, (presenter.animate(
        frame, dwell=presenter.dwell, pause=presenter.pause
    ) for frame in presenter.frames)):

        for line, duration in story.render_frame_to_terminal(animation):
            print(line, "\n")
            #time.sleep(duration)

    if stop:
        break
