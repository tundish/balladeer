from balladeer import Drama
from balladeer import Story

drama = Drama()
drama.folder = ["hello.rst"]
story = Story(context=drama)

presenter = story.represent()

for frame in presenter.frames:
    animation = presenter.animate(frame)

    for line, duration in story.render_frame_to_terminal(animation):
        print(line)
