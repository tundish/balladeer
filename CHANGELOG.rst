..  Titling
    ##++::==~~--''``

.. This is a reStructuredText file.

Change Log
::::::::::

0.57.0
======

* Resident exits are named-tuples.
* Resident class provides `focus` property.
* Multiple fixes to StoryStager.

0.56.0
======

* By default, text in `code` emphasis is expanded into a form/button which posts the text as a command.

0.55.0
======

* Improved behaviour in StoryStager for populating types.
* Minor improvement to asset path reporting.
* Case conversion on StoryStager state lookup.
* Expect Events from busker.
* New method `monitor_context` to process Events.

0.54.0
======

* Add `resident` module and tests.
* Add `storystager` module and tests.
* `discover_assets` accepts keyword arguments.
* `storybuilder` module renamed from `story`.

0.53.0
======

* ballader.lite no longer depends on turberfield-utils.
* Added reporting of Loader.staging discovery.
* Added `evaluation` as an alias for `Fruition.transition`.

0.52.0
======

* WorldBuilder does not generate any entities by default.
* Better use of kwarg parameters.
* Fix a bug in deep copy of Entity.
* Add busker as a dependency
* Use busker.stager to load stage files.

0.51.0
======

* Allow parameter passing into MapBuilder.
* Allow parameter passing into WorldBuilder.
* Allow parameter passing into StoryBuilder.
* Allow parameter passing into Drama.
* Expose Fruition type.

0.50.0
======

* Minor fixes in app compose helper methods to improve testability.
* Extra delegate methods for page composition.

0.49.0
======

* Fix button attribute from Home endpoint.
* Add 'label' to cue parameters.
* Change to formatting within Speech; `!e` does HTML entity substitution, `!x` performs ROT13 translation.

0.48.0
======

* To make for better grouping, Fruition no longer inherits from IntEnum.
* More robust building of specs with multiple states.

0.47.0
======

* Better error handling when building to spec.
* Page creates outer div for zones (by default; basket, inputs, svg, and bucket).

0.46.0
======

* Fixed a bug casting invalid scene files.
* `discover_assets` sorts by path.
* Ensure `types` is a set when building to spec.
* Fix bug to ensure all spec `types` required for a role.
* Populate endpoint metadata from quick_start keyword arguments.
* App session renders options list for command.

0.45.0
======

* Added `goal` to Detail state.
* Added a utility to generate Conversation diagram.
* Add a Presenter class for sanitization of HTML output.
* Insert 'target="_blank" rel="noopener noreferrer"' into hyperlinks.
* WorldBuilder default behaviour is to create Entities from asset specs.

0.44.0
======

* Make Turn a module-level type.
* Fixed a bug in App after Turn refactoring.
* All class discovery magic refactored to quick_start function.
* All Builder classes have a make method now.
* Fixed a bug in `Story.__deepcopy__`.

0.43.0
======

* Condition specifications now evaluate simple attributes as boolean.
* Created `SpeechTables` mixin and tests for conversation tree.
* New Sphinx theme for documentation.

0.42.0
======

* Fix an issue which was ignoring all but the final directive of a scene.
* More robust organisation of directors notes. Key is formally `(path, shot_id, cue_index)`.

0.41.0
======

* Pass Turn attributes as keyword parameters to each Drama directive handler.
* Fix content of About endpoint.

0.40.0
======

* Some documentation fixes.
* Fix packaging of `balladeer.utils`.

0.39.0
======

* Allow parameter `class` from cue which renders at blockquote level.
* Render theme parameters as CSS root variables with `ballad-` prefix.
* Allow parameter `theme` from cue which populates root variables.
* Add theme utility to render colour swatches.
* Loader excludes `style` files by default.
* Allow parameter `style` from cue which specifies named style files.
* Improvements to `Page.paste` method.
* Detect sqlite files as Assets.

0.38.0
======

* Fixed a bug when building an assembly with Entity links.
* First online documentation.

0.37.0
======

Adds functionality for text adventures.

* Example 11: *Cloak of Darkness*. First working implementation.
* Added a standard *Detail* state for controlling verbosity.
* Unified the classic *Waypoint* with *State*.
* Added the *compass* module with classic code and tests.
* Added the *description* property to Entity.
* *Entity* gets *revert* attribute.
* Began to create API documentation.
* *Drama.active* is now a dictionary whose values are valid commands.

0.36.0
======

Minor fixes while preparing development blog.

* Fixes to examples 1 and 10.
* Better error handling during Asset discovery.
* `Story.context` now orders drama by integer state.
* Top-level imports are now all from `balladeer.lite`.

0.35.0
======

Bugfixes to example 8.

* Loader now offers better filtering of test modules, etc.
* Settled on a convention for naming of controls.

0.34.0
======

All examples now converted to the *lite* format.

* Loader discovery enhanced for hierarchical directories.
* Better calculation of asset paths.
* Command options added to assembly output.

0.33.0
======

Support for audio assets.

* Unique index and ordinal for each rendered block.
* Better structure for Director's notes.
* `audio` tags are rendered inside `details`.
* `audio` playback triggered by JS timer.

0.32.0
======

This is the 'MVP' release of the new *lite* format.

* `<cite>` tags get animation timing similar to `<p>` tags.
* Story objects now accept Speech on instantiation.
* Fixes to layout and formatting of some examples.

0.31.0
======

Provides a well-formed example to demonstrate JS integration.

* Refactored Story for easier override of page composition.
* Director notes now accessible via Turn object.
* Fix for Assembly endpoint.
* Better management and distribution of discovered assets.
* ex_06_js_frontend demonstrates integration with a JS application.

0.30.0
======

Full steam ahead with the *lite* variant. Extensive refactoring to implement these key features:

* Standardised on `Grouping.typewise` wherever appropriate.
* Added `sketch` and `aspect` to Entity.
* Director keeps sequential notes in a ChainMap.
* Clarified concepts of scene/shot/speech.
* Clarified Drama interfaces to actions/interlude/directions.
* Drama adopts Prologue/Dialogue/Epilogue as return types.
* Drama owns `prompt`.
* Director rewrite can re-order Prologue/Dialogue/Epilogue.
* Story is now a context manager and has return type `Turn`.

The following examples have been converted to use the *lite* API:

* ex_06_js_frontend
* ex_10_lite_sequence

0.29.0
======

Substantial effort towards implementation of *lite* variant.
Some key things to note:

* Decision on convention for naming of scene files (`.scene.toml`).
* Recreation of previous cartoon fight example to pin down casting priorities.
* Decoupling of Story (organisation) from Director (presentation).
* Some refinement around previous patterns used for World and Map.
* Lots more unit tests. Commitment to TDD. They run fast, too.

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
