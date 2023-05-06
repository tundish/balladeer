import time

from balladeer.lite.speech import Dialogue
from balladeer.lite.story import StoryBuilder


story = StoryBuilder(
    Dialogue("Here's a joke..."),
    Dialogue("<ADAM> Knock, knock."),
    Dialogue("<BETH> Who's there?"),
    Dialogue("<ADAM> Doctor."),
    Dialogue("<BETH> Doctor who?"),
    Dialogue("<ADAM> You just said it."),
    Dialogue("Press Ctrl-C to finish."),
)

while story.speech:
    with story.turn() as turn:
        for speech in turn.speech:
            time.sleep(story.director.pause + story.director.dwell * len(speech.words))
            print(*speech.words)

