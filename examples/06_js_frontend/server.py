"""
This is a complete example of a Balladeer story which accepts text commands over the web.

"""
import argparse
import pathlib
import random
import re
import sys
import uuid

from aiohttp import web
import pkg_resources

from balladeer import Assembly
from balladeer import DataObject
from balladeer import Drama
from balladeer import Fruition
from balladeer import Stateful
from balladeer import Story as StoryType


class Bottle(DataObject, Stateful): pass


class Story(StoryType):

    def render_animated_frame_to_html(self, frame, controls=[], **kwargs):
        return "\n".join([
            '<div id="app"><diorama v-bind:population="population"></diorama></div>',
            StoryType.render_animated_frame_to_html(frame, controls, **kwargs),
            '<script src="/js/bottles.js"></script>',
        ])


class Bottles(Drama):

    colours = ["#00FF00", "#00EE00", "#00DD00"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.population = [
            Bottle(colour=random.choice(self.colours)).set_state(Fruition.inception),
            Bottle(colour=random.choice(self.colours)).set_state(Fruition.inception),
            Bottle(colour=random.choice(self.colours)).set_state(Fruition.inception),
            Bottle(colour=random.choice(self.colours)).set_state(Fruition.inception),
            Bottle(colour=random.choice(self.colours)).set_state(Fruition.inception),
            Bottle(colour=random.choice(self.colours)).set_state(Fruition.inception),
        ]
        self.active.add(self.do_bottle)
        self.active.add(self.do_look)
        self.prompt = "?"

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
        break

        """
        try:
            random.choice(self.unbroken).state = Fruition.completion
        except IndexError:
            pass

    def do_look(self, this, text, presenter, *args, **kwargs):
        """
        look

        """
        self.prompt = "?"


VALIDATION = {
    "session": re.compile("[0-9a-f]{32}"),
}


async def get_root(request):
    drama = Bottles()
    drama.folder = ["song.rst", "end.rst"]
    story = Story(context=drama)
    text = story.context.deliver("look", presenter=None)
    story.presenter = story.represent(text)
    request.app["sessions"][story.id] = story
    raise web.HTTPFound("/{0.id.hex}".format(story))


async def get_assembly(request):
    uid = uuid.UUID(hex=request.match_info["session"])
    story = request.app["sessions"][uid]
    return web.Response(
        text=Assembly.dumps(story.context.population),
        content_type="application/json"
    )


async def get_session(request):
    uid = uuid.UUID(hex=request.match_info["session"])
    story = request.app["sessions"][uid]

    animation = next(filter(None, (story.presenter.animate(
        frame, dwell=story.presenter.dwell, pause=story.presenter.pause
    ) for frame in story.presenter.frames)))

    title = story.presenter.metadata.get("project")[0]
    controls = [
        "\n".join(story.render_action_form(action, autofocus=not n))
        for n, action in enumerate(story.actions)
        if story.context.count
    ]
    rv = story.render_body_html(title=title).format(
        '<script src="https://unpkg.com/vue@3"></script>',
        story.render_dict_to_css(vars(story.settings)),
        story.render_animated_frame_to_html(animation, controls)
    )

    return web.Response(text=rv, content_type="text/html")


async def post_command(request):
    uid = uuid.UUID(hex=request.match_info["session"])
    story = request.app["sessions"][uid]
    data = await request.post()
    cmd = data["cmd"]
    if cmd and not story.context.validator.match(cmd):
        raise web.HTTPUnauthorized(reason="User sent invalid command.")
    else:
        text = story.context.deliver(cmd, presenter=story.presenter)
        story.presenter = story.represent(text, facts=story.context.facts, previous=story.presenter)
    raise web.HTTPFound("/{0.hex}".format(uid))


def build_app(args):
    app = web.Application()
    app.add_routes([
        web.get("/", get_root),
        web.get("/{{session:{0}}}".format(VALIDATION["session"].pattern), get_session),
        web.get("/{{session:{0}}}/assembly".format(VALIDATION["session"].pattern), get_assembly),
        web.post("/{{session:{0}}}/cmd/".format(VALIDATION["session"].pattern), post_command),
    ])
    app.router.add_static(
        "/css/base/",
        pkg_resources.resource_filename("turberfield.catchphrase", "css")
    )
    app.router.add_static("/img/", pathlib.Path(__file__).parent)
    app.router.add_static("/js/", pathlib.Path(__file__).parent)
    app["sessions"] = {}
    return app


def main(args):
    Assembly.register(Bottle, Fruition)

    app = build_app(args)
    return web.run_app(app, host=args.host, port=args.port)


def parser(description=__doc__):
    rv = argparse.ArgumentParser(description)
    rv.add_argument(
        "--host", default="127.0.0.1",
        help="Set an interface on which to serve."
    )
    rv.add_argument(
        "--port", default=8080, type=int,
        help="Set a port on which to serve."
    )
    return rv


def run():
    p = parser()
    args = p.parse_args()
    rv = main(args)
    sys.exit(rv)


if __name__ == "__main__":
    run()
