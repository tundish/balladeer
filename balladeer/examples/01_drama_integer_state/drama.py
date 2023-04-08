import time

from balladeer import Drama
from balladeer import Story


class Bottles(Drama):
    def interlude(self, folder, index, *args, **kwargs):
        self.state = max(0, self.state - 1)
        return self.facts


drama = Bottles().set_state(4)
drama.folder = ["song.rst"]
story = Story(context=drama)

while drama.state:
    presenter = story.represent()
    for frame in filter(None, presenter.frames):
        animation = presenter.animate(frame, dwell=presenter.dwell, pause=presenter.pause)
        if not animation:
            continue

        for line, duration in story.render_frame_to_terminal(animation):
            print(line, "\n")
            time.sleep(duration)
