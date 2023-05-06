import time

from balladeer.lite.app import quick_start
from balladeer.lite.speech import Prologue
from balladeer.lite.speech import Dialogue
from balladeer.lite.speech import Epilogue
from balladeer.lite.story import StoryBuilder


story = StoryBuilder(
    Prologue("Here's a joke..."),
    Dialogue("<ADAM> Knock, knock."),
    Dialogue("<BETH> Who's there?"),
    Dialogue("<ADAM> Doctor."),
    Dialogue("<BETH> Doctor who?"),
    Dialogue("<ADAM> You just said it."),
    Epilogue("Press Ctrl-C to finish."),
)


if __name__ == "__main__":
    quick_start(builder=story)

