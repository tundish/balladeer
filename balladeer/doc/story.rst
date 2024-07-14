..  Titling
    ##++::==~~--''``

.. _`story section`:

Story
=====

The :py:class:`~balladeer.lite.story.StoryBuilder` class provides the top level object for your narrative.

To create a new Story, override the `build` method of a subclass.
It is a generator of :py:class:`~balladeer.lite.drama.Drama`  objects.

.. code-block:: python

    class Story(StoryBuilder):
        def build(self, **kwargs):
            yield Drama(world=self.world, config=self.config, **kwargs).set_state(Detail.none)


The public API is under development and not documented at this time.
While this is the case, you should use the ``quick_start`` function to run your Story.

.. py:function:: quick_start(module: [str | ModuleType] = "", resource="", builder=None, host="localhost", port=8080):

    Launch a Story to play over the Web.

    :param module:      A Python module, or else a string which identifies one.
    :param resource:    An optional path into a submodule. Web assets will be loaded from this location.
    :param builder:     A subclass of :py:class:`~balladeer.lite.story.StoryBuilder` or an instance object.
    :param host:        The host interface from which to serve the Story.
    :param port:        The network port from which to serve the Story.


If you don't supply all that information, ``quick_start`` is clever enough to guess anyway.
Have a look at the examples_ to see how simple it is to use.

.. _examples: https://github.com/tundish/balladeer/tree/master/balladeer/examples
