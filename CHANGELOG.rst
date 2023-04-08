..  Titling
    ##++::==~~--''``

.. This is a reStructuredText file.

Change Log
::::::::::

0.28.0
======

This is a transitional release towards Balladeer *lite*.

I have adopted `TOML <https://toml.io/en/>`_ as the new format for scene files.
Character dialogue uses `SpeechMark <https://pypi.org/project/speechmark/>`_.

Documentation refers to the *classic* format.
This will be corrected in further releases over the next few weeks.

Fixes to classic:

* Repin to turberfield-dialogue 0.47.0.
* Folio introduces named page styles for front and rear matter.
* Fix errant spaces in Folio output.
* Add a chapter variable to the style of each section.

0.27.0
======

* Add folio module for generation of transcripts.
* Repin to turberfield-dialogue 0.46.1.
* Repin to turberfield-utils 0.47.0.

0.26.0
======

* Repin to turberfield-dialogue 0.40.0.

0.25.0
======

* Repin to turberfield-catchphrase 0.25.0.

0.24.0
======

* Added optional Presenter factory parameter to Story.represent.
* Repin to turberfield-dialogue 0.39.0.
* Repin to turberfield-catchphrase 0.24.0.
* Repin to docutils 0.18.1.

0.23.0
======

* Improve routing algorithm to avoid loops.

0.22.0
======

* Repin to turberfield-dialogue.

0.21.0
======

* Repin to turberfield-dialogue.

0.20.0
======

* Fix cartography types.

0.19.0
======

* `Story.context` is now a property; more convenient when subclassing.

0.18.0
======

* Transition is now returned in `Map.options` property.

0.17.0
======

* Repin to turberfield-utils.
* Add cartography module.

0.16.0
======

* Various fixes to examples.
* Various updates to development blog.

0.15.0
======

* Added an example on basic use of parser.
* Now using output of interlude as fact keywords.

0.14.0
======

* Allow keyword arguments in `represent`.

0.13.0
======

* Add examples directory.
* Repin to turberfield-dialogue.

0.12.0
======

* Allow easier setting of `Story` context.
* Provide default empty ensemble.
* Repin to turberfield-catchphrase.
* Repin to docutils.

0.11.0
======

* Adopt absolute pinning for dependencies.

0.10.0
======

* `Gesture` property names are now unique across Head and Hand.
* `Gesture` attribute access implemented via ChainMap.

0.9.0
=====

* Add __str__ method for `Gesture`.

0.8.0
=====

* Use Brew class in unit tests for `Gesture`.

0.7.0
=====

* Add tests for `Drama.next_states`.
