..  Titling
    ##++::==~~--''``

Speech
======

The role of most of our literature is, it seems, to destroy the world.

-- Jean Paul Gustave Ricoeur

Modelling
~~~~~~~~~

In the previous sections we saw how a few simple principles provide the potential for an extremely
detailed world model.

Python is such a powerful language. We could generate thousands of entities with which to populate
our story. Perhaps we might automate the process in clever ways. Maybe ingest some real-world data
sets and synthesize an analogue of our home town or city.

Would that be a good approach? I shouldn't think so. It doesn't really help tell your story.

If you forget to create an Entity for the knife which kills Caesar, what does it matter?
During the scene of the murder, Brutus always comes up with one anyway.
Whether it is mentioned in the script or not, that knife exists in the mind of the reader.
It's there when it needs to be, otherwise no dead Emperor.

It's true that text adventures have a tradition of progressing the story via the manipulation of objects.
But there are other ways, and Balladeer encourages you to try them.

Here are some suggestions for a good Entity:

* A newspaper which prints articles from a parallel reality.
* A kettle that whistles tunes.
* A statue which comes alive and murders people.
* A bulletproof car with the calm authority of an English Butler.

In other words; *characters*. And the primary medium for your characters is Speech.

Markup
~~~~~~

So we need a way of defining Speech.
It's more than a string of words. We want to remember who says the words and why.
We want the words to have an effect on the story.

Enter SpeechMark_.

.. note::   Please read the `documentation on SpeechMark`_.
            Take a few minutes to become familiar with its syntax.


.. autoclass:: balladeer.lite.speech.Speech
   :members:
   :member-order: bysource

.. _SpeechMark: https://github.com/tundish/speechmark
.. _documentation on SpeechMark: https://github.com/tundish/speechmark
