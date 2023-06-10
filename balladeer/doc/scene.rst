..  Titling
    ##++::==~~--''``

Scenes
======

.. literalinclude:: ../examples/ex_11_inventory_compass/foyer.scene.toml
    :lines: 1-7

.. literalinclude:: ../examples/ex_11_inventory_compass/foyer.scene.toml
    :lines: 8-13

.. literalinclude:: ../examples/ex_11_inventory_compass/foyer.scene.toml
    :lines: 35-40

.. literalinclude:: ../examples/ex_11_inventory_compass/foyer.scene.toml

::

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
.. _TOML: https://toml.io/en/

