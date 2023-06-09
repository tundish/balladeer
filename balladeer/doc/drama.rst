..  Titling
    ##++::==~~--''``

Drama
=====

The previous sections of this manual have introduced you to the classes
which Balladeer defines so that you can build your narrative.

The place where you write your code is called the Drama.

.. py:class:: Drama(self, *args, world=None, config=None, **kwargs)

One important aspect of the Drama class is that inherits from
:py:class:`~balladeer.lite.entity.Entity`.
This means you can assign
:py:class:`~balladeer.lite.types.State` to it.

It's a good idea to customize your drama with Python properties so
that you have access to useful characteristics.
One of the supplied examples_ shows how the Drama class keeps track
of the current location of the narrative.

.. literalinclude:: ../examples/ex_11_inventory_compass/main.py
    :lines: 70-72

In addition to properties, there are three ways of adding functionality.

* Overriding the Interlude_ method.
* As a `Directive handler`_.
* In a `Dialogue generator`_ method.

Interlude
~~~~~~~~~

In Balladeer the `interlude` gets called every turn of a
:ref:`Story <story section>`. This makes it the ideal
place to put game rules which are invariant.

.. py:function:: drama.interlude(self, *args, **kwargs)

   Apply rules once every story turn.

   :return: The Drama object
   :rtype: :py:class:`~balladeer.lite.entity.Entity`.

Directive handler
~~~~~~~~~~~~~~~~~

SpeechMark_ has a feature called directives_.
When a drama object implements a directive handler, it may be invoked
from Speech.

Handlers must be instance methods whose name begins with the prefix ``on_``.
They take an argument which is the primary entity of the declaration.
Any other entities are supplied as positional arguments.

.. py:function:: drama.on_xxxing(self, entity: Entity, *args: tuple[Entity], **kwargs):

   Handles the SpeechMark directive 'xxxing'.

   :param entity: The primary entity of the directive
   :param args: The associated entites of the directive
   :rtype: None

This is a snippet from the Balladeer examples_.
In the scene, one character attacks another::

    <WEAPON.attacking@FIGHTER_2>

        _Whack!_

Here is the Drama class with the corresponding handler:

.. literalinclude:: ../examples/ex_10_animate_media/main.py
    :lines: 42-45

Dialogue generator
~~~~~~~~~~~~~~~~~~

Discourse

do_

Speech
------

Generate:

* :py:class:`~balladeer.lite.speech.Prologue`
* :py:class:`~balladeer.lite.speech.Dialogue`
* :py:class:`~balladeer.lite.speech.Epilogue`

Action
------

.. literalinclude:: ../examples/ex_11_inventory_compass/main.py
    :lines: 161-174

.. literalinclude:: ../examples/ex_11_inventory_compass/main.py
    :lines: 212-222

.. _SpeechMark: https://github.com/tundish/speechmark
.. _directives: https://github.com/tundish/speechmark#605
.. _examples: https://github.com/tundish/balladeer/tree/master/balladeer/examples
