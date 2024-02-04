..  Titling
    ##++::==~~--''``

Basics
======

Python is a language with very powerful data types.
Once you `know them`_ you can achieve a great deal in only a few lines of code.

Balladeer is a domain-specific framework which will help you structure your code in
order to best tell your story. It's a simple object-oriented library with about a dozen classes in total.

Here are two which are fundamental to the Balladeer
philosophy. We will see them in use soon. So let's get some
detail on them before we proceed further.

States
~~~~~~

Whatever the genre of your narrative, it's a safe bet that
the characters you create will undergo change.

They may advance in their profession, lose weight, take up sewing, get drenched in a rainstorm, or disappear never to be seen again.

In Balladeer, you can model all these by defining and allocating :py:class:`~balladeer.lite.types.State`.


.. autoclass:: balladeer.lite.types.State
   :members:
   :member-order: bysource

.. _`state example`:

By way of example, here's how you might create a state
for political affiliation in the UK.

.. literalinclude:: ../lite/test/test_types.py
   :pyobject: StateTests.Politics

Note how this class captures synonyms for the various parties. The `label` property gives you a preferred term for
each one:

>>> Politics.ukp.label
'UKIP'

Grouping
~~~~~~~~

Whether you are modelling a forest glade, a castle dungeon, or an alien space fleet,
you will need to create objects for that model.

The next challenge is to organize those objects, sorting and
filtering them so that you can isolate the ones you need
to operate on (ie: modify their states_).

This is what :py:class:`~balladeer.lite.types.Grouping`
is for.

.. autoclass:: balladeer.lite.types.Grouping
   :members:
   :member-order: bysource

.. _know them: https://docs.python.org/3/library/stdtypes.html
