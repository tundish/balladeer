import balladeer
from balladeer import quick_start
from balladeer import Dialogue
from balladeer import StoryBuilder


story = StoryBuilder(
    Dialogue("""
    <DOUGAL> Well, the voices were coming from that old factory on the hill.
    You know, the one where they used to make treacle.

    It's been empty for years but now, it had lights on.

    """
    ),
    Dialogue("""
    <DOUGAL> I got myself with some cunning into a position of vantage.

    """
    ),
    Dialogue("""
    <DOUGAL> What did I see?, you will ask.

    Not very much, I answer.

    The old factory was there on top of the hill, but everything seemed
    craggy and very sinister, and very _blue_

    """
    ),
)


if __name__ == "__main__":
    quick_start(balladeer.examples.ex_12_style_theme, builder=story)
