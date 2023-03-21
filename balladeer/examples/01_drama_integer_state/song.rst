:project:   Examples
:pause:     0
:dwell:     0.4

.. entity:: DRAMA
    :types: balladeer.Drama

.. |BOTTLES| property:: DRAMA.state

Song
====

Many
----

.. condition:: DRAMA.state ([^01]+)

|BOTTLES| green bottles, hanging on the wall.

And if one green bottle should accidentally fall,
There'll be...

One
---

.. condition:: DRAMA.state 1

|BOTTLES| green bottle, hanging on the wall.

And if one green bottle should accidentally fall,
There'll be...

None
----

.. condition:: DRAMA.state 0

No green bottles hanging on the wall.

