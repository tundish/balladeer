import balladeer
from balladeer import quick_start
from balladeer import Dialogue
from balladeer import Page
from balladeer import Session
from balladeer import StoryBuilder
from balladeer import Turn
from balladeer.utils.themes import theme_page

__doc__ = """
Usage:

    python -m balladeer.examples.ex_12_styling_themes.main > themes.html

"""

Page.themes["grey"] = {
    "ink": {
        "gravity": "hsl(282.86, 0%, 6.12%)",
        "shadows": "hsl(293.33, 0%, 22.75%)",
        "lolight": "hsl(203.39, 0%, 31.96%)",
        "midtone": "hsl(203.39, 0%, 41.96%)",
        "hilight": "hsl(203.06, 0%, 56.47%)",
        "washout": "hsl(66.77, 0%, 82.75%)",
        "glamour": "hsl(50.00, 0%, 100%)",
    },
}

Page.themes["blue"] = {
    "ink": {
        "gravity": "hsl(203.33, 100%, 6.12%)",
        "shadows": "hsl(203.33, 96.92%, 12.75%)",
        "lolight": "hsl(203.33, 96.72%, 21.96%)",
        "midtone": "hsl(203.33, 96.72%, 31.96%)",
        "hilight": "hsl(203.33, 97.72%, 46.47%)",
        "washout": "hsl(203.33, 76.92%, 72.75%)",
        "glamour": "hsl(46.77, 76.92%, 72.75%)",
    },
}

story = StoryBuilder(
    Dialogue("""
    <DOUGAL?style=01&theme=grey> The voices were coming from that old factory on the hill.
    You know, the one where they used to make treacle.

    It's been empty for years but now it had lights on.

    """
    ),
    Dialogue("""
    <DOUGAL?style=02&theme=grey> Well being as you know, a brave spirit, I thought I'd get a better
    look at it all.

    So, moving backwards so as to confuse anyone with evil intents into thinking
    I was going forwards, I got myself with some cunning into a position of vantage.

    """
    ),
    Dialogue("""
    <DOUGAL?style=03&theme=blue> "What did I see?", you will ask.  "Not very much", I answer.

    The old factory was there on top of the hill, but everything seemed
    craggy and very sinister, and very _blue_.

    And then I heard the voice again.

    """
    ),
)


class Narrative(Session):
    def compose(
        self, request, page: Page, story: StoryBuilder = None, turn: Turn = None
    ) -> Page:
        page = super().compose(request, page, story, turn)
        page.paste(
            '<div class="dressing">',
            *(f'<span class="rockery"></span>' for n in range(8)),
            '<span class="factory"></span>',
            "</div>",
            zone=page.zone.basket
        )
        return page


if __name__ == "__main__":
    print(theme_page().html)
    quick_start(balladeer.examples.ex_12_styling_themes, story_builder=story)
