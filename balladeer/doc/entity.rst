..  Titling
    ##++::==~~--''``

Entities
========

Entity objects
~~~~~~~~~~~~~~

The :py:class:`~balladeer.lite.entity.Entity`
class is the base for all objects in your narrative.
Earlier we saw the need for :ref:`more than one name for the same thing <state example>`.
Entities are like that too. They can have many `names`, many `types`, and many `states`.

.. autoclass:: balladeer.lite.entity.Entity
   :members: name, type, description
   :member-order: bysource
   :special-members:
   :no-undoc-members:

Entity state
~~~~~~~~~~~~

Entity objects have methods and properties to support state allocation.

.. automethod:: balladeer.lite.entity.Entity.set_state

.. automethod:: balladeer.lite.entity.Entity.get_state

.. autoproperty:: balladeer.lite.entity.Entity.state


