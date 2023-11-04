..  Titling
    ##++::==~~--''``

Conversation
============

Sometimes you need to create encounters between characters without there being too much stateful significance.
You want the player to discover the game world, its lore and back story.
You want to deliver a rich experience with a minimum of coding overhead.

This can be achieved by creating `conversation trees`; blocks of optional dialogue which lead the player to
explore the environment and interact with it.

Balladeer provides a mixin class called `SpeechTables` which gives your Drama the ability to generate dialogue
which gives the player choices, and integrates with the parser to recognise the phrases and options which identify
them.

.. code-block:: python

    from balladeer import Drama
    from balladeer import SpeechTables

    class Conversation(SpeechTables, Drama):
        ...

Mixin
~~~~~

.. literalinclude:: ../lite/test/test_speechtables.py
    :lines: 58-119
    :dedent: 4

