..  Titling
    ##++::==~~--''``

.. _`drama section`:

Drama
=====

The previous sections of this manual have introduced you to the classes
which Balladeer defines so that you can build your narrative.

The place where you write your code is called the Drama.

.. py:class:: Drama(self, *args, config=None, world=None, **kwargs)

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

.. py:function:: drama.interlude(self, *args, **kwargs):

   Apply rules once every story turn.

   :return: The Drama object
   :rtype: :py:class:`~balladeer.lite.entity.Entity`.

Directive handler
~~~~~~~~~~~~~~~~~

SpeechMark_ has a feature called directives_.
When a drama object implements a directive handler, it may be invoked
from Speech.

Handlers must be instance methods whose name begins with the prefix ``on_``.
They take an argument which is the primary entity of the directive.
Any other entities are supplied as positional arguments.

.. py:function:: drama.on_xxxing(self, entity: Entity, *args: tuple[Entity], **kwargs):

   Handles the SpeechMark directive 'xxxing'.

   :param entity: The primary entity of the directive
   :param args: The associated entities of the directive
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

Dialogue generators must be instance methods whose name begins with the prefix ``do_``.
They take keyword arguments, each of which must have an annotation_.

The method must contain a docstring which defines the text that triggers the method.
Docstrings may contain format specifiers which reference the keyword arguments.

.. py:function:: drama.do_xxx(self, this, text, director, *args, **kwargs):

    Annotations for keyword arguments may be:

    * An iterable type eg: an Enum/State.
    * A string which gives attribute access via the drama object to an iterable of entities.

    This method is a generator of Speech objects.
    The speech objects must be of these three classes:

    :py:class:`~balladeer.lite.speech.Prologue`
        Speech which belongs at the top of a page.
    :py:class:`~balladeer.lite.speech.Dialogue`
        Speech interleaved with the main content of the scene.
    :py:class:`~balladeer.lite.speech.Epilogue`
        Speech which belongs at the bottom of a page.

This sounds complicated, but it's easily demonstrated with a couple of examples_.

This ``do_move`` method declares in its docstring that text like ``n``, ``north``, ``go n`` or ``go north``
will activate the method. The method will be invoked with the corresponding
:py:class:`~balladeer.lite.compass.Compass` class member supplied via the *heading* parameter.

.. literalinclude:: ../examples/ex_11_inventory_compass/main.py
    :lines: 161-174

Next we have ``do_drop``, an example of an annotation which is a string accessor on the drama object.
The text which triggers the method is ``drop`` or ``discard``, so long as it's followed by the name of
any item in the *inventory* location of the drama object's :py:class:`~balladeer.lite.world.WorldBuilder`.

.. literalinclude:: ../examples/ex_11_inventory_compass/main.py
    :lines: 212-222

.. _SpeechMark: https://github.com/tundish/speechmark
.. _directives: https://github.com/tundish/speechmark#605
.. _examples: https://github.com/tundish/balladeer/tree/master/balladeer/examples
.. _annotation: https://docs.python.org/3/howto/annotations.html
