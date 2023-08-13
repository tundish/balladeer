..  Titling
    ##++::==~~--''``

.. _`theme section`:

Themes
======

CSS
~~~

The best way to change how your Story looks is to apply CSS rules to the HTML5 output.

The examples have some CSS files to get you started. I recommend separate files for different purposes.
Here's my own naming convention, which you are welcome to adopt for yourself.

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
    :lines: 652
    :dedent: 8

That will include your class in the HTML containing the speech::

    <blockquote class="warning" ...>

Theming
~~~~~~~

.. _Weasyprint: https://weasyprint.org/
