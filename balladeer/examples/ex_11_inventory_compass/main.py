#!/usr/bin/env python
# encoding: UTF-8

import random

import balladeer
from balladeer import Compass
from balladeer import Detail
from balladeer import Drama
from balladeer import Entity
from balladeer import Grouping
from balladeer import Prologue, Dialogue, Epilogue
from balladeer import MapBuilder
from balladeer import StoryBuilder
from balladeer import Traffic
from balladeer import Transit
from balladeer import WorldBuilder
from balladeer import quick_start

__doc__ = """
python3 -m balladeer.examples.ex_11_inventory_compass.main

"""


class Map(MapBuilder):

    spots = {
        "foyer": ["foyer", "lobby"],
        "bar": ["bar", "saloon bar"],
        "cloakroom": ["cloakroom", "cloak room", "cloaks"],
        "hook": ["hook", "cloakroom hook"],
        "inventory": ["inventory"],
    }

    def build(self):
        yield from [
            Transit().set_state(self.exit.bar, Compass.N, self.into.foyer, Traffic.flowing),
            Transit().set_state(self.exit.foyer, Compass.W, self.into.cloakroom, Traffic.flowing),
        ]


class World(WorldBuilder):
    def build(self):
        yield from [
            Entity(
                name="Cloak", type="Clothing",
                sketch="A {names[0]} so black that its folds and textures cannot be perceived.",
                aspect="It seems to swallow all light.",
                repute="It seems to swallow all light.",
            ).set_state(self.map.spot.inventory, 1),
            Entity(
                name="Hook", type="Fixture",
                sketch="A brass hook.",
                aspect="Solid. This is not for decoration.",
            ).set_state(self.map.home.cloakroom, self.map.spot.cloakroom, 1),
            Entity(
                name="Message", type="Marking",
                sketch="A {names[0]} in the dust on the floor. It says: '{aspect}'",
                aspect="You win!",
            ).set_state(self.map.home.bar, self.map.spot.bar, 0),
        ]


class Adventure(Drama):

    @property
    def here(self):
        return self.get_state("Spot")

    @property
    def local(self):
        inventory = self.world.map.spot.inventory
        return Grouping.typewise(
            i for i in self.world.entities if i.get_state("Spot") in (self.here, inventory)
        )

    @property
    def visible(self):
        return Grouping.typewise(
            i for i in self.world.entities if i.get_state("Spot") == self.here and i.state
        )

    def do_help(self, this, text, director, *args, **kwargs):
        """
        help | syntax

        """
        commands = [random.choice(list(i)) for i in self.active.values() if i]
        yield Epilogue(
            "<> Syntax:\n" +
            "\n".join([f"+ {i.upper()}" for i in commands])
        )

    def do_hint(self, this, text, director, *args, **kwargs):
        """
        hint | h

        """
        self.set_state(Detail.hint)

    def do_look(self, this, text, director, *args, **kwargs):
        """
        look
        where | where am i

        """
        self.set_state(Detail.here)
        entities = self.visible.each

        if entities:
            yield Dialogue("<> You take a look around.")
            yield Dialogue( "<> You see:\n" + "\n".join([f"+ {i.description}" for i in entities]))

        yield Epilogue(
            "<> Exits are:\n" +
            "\n".join([f"+ {dirn.title}" for dirn, dest, transit in self.world.map.options(self.here)])
        )

    def do_inventory(self, this, text, director, *args, **kwargs):
        """
        inventory | i

        """
        self.set_state(Detail.held)
        entities = [
            i for i in self.world.entities if i.get_state("Spot") == self.world.map.spot.inventory
        ]
        yield Epilogue(
            "<> You are carrying:\n" +
            "\n".join([f"+ {i.description}" for i in entities])
        )

    def do_move(self, this, text, director, *args, heading: Compass, **kwargs):
        """
        {heading.name} | {heading.label}
        go {heading.name} | go {heading.label}

        """
        options = {compass: spot for compass, spot, transit in self.world.map.options(self.here)}
        if heading not in options:
            yield Prologue(f"<> You can't go {heading.title} from here.")
        else:
            self.set_state(options[heading])

        # On leaving the bar we remove a letter of the message
        for mark in self.local["Marking"]:
            mark.aspect = mark.aspect.replace(
                random.choice(mark.aspect), " ", 1
            )

    def do_take(self, this, text, director, *args, item: "local[Clothing]", **kwargs):
        """
        get {item.names[0]}
        pick up {item.names[0]}
        take {item.names[0]}
        wear {item.names[0]}

        """
        if item.get_state("Spot") == self.world.map.spot.inventory:
            yield Prologue(f"<> You already have the {item.names[0]}.")
            return

        lookup = {i.uid: i for i in self.world.entities}
        fixture = lookup.get(next(
            (uid for uid in item.links if "Fixture" in getattr(lookup.get(uid), "types", [])),
            None
        ))
        if fixture:
            # Remove the association between entities and modify fixture visibility
            item.links.discard(fixture.uid)
            fixture.links.discard(item.uid)
            fixture.state = fixture.state if len(fixture.links) else 1

        item.set_state(self.world.map.spot.inventory)
        item.aspect = item.repute
        yield Prologue(f"<> You take the {item.names[0]}.")

    def do_drop(self, this, text, director, *args, item: "world.statewise[Spot.inventory]", **kwargs):
        """
        drop {item.names[0]}
        discard {item.names[0]}

        """
        item.set_state(self.here)
        item.aspect = f"It lies on the floor."
        yield Prologue(f"<> You drop the {item.names[0]}.")

    def do_hang(
        self, this, text, director, *args,
        clothing: "local[Clothing]",
        fixture: "local[Fixture]",
        **kwargs
    ):
        """
        hang {clothing.names[0]} on {fixture.names[0]}
        hang up {clothing.names[0]}
        put {clothing.names[0]} on {fixture.names[0]}
        cover {fixture.names[0]} with {clothing.names[0]}

        """
        if clothing.uid in fixture.links:
            yield Prologue(f"<> Already done.")
        else:
            clothing.set_state(self.here)
            clothing.links.add(fixture.uid)
            clothing.aspect = f"It hangs from a {fixture.names[0]}."
            fixture.links.add(clothing.uid)
            fixture.state = 0
            yield Prologue(f"<> You hang the {clothing.names[0]} on the {fixture.names[0]}.")


class Story(StoryBuilder):
    def build(self):
        yield Adventure(world=self.world, config=self.config).set_state(
            self.world.map.spot.foyer, Detail.none
        )


if __name__ == "__main__":
    quick_start(balladeer.examples.ex_11_inventory_compass)
