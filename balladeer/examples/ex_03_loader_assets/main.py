from balladeer import quick_start
from balladeer import Dialogue
from balladeer import StoryBuilder


story = StoryBuilder(
    Dialogue("<?offer=1>Here's a joke..."),
    Dialogue("<ADAM> Knock, knock."),
    Dialogue("<BETH> Who's there?"),
    Dialogue("<ADAM> Doctor."),
    Dialogue("<BETH> Doctor who?"),
    Dialogue("<ADAM> You just said it."),
)


if __name__ == "__main__":
    quick_start(__file__, story_builder=story)
