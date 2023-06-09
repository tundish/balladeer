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
* In a `Dialogue generator`_ method.
* As a `Directive handler`_.

Interlude
~~~~~~~~~

.. py:function:: drama.interlude(self, *args, **kwargs)

   Return a list of random ingredients as strings.

   :param self: Optional "kind" of ingredients.
   :type self: list[str] or None
   :return: The ingredients list.
   :rtype: None

No return value.
Invariant

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

Directive handler
~~~~~~~~~~~~~~~~~

on_

No return value.

.. _examples: https://github.com/tundish/balladeer/tree/master/balladeer/examples
