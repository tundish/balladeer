..  Titling
    ##++::==~~--''``

Interaction
===========

Sometimes you need to create encounters between characters without there being too much stateful significance.
You want the player to discover the game world, its lore and back story.
You want to deliver a rich experience with a minimum of coding overhead.

This can be achieved by creating `dialogue trees`; blocks of optional dialogue which lead the player to
explore the environment and interact with it.

Balladeer provides a mixin class called :py:class:`~balladeer.lite.speechtables.SpeechTables` which gives
your Drama the ability to generate dialogue that gives the player choices, and integrates with the parser
to recognise the phrases and options which identify them.

.. code-block:: python

    from balladeer import Drama
    from balladeer import SpeechTables

    class Interaction(SpeechTables, Drama):
        ...

Example
~~~~~~~

The dialogue tree is attached to a single shot of SpeechMark, which acts as a parent.
The markup in the shot has two responsibilities:

    * To define a numbered list of dialogue options for the player to use.
    * To include a ``branching`` directive which tells the :py:class:`~balladeer.lite.speechtables.SpeechTables`
      class that it must inspect these options and add them to the parser's collection of recognised options and
      phrases.

The hierarchy of choices and consequences is defined as a TOML table beneath the parent dialogue. The outcome
corresponding to option ``1`` is stored against that same key in the data.

Dialogue can branch again wherever you wish, allowing for deeply nested trees.

For as long as the interaction is in play, the ``tree`` attribute of your Drama class will evaluate **True**.

You can control when to terminate the interaction by adding a directive to any of the dialogue blocks:

    * A simple ``returning`` directive will end the interaction completely.
      The ``tree`` attribute of your Drama class will evaluate **False** once more.
    * A ``returning`` directive which targets the Drama object eg: ``returning@INTERACTION`` will
      hop back up to the previous branching node and stay in the dialogue tree.

.. literalinclude:: ../lite/test/test_speechtables.py
    :lines: 58-119
    :dedent: 4

