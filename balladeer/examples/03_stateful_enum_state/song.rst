:project:   Examples
:pause:     0
:dwell:     0.4

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
.. condition:: DRAMA.state 0

|BOTTLES| green bottles, hanging on the wall.

.. property:: BOTTLE.state balladeer.Fruition.completion
.. property:: DRAMA.state 1

One
---

.. condition:: DRAMA.count 1
.. condition:: DRAMA.state 0

|BOTTLES| green bottle, hanging on the wall.

.. property:: BOTTLE.state balladeer.Fruition.completion
.. property:: DRAMA.state 1

All
---

.. condition:: DRAMA.state 1

And if one green bottle should accidentally fall,
There'll be...

.. property:: DRAMA.state 0
