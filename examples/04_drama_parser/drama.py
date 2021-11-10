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
        self.active.add(self.do_bottle)
        self.active.add(self.do_look)
        self.prompt = ">"

    @property
    def ensemble(self):
        return self.population

    @property
    def count(self):
        return len(self.unbroken)

    @property
    def unbroken(self):
        return [i for i in self.population if i.get_state(Fruition) == Fruition.inception]

    def do_bottle(self, this, text, presenter, *args, **kwargs):
        """
        bottle

        """
        try:
            self.unbroken[0].state = Fruition.completion
        except IndexError:
            pass

    def do_look(self, this, text, presenter, *args, **kwargs):
        """
        look

        """
        self.prompt = ">"
        return


drama = Bottles()
drama.folder = ["song.rst", "end.rst"]
story = Story(context=drama)

text = ""
presenter = None
while True:
    stop = not drama.count
    presenter = story.represent(text, previous=presenter)

    for animation in filter(None, (presenter.animate(
        frame, dwell=presenter.dwell, pause=presenter.pause
    ) for frame in presenter.frames)):

        for line, duration in story.render_frame_to_terminal(animation):
            print(line, "\n")
            time.sleep(duration)

    if stop:
        break

    cmd = input("{0} ".format(story.context.prompt))
    text = story.context.deliver(cmd, presenter=presenter)
