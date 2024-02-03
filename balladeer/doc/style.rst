..  Titling
    ##++::==~~--''``

.. _`style section`:

Styles
======

There may come a moment in your Story when switching :ref:`themes<theme section>` is not
sufficient to get the effect you need. What you might prefer is a radical change to the entire
structure of the page.

As we've seen earlier, Balladeer discovers your Story assets when it starts up::

    Discovered in ex_12_styling_themes    : basics.css                           (text/css)
    Discovered in ex_12_styling_themes    : layout.css                           (text/css)
    Discovered in ex_12_styling_themes    : object.css                           (text/css)
    Discovered in ex_12_styling_themes    : style_01.css                         (text/css)
    Discovered in ex_12_styling_themes    : style_02.css                         (text/css)
    Discovered in ex_12_styling_themes    : style_03.css                         (text/css)
    Discovered in ex_12_styling_themes    : skye_terrier.png                     (image/png)
    Discovered in ex_12_styling_themes    : treacle_factory.png                  (image/png)

Every HTML page is rendered with links to the CSS files discovered in your project.

.. code-block:: html

    <link rel="stylesheet" href="/static/basics.css" />
    <link rel="stylesheet" href="/static/layout.css" />
    <link rel="stylesheet" href="/static/object.css" />

Can you spot which are missing? Balladeer excludes by default any CSS file with the word '*style*' in its name.
This includes its full file path, so you can choose to keep all such files in a single `styles` directory.

In order to activate one of these style files, you have to specify it via the `style` parameter in dialogue.
You need only set a substring of the style file name in order for it to be linked.
Of course, you can apply a theme at the same time too. 

.. literalinclude:: ../examples/ex_12_styling_themes/main.py
    :lines: 60-66

