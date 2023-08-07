import balladeer
from balladeer import quick_start
from balladeer import Dialogue
from balladeer import Page
from balladeer import Session
from balladeer import StoryBuilder
from balladeer.utils.themes import theme_page

__doc__ = """
Usage:

    python -m balladeer.examples.ex_12_style_theme.main > themes.html

"""

Page.themes["grey"] = {
    "ink": {
        "gravity": "hsl(293.33, 96.92%, 12.75%)",
        "shadows": "hsl(202.86, 100%, 4.12%)",
        "lolight": "hsl(203.39, 96.72%, 11.96%)",
        "midtone": "hsl(203.39, 96.72%, 31.96%)",
        "hilight": "hsl(203.06, 97.3%, 56.47%)",
        "washout": "hsl(50.00, 0%, 100%)",
        "glamour": "hsl(66.77, 96.92%, 72.75%)",
    },
}

Page.themes["blue"] = {
    "ink": {
        "gravity": "hsl(293.33, 96.92%, 12.75%)",
        "shadows": "hsl(202.86, 100%, 4.12%)",
        "lolight": "hsl(203.39, 96.72%, 11.96%)",
        "midtone": "hsl(203.39, 96.72%, 31.96%)",
        "hilight": "hsl(203.06, 97.3%, 56.47%)",
        "washout": "hsl(50.00, 0%, 100%)",
        "glamour": "hsl(66.77, 96.92%, 72.75%)",
    },
}

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


class Song(Session):
    def compose(
        self, request, page: Page, story: StoryBuilder = None, turn: StoryBuilder.Turn = None
    ) -> Page:
        page = super().compose(request, page, story, turn)
        page.paste(
            '<div class="dressing">',
            *(f'<span class="flower">{n+1:02d}</span>' for n in range(12)),
            "</div>",
            zone=page.zone.bucket
        )
        return page


if __name__ == "__main__":
    print(theme_page().html)
    quick_start(balladeer.examples.ex_12_style_theme, builder=story)
