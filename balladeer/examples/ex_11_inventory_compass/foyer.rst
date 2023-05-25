..  This is a Turberfield dialogue file (reStructuredText).
    Scene ~~
    Shot --

:author: D Haynes
:date: 2017-05-11

.. entity:: NARRATOR
   :types: logic.Narrator
   :states: logic.Location.foyer

.. entity:: CLOAK
   :types: logic.Cloak
   :states: logic.Location.foyer

After the fire, a Magician returns
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

From where you stand
--------------------

[NARRATOR]_

    This place no longer looks much like a hotel. This would have been the foyer, though.
    You can see the footprint of a grand reception desk running down one side
    of the floor.

[NARRATOR]_

    The room has been stripped of all it once contained.

Checking your person
--------------------

[CLOAK]_

    You are wearing a long cloak, which gathers around you. It feels furry,
    like velvet, although that's hard to tell by looking. It is so black
    that its folds and textures cannot be perceived.

[CLOAK]_

    It seems to swallow all light.

.. memory:: logic.Location.foyer
   :subject: NARRATOR

   The Player visited the foyer.

Looking around
--------------

[NARRATOR]_

    To the North, the door by which you first entered is stuck fast.

[NARRATOR]_

    There are other doors to the South and West.

