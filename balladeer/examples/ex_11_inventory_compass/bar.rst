..  This is a Turberfield dialogue file (reStructuredText).
    Scene ~~
    Shot --

:author: D Haynes
:date: 2017-05-11

.. entity:: NARRATOR
   :types: logic.Narrator
   :states: logic.Location.bar

.. entity:: CLOAK
   :types: logic.Cloak
   :states: logic.Location.bar

.. entity:: PRIZE
   :types: logic.Prize
   :states: 1

A man walks into a bar...
~~~~~~~~~~~~~~~~~~~~~~~~~


From where you stand
--------------------

[NARRATOR]_

    This is the bar.

[CLOAK]_

    The room is totally dark. The echoes suggest empty, too.

Checking your person
--------------------

[CLOAK]_

    The hem of your cloak is catching against uneven wooden boards.
    The smell of sawdust begins to reach your nostrils as you sweep
    over the floor.
    
.. memory:: logic.Location.bar
   :subject: CLOAK

   The Player wore the cloak in the bar.

Looking around
--------------

[PRIZE]_

    Someone has written a message in the dust on the floor. It says:

    |message|

.. memory:: logic.Location.bar
   :subject: PRIZE

   The Player read the message as "|message|".

[NARRATOR]_

    There is a door to the North.

.. |message| property:: PRIZE.message
