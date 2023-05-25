..  This is a Turberfield dialogue file (reStructuredText).
    Scene ~~
    Shot --

:author: D Haynes
:date: 2017-05-11

.. entity:: NARRATOR
   :types: logic.Narrator
   :states: logic.Location.cloakroom_space

.. entity:: CLOAK
   :types: logic.Cloak
   :states: logic.Location.cloakroom_space

.. entity:: CLOAK_ON_THE_FLOOR
   :types: logic.Cloak
   :states: logic.Location.cloakroom_floor
            1

.. entity:: CLOAK_ON_THE_HOOK
   :types: logic.Cloak
   :states: logic.Location.cloakroom_hook
            1

Utility and futility
~~~~~~~~~~~~~~~~~~~~


From where you stand
--------------------

[NARRATOR]_

    This is a cloakroom for patrons of the bar. You can tell because at eye-level
    an array of metalwork resembles a line of coat hooks. All are gone, witnessed only by
    broken brass baseplates or rotten screw holes.

[NARRATOR]_

    No, wait; there is one. One coat hook survives.

Checking your person
--------------------

[CLOAK]_

    You are wearing a dark cloak.

Looking around
--------------

[CLOAK_ON_THE_FLOOR]_

    Your cloak lies in a heap on the floor.

.. memory:: logic.Location.cloakroom_floor
   :subject: CLOAK_ON_THE_FLOOR

   The Player dropped the cloak.

[CLOAK_ON_THE_HOOK]_

    Your velvet cloak hangs darkly from the hook.

.. memory:: logic.Location.cloakroom_hook
   :subject: CLOAK_ON_THE_HOOK

   The Player hung the cloak on a hook.

[NARRATOR]_

    There is a door to the East.

