..  Titling
    ##++::==~~--''``


Map
===

Not every narrative needs a Map.

However if you want the player to explore your story world,
they need to be able to change their location.

Then you have to consider how travel works.
What locations can be reached from here? How do we identify the possible directions?
Can I give this pathway a name? Did I just make that pathway a real place by naming it?

The design goal for Balladeer's topological model is to be extremely flexible, while
remaining as simple as possible.

Compass
~~~~~~~

The Compass is a traditional direction system. It is very common in text adventures.

.. autoclass:: balladeer.lite.compass.Compass
   :members:
   :member-order: bysource
   :no-special-members: __new__
   :no-undoc-members:

.. automethod:: balladeer.lite.compass.Compass.bearing

Traffic and Transits
~~~~~~~~~~~~~~~~~~~~

Sometimes in a story a way is blocked, only to be opened later. Or perhaps
there's a slippery slope which can be taken only in one direction.

:py:class:`~balladeer.lite.compass.Traffic` is a simple state definition to model that behaviour.

.. literalinclude:: ../lite/compass.py
   :pyobject: Traffic

A :py:class:`~balladeer.lite.compass.Transit` is an object which describes the navigation between
two places in the world. It inherits from :py:class:`~balladeer.lite.entity.Entity` so it may be anonymous,
or a fully described feature of your story.

.. literalinclude:: ../lite/test/test_types.py
   :lines: 142-147
   :dedent: 8

>>> transit.description
"A Wooden Door. It seems to be locked."

.. caution:: **Compact idiom for attribute swapping and state allocation**.

    At the the expense of readability, this one-liner will:

    * Change the state of the door
    * Copy the value of `aspect` to `revert`
    * Change the value of `aspect` to "unlocked"

    >>> transit.set_state(Traffic.flowing).aspect, transit.revert = "unlocked", transit.aspect

    With the subsequent result:

    >>> transit.description
    "A Wooden Door. It seems to be unlocked."
    >>> transit.get_state("Traffic")
    <Traffic.flowing>
    >>> transit.revert
    "locked"

MapBuilder
~~~~~~~~~~

.. autoclass:: balladeer.lite.compass.MapBuilder
   :members:
   :member-order: bysource


