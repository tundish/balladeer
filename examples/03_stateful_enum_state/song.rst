:project:   Examples
:pause:     0
:dwell:     0.4

.. entity:: DRAMA
    :types: balladeer.Drama

.. entity:: BOTTLE
    :types:     balladeer.Stateful
    :states:    balladeer.Fruition.inception

.. |BOTTLES| property:: DRAMA.unbroken

Song
====

Many
----

.. condition:: DRAMA.unbroken ([^01]+)

|BOTTLES| green bottles, hanging on the wall.

And if one green bottle should accidentally fall,
There'll be...

.. property:: BOTTLE.state balladeer.Fruition.completion

One
---

.. condition:: DRAMA.unbroken 1

|BOTTLES| green bottle, hanging on the wall.

And if one green bottle should accidentally fall,
There'll be...

.. property:: BOTTLE.state balladeer.Fruition.completion

None
----

.. condition:: DRAMA.unbroken 0

No green bottles hanging on the wall.

