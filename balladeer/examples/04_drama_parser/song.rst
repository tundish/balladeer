:project:   Examples
:pause:     0.5
:dwell:     0

.. entity:: DRAMA
    :types: balladeer.Drama

.. entity:: BOTTLE
    :types:     balladeer.Stateful
    :states:    balladeer.Fruition.inception

.. |BOTTLES| property:: DRAMA.count

Song
====

Many
----

.. condition:: DRAMA.count ([^01]+)
.. condition:: DRAMA.history[0].name do_look

|BOTTLES| green bottles, hanging on the wall.

One
---

.. condition:: DRAMA.count 1
.. condition:: DRAMA.history[0].name do_look

|BOTTLES| green bottle, hanging on the wall.


All
---

.. condition:: DRAMA.history[0].name do_bottle

And if one green bottle should accidentally fall,
There'll be...

.. property:: DRAMA.prompt Type 'look' to check the damage >
