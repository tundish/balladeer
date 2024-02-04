..  Titling
    ##++::==~~--''``

.. _`theme section`:

Themes
======

CSS
~~~

The best way to change how your Story looks is to apply CSS rules to the HTML5 output.

The examples have some CSS files to get you started. I recommend separate files for different purposes.
Here's my own naming convention which you can adopt; or develop another as you wish.

==========  =======================================================================
CSS file    Focus
==========  =======================================================================
basics.css  Normalization. Generic defaults.
layout.css  Flex and Grid structures.
object.css  Thumbnails and decoration for specific story entities.
reveal.css  Animations and transitions.
style*.css  Scene-specific styling. See the :ref:`Styles page<Style section>` below.
==========  =======================================================================

Class
~~~~~

You can assign CSS classes to your dialogue using the `class` parameter like so:

.. literalinclude:: ../lite/test/test_director.py
    :lines: 767
    :dedent: 8

That will include your class in the HTML containing the speech::

    <blockquote class="warning" ...>

Theming
~~~~~~~

In order to maintain a consistency to the look of your Story, it's a good idea to use `CSS variables`_
to record your favourite colours, fonts, etc. That way, when you tweak them the changes will apply
to all the elements you have rules for.

The Balladeer :py:class:`~balladeer.lite.types.Page` class has a `themes` dictionary where you can organise
your CSS settings under convenient labels.

.. literalinclude:: ../lite/types.py
    :lines: 31-44

You can modify the default, or create themes of your own simply by adding them to the `themes` dictionary.

.. literalinclude:: ../examples/ex_12_styling_themes/main.py
    :lines: 16-26

A theme is rendered into each HTML page like so:

.. code-block:: html

    <style type="text/css">
    :root {
    --ballad-ink-gravity: hsl(282.86, 0%, 6.12%);
    --ballad-ink-shadows: hsl(293.33, 0%, 22.75%);
    --ballad-ink-lolight: hsl(203.39, 0%, 31.96%);
    --ballad-ink-midtone: hsl(203.39, 0%, 41.96%);
    --ballad-ink-hilight: hsl(203.06, 0%, 56.47%);
    --ballad-ink-washout: hsl(66.77, 0%, 82.75%);
    --ballad-ink-glamour: hsl(50.00, 0%, 100%);
    }
    </style>

Balladeer switches the theme for you when you want to depart from the default:

.. literalinclude:: ../lite/test/test_director.py
    :lines: 787
    :dedent: 8

.. _CSS variables: https://developer.mozilla.org/en-US/docs/Web/CSS/Using_CSS_custom_properties
.. _Weasyprint: https://weasyprint.org/
