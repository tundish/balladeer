..  Titling
    ##++::==~~--''``

Scenes
======

We saw in a :ref:`previous section <drama section>` how you can generate Speech programmatically
from a :py:class:`~balladeer.lite.drama.Drama` object.

That's only half the picture though. Most of the time you'd want to pick Speech out of a text file, where
it's easier to edit and maintain.

Balladeer uses the TOML format to store scene dialogue.
Scene file names end in `".scene.toml"`.

.. important::   Please read the `documentation for TOML`_.
            Spend a few minutes to become familiar with its format.

Specifications
~~~~~~~~~~~~~~

The top of the scene file is the place to put *specifications* for the scene.
It consists of a TOML table for each of the Entities you want to cast into the scene.
Each table name should be in upper case. This is the role name. The specifications for the role
determine which entities get cast for the role.

In order to fulfil the role, an entity must match attributes with the specification. You can use three
criteria:

    type
        The value of the ``type`` specification must appear in the entity `types` attribute,
        or else be the name of the entity's natural Python type.
    state
        The value of the ``state`` specification must be a string which specifies the
        dotted name of a required state, or an integer in the case of *int* state.
    states.X
        The second part of the dotted name for the specification is the name of a State.
        The value of a ``states.X`` specification is a list of strings giving the state values which
        are valid for each role.

Here's the specification for one of the scene files in Balladeer's *Cloak of Darkness* example_.

.. literalinclude:: ../examples/ex_11_inventory_compass/foyer.scene.toml
    :lines: 1-7

Shots
~~~~~

The rest of the scene file consists of a `table array`_ of shots. The key for the shot array is an underscore,
``_``. The speech in the shot is defined as a multiline string with the key ``s``.

In other words, something that looks like this:

.. literalinclude:: ../lite/test/test_director.py
    :lines: 879-883
    :dedent: 12

Conditions
~~~~~~~~~~

Each shot may have one or more *conditions* attached to it which determine whether or not the speech is voiced.
The format for conditions is the same as for specifications_, except that the keys are preceded with ``if.ROLE``.

Here's an example from *Cloak of Darkness*. The shot has a single condition, specifying multiple values for
one state.

.. literalinclude:: ../examples/ex_11_inventory_compass/foyer.scene.toml
    :lines: 8-13

You can have multiple conditions which apply to different roles:

.. literalinclude:: ../examples/ex_11_inventory_compass/foyer.scene.toml
    :lines: 35-40

Model
~~~~~

For reference, so you can understand the link between scene syntax and TOML structure, here's an
entire scene file:

.. literalinclude:: ../examples/ex_11_inventory_compass/foyer.scene.toml

... and here's how Balladeer reads it::

    {
        'DRAMA': {'state': 'Spot.foyer', 'type': 'Adventure'},
        'GARMENT': {'type': 'Clothing'},
        '_': [
            {'if': {'DRAMA': {'states': {'Detail': ['none', 'hint']}}},
            's': "<>  This shell of a building is what's left of a hotel.\n"
                 '<>  The room has been stripped of all it once contained.\n'},
            {'if': {'DRAMA': {'states': {'Detail': ['here']}}},
            's': '<>  Right here would have been a foyer.\n'
                 '    You can see the footprint of a grand reception desk running down one side\n'
                 '    of the floor.\n'
                 '\n'},
            {'if': {'DRAMA': {'states': {'Detail': ['hint']}}},
            's': '<>  Try these commands:\n'
                 '\n'
                 "    + 'Look' to see more detail.\n"
                 "    + 'Inventory' to learn what you are carrying.\n"
                 "    + 'Go' to travel in a certain direction.\n"
                 '\n'},
            {'if': {'DRAMA': {'states': {'Detail': ['held']}},
                   'GARMENT': {'states': {'Spot': ['inventory']}}},
            's': '<>  You are wearing a long cloak, which gathers around you.\n'}
        ]
    }

.. _SpeechMark: https://github.com/tundish/speechmark
.. _documentation for TOML: https://toml.io/en/v1.0.0
.. _table array: https://toml.io/en/v1.0.0#array-of-tables
.. _example: https://github.com/tundish/balladeer/tree/master/balladeer/examples/ex_11_inventory_compass
