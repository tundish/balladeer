..  Titling
    ##++::==~~--''``


Map
===

Not every narrative needs a Map.

However if you want the player to explore your story world,
they need to be able to change their location.

Then you have to consider how travel works.
What locations can be reached from here? How do we identify the possible directions?

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

It's very common in a story for a way to be blocked, only to open later. Or perhaps
there's a slippery slope which can only be taken in one direction.

:py:class:`~balladeer.lite.compass.Traffic` is a simple state definition to model that behaviour.

.. literalinclude:: ../lite/compass.py
   :pyobject: Traffic

A :py:class:`~balladeer.lite.compass.Transit` is an Entity which describes the navigation between
two places in the story.

MapBuilder
~~~~~~~~~~

.. autoclass:: balladeer.lite.compass.MapBuilder
   :members:
   :member-order: bysource


