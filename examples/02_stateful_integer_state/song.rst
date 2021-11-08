:project:   Examples
:pause:     0
:dwell:     0.4

.. entity:: DRAMA
    :types: balladeer.Drama

.. entity:: BOTTLE
    :types:     balladeer.Stateful
    :states:    1

Song
====

Many
----

.. condition:: DRAMA.unbroken ([^01]+)

|BOTTLES| green bottles, hanging on the wall.

And if one green bottle should accidentally fall,
There'll be...

.. property:: BOTTLE.state 0

One
---

.. condition:: DRAMA.unbroken 1

|BOTTLES| green bottle, hanging on the wall.

And if one green bottle should accidentally fall,
There'll be...

.. property:: BOTTLE.state 0

None
----

.. condition:: DRAMA.unbroken 0

No green bottles hanging on the wall.

.. |BOTTLES| property:: DRAMA.unbroken
