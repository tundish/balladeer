#!/usr/bin/env python
#   encoding: utf-8

# This is part of the Balladeer library.
# Copyright (C) 2023 D E Haynes

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import html
import re
import textwrap
import tomllib
import unittest

import balladeer
from balladeer.lite.speechmark import SpeechMark

__doc__ = f"""
:Version: {balladeer.__version__}
:Author: D E Haynes
:Licence: `CC BY-NC-ND <https://creativecommons.org/licenses/by-nc-nd/4.0/>`_ Attribution-NonCommercial-NoDerivs

"""

# block = cue + dialogue
# cue = persona .directive @ entity, :mode ? parameters # fragment


# Ex 2
"""
<blockquote>
<header>Mandelbrot </header>
<p><span class="text">Look, if you can't make a proper analysis of the situation, why don't you&NewLine;pick at </span>
<a href="https://www.random.org/integers/?num=1&min=1&max=3&col=1&base=10&format=html">random</a>
<span class="text">&quest;</span></p>
</blockquote>
"""

# Plugins must allow for transformation of links, eg:
"""
<nav>
<ul>
<li style="animation-delay: 22.80s; animation-duration: 3.70s">
<form role="form" action="False" method="GET" name="contents">

</form></li>
</ul>
</nav>
"""


# Ordered list marker: '[0-9a-zA-Z].' (remember fragment reference)
# Unordered list marker: '+'
# <em>:  one or more *
# <strong>: _
# <code>:  `
# <a>: [label](url)

Head = ("propose", "confirm", "counter", "abandon", "condemn", "declare")


Hand = ("decline", "suggest", "promise", "disavow", "deliver")


class Syntax(unittest.TestCase):
    """
    SpeechMark
    ##########

    SpeechMark is a convention for markup of authored text.
    It is suited for capturing dialogue, attributing speech, and writing screenplay directions.
    This document explains the syntax, and shows how it should be rendered in HTML5.

    SpeechMark takes inspiration from other markup systems already in common use, eg:

    * `Markdown <https://commonmark.org/>`_
    * `RestructuredText <https://docutils.sourceforge.io/rst.html>`_

    I tried both these systems prior to creating SpeechMark. I found I needed some features which
    Markdown didn't have. RST proved to be overkill for this particular purpose, and the document model
    became cumbersome to me.

    Philosophy
    ==========

    SpeechMark syntax is deliberately constrained to be simple and unambiguous.
    This is to permit fast and efficient processing of many small pieces of text over an extended period of time.

    SpeechMark does not concern itself with document structure. There are no titles, sections or breaks.
    Rather, the input is expected to be a stream of text fragments.

    The specification intends to be lossless, so that every non-whitespace feature of the original text
    may be retrieved from the output. It should be possible to round-trip your SpeechMark scripts into
    HTML5 and back again.

    Features
    ========

    SpeechMark has the basic elements you see in other markup systems, ie:

        * Emphasis_
        * Hyperlinks_
        * Comments_
        * Lists_

    There is one feature very specific to SpeechMark:

        * Cues_

    SpeechMark doesn't try to do everything. To integrate it into an application, you may
    need:

        * Preprocessing_
        * Postprocessing_

    Emphasis
    --------

    SpeechMark supports three flavours of emphasis.

    * Surround text by asterisks ``*like this*`` to generate ``<em>`` tags.
    * Use underscores ``_like this_`` to generate ``<strong>`` tags.
    * Use backticks ```like this``` to generate ``<code>`` tags.

    Hyperlinks
    ----------

    Hyperlinks have two components; the label and the URL.
    The label appears first within square brackets, followed by the URL in parentheses::

        [SpeechMark](https://github.com/tundish/speechmark)

    Comments
    --------

    The `#` character denotes a comment. It must be the first character on a line::

        # Comments aren't ignored. They get converted to HTML (<!-- -->)

    Lists
    -----

    Unordered lists
    ```````````````

    The `+` character creates a list item of the text which follows it, like so::

        + Beef
        + Lamb
        + Fish


    Ordered lists
    `````````````
    Using digits and a dot before text will give you an ordered list::

        1. Beef
        2. Lamb
        3. Fish

    Cues
    ----

    A cue marks the start of a new block of dialogue. Is is denoted by angled brackets::

        <>  Once upon a time, far far away...

    Cues are flexible structures. They have a number of features you can use all together, or
    you can leave them empty.

    A cue may contain information about the speaker of the dialogue, and how they deliver it.

    The most basic of these is the **role**. This is the named origin of the lines of dialogue.
    It is recommended that you state the role in upper case letters, eg: GUEST, STAFF.
    Inanimate objects can speak too of course. Eg: KETTLE, and PHONE::

        <PHONE> Ring riiing!

    The **mode** declares the form in which the act of speech is delivered.
    Although it's the most common, *says* is just one of many possible modes of speech.
    There are others you might want to use, like *whispers* or *thinks*.
    The mode is separated by a colon::

        <GUEST:thinks> I wonder if anyone is going to answer that phone.

    Capturing the mode of speech enables different presentation options,
    eg: character animations to match the delivery.
    Modes of speech should be stated in the simple present, third person form.

    **Directives** indicate that there are specific side-effects to the delivery of the dialogue.
    They may be used to fire transitions in a state machine, specifying that the speech achieves
    progress according to some social protocol.

    It's recommended that these directives be stated as present participles
    such as *promising* or *declining*::

        <PHONE.announcing> Ring riiing!

    Directives, being transitive in nature, sometimes demand objects to their action. So you may
    specify the recipient roles of the directive if necessary too::

        <PHONE.announcing@GUEST,STAFF> Ring riiing!

    **Parameters** are key-value pairs which modify the presentation of the dialogue. SpeechMark borrows the
    Web URL syntax for parameters (first a '?', with '&' as the delimiter).

    Their meaning is specific to the application. For example, it might be necessary to specify
    some exact timing for the revealing of the text::

        <?pause=3&dwell=0.4>

            From above there is the sound of footsteps.

            Snagging on a threadbare carpet.

            Then shuffling down the ancient stairs.

    SpeechMark recognises the concept of **fragments**, which also come from URLs. That's the part after a '#'
    symbol. You can use the fragment to refer to items in a list::

        <STAFF.proposing#3> What will you have, sir? The special is fish today.

            1. Order the Beef Wellington
            2. Go for the Shepherd's Pie
            3. Try the Dover Sole

    Preprocessing
    =============

    Whitespace
    ----------

    A SpeechMark parser expects certain delimiters to appear only at the beginning of a line.
    Therefore, if your marked-up text has been loaded from a file or data structure, you may need to
    remove any common indentation and trim the lines of whitespace characters.

    Variable substitution
    ---------------------

    It is a very useful trick for dialogue to reference attributes of the objects in scope,
    eg: ``GUEST.surname``.

    Unfortunately, the syntax for variable substitution is language dependent.
    Equally the mode of attribute access is application dependent.
    Should it be ``GUEST.surname`` or ``GUEST['surname']``?

    SpeechMark therefore does not provide this ability, and it must be performed prior to parsing.
    Here's an example using Python string formatting, where the context variables are dictionaries::

        <GUEST> I'll have the Fish, please.

        <STAFF> Very good, {GUEST['honorific']} {GUEST['surname']}.


    Postprocessing
    ==============

    Pruning
    -------

    SpeechMark tries not to throw anything away. You might not want that behaviour. Specifically,
    you may prefer to remove lines of comment from the HTML5 output.

    Since the output is line-based, it's a simple matter to strip out those lines using your favourite prgramming
    language or command line tools.

    Extending
    ---------

    Speechmark does not support extensions. There is no syntax to create custom tags.

    However, if you need to transform the output before it gets to the web, you could utilise the
    ``<code>`` tag for that purpose.

    Suppose you have a menu you've defined as a list::

        + `button`[Map](/api/map)
        + `button`[Inventory](/api/inventory)

    Here is part of that output::

        <li><p><code>button</code><a href="/api/map">Map</a></p></li>

    This could be sufficient to trigger a ``button`` function in your postprocessor which replaces
    the bare link with a ``<form>`` and ``<input>`` controls to pop up the map.

    Specification
    =============

    1. General
    ----------

    1.1
    ```

    SpeechMark input must be line-based text, and should have UTF-8 encoding.

    1.2
    ```

    Inline markup must consist of pairs of matching delimiters. There must be no line break within them;
    all inline markup must terminate on the same line where it begins. Delimiters may not contain other
    delimiter pairs. There is no nested markup.

    1.3
    ```

    The generated output must be one or more HTML5 ``blockquote`` elements.
    All elements must be explicitly terminated.

    1.4
    ```

    All output must be placed within blocks. Each block may begin with a cite element. A block may contain one
    or more paragraphs. A block may contain a list. Every list item must contain a paragraph.

    """
    examples = []

    def example(label=""):
        def wrapper(fn):
            def inner(self, *args, **kwargs):
                return fn(self, **data)
            doc = fn.__doc__ or ""
            text, toml = re.split(r"#\W*TOML\n", doc, maxsplit=1)
            data = tomllib.loads(toml)
            Syntax.examples.append((label, text, data, fn))
            fn.__doc__ = text
            return inner
        return wrapper

    def check(self, markup: dict={}, output=""):
        sm = SpeechMark()
        for n, (tag, text) in enumerate(markup.items()):
            text = textwrap.dedent(text).strip()
            with self.subTest(n=n, tag=tag, text=text):
                rv = sm.loads(text)
                self.compare(rv, output)

    def compare(self, a, b, msg=""):
        x = "".join(i.strip() for i in a.splitlines())
        y = "".join(i.strip() for i in b.splitlines())
        self.assertEqual(x, y, msg or a)


class EmphasisTests(Syntax):
    """
    2. Emphasis
    -----------

    """

    @Syntax.example(label="2.01")
    def test_minimal_emphasis(self, markup: dict={}, output=""):
        """
        Emphasis is added using pairs of asterisks.

        # TOML
        markup."Single instance"  =   "*Definitely!*"
        output = '''
        <blockquote>
        <p><em>Definitely!</em></p>
        </blockquote>
        '''
        """
        return self.check(markup, output)

    @Syntax.example(label="2.02")
    def test_multiple_emphasis(self, markup: dict={}, output=""):
        """
        There may be multiple emphasized phrases on a line.

        # TOML
        markup."Multiple instances" =   "*Definitely* *Definitely!*"
        output = '''
        <blockquote>
        <p><em>Definitely</em> <em>Definitely!</em></p>
        </blockquote>
        '''
        """
        return self.check(markup, output)

    def test_cornercases_abutting_emphasis(self):
        expected = textwrap.dedent("""
        <blockquote>
        <p><em>Definitely</em><em>Definitely!</em></p>
        </blockquote>
        """)
        sm = SpeechMark()
        rv = sm.loads("*Definitely**Definitely!*")
        self.compare(rv, expected, rv)


class SignificanceTests(Syntax):
    @Syntax.example(label="2.03")
    def test_minimal_significance(self, markup: dict={}, output=""):
        """
        Strong text is denoted with underscores.

        # TOML
        markup."Single instance"  =   "_Warning!_"
        output = '''
        <blockquote>
        <p><strong>Warning!</strong></p>
        </blockquote>
        '''
        """
        return self.check(markup, output)

    @Syntax.example(label="2.04")
    def test_multiple_significance(self, markup: dict={}, output=""):
        """
        There may be multiple snippets of significant text on one line.

        # TOML
        markup."Multiple instances" =   "_Warning_ _Warning_!"
        output = '''
        <blockquote>
        <p><strong>Warning</strong> <strong>Warning</strong>!</p>
        </blockquote>
        '''
        """
        return self.check(markup, output)

    def test_cornercases_code(self):
        expected = textwrap.dedent("""
        <blockquote>
        <p>
        <strong>Warning</strong><strong>Warning</strong>!
        </p>
        </blockquote>
        """)
        sm = SpeechMark()
        rv = sm.loads("_Warning__Warning_!")
        self.compare(rv, expected, rv)


class CodeTests(Syntax):

    @Syntax.example(label="2.05")
    def test_single_code(self, markup: dict={}, output=""):
        """
        Code snippets are defined between backticks.

        # TOML
        markup."Single instance"  =   "`git log`"
        output = '''
        <blockquote>
        <p><code>git log</code></p>
        </blockquote>
        '''
        """
        return self.check(markup, output)

    @Syntax.example(label="2.06")
    def test_multiple_code(self, markup: dict={}, output=""):
        """
        There may be multiple code snippets on a line.

        # TOML
        markup."Multiple instances" =   "`git` `log`"
        output = '''
        <blockquote>
        <p><code>git</code> <code>log</code></p>
        </blockquote>
        '''
        """
        return self.check(markup, output)

    def test_cornercases_code(self):
        expected = textwrap.dedent("""
        <blockquote>
        <p><code>8.8.8.8</code></p>
        </blockquote>
        """)
        sm = SpeechMark()
        rv = sm.loads("`8.8.8.8`")
        self.compare(rv, expected, rv)

    def test_cornercases_abutted_code(self):
        expected = textwrap.dedent("""
        <blockquote>
        <p><code>git</code><code>log</code></p>
        </blockquote>
        """)
        sm = SpeechMark()
        rv = sm.loads("`git``log`")
        self.compare(rv, expected, rv)


class LinkTests(Syntax):
    """
    3. Hyperlinks
    -------------

    """

    def test_basic_match(self):
        sm = SpeechMark()
        match = sm.link_matcher.match("[Python](https://python.org)")
        self.assertTrue(match)
        self.assertEqual("Python", match.groupdict().get("label"))
        self.assertEqual("https://python.org", match.groupdict().get("link"))

    @Syntax.example(label="3.01")
    def test_single_link(self, markup: dict={}, output=""):
        """
        Hyperlinks are defined by placing link text within square brackets and the link destination
        in parentheses. There must be no space between them.
        See also https://spec.commonmark.org/0.30/#example-482.

        # TOML
        markup."Single instance"  =    "[Python](https://python.org)"
        output = '''
        <blockquote>
        <p><a href="https://python.org">Python</a></p>
        </blockquote>
        '''
        """
        return self.check(markup, output)

    @Syntax.example(label="3.02")
    def test_multiple_links(self, markup: dict={}, output=""):
        """
        There may be multiple hyperlinks on a line.

        # TOML
        markup."Multiple instances" =  "[Python](https://python.org) [PyPI](https://pypi.org)"
        output = '''
        <blockquote>
        <p><a href="https://python.org">Python</a> <a href="https://pypi.org">PyPI</a></p>
        </blockquote>
        '''
        """
        return self.check(markup, output)

    def test_cornercases_links_with_spaces(self):
        expected = textwrap.dedent("""
        <blockquote>
        <p>[Python] (https://python.org)</p>
        </blockquote>
        """)
        sm = SpeechMark()
        rv = sm.loads("[Python] (https://python.org)")
        self.compare(rv, expected, rv)

    def test_cornercases_abutting_links(self):
        expected = textwrap.dedent("""
        <blockquote>
        <p><a href="https://python.org">Python</a><a href="https://python.org">Python</a></p>
        </blockquote>
        """)
        sm = SpeechMark()
        rv = sm.loads("[Python](https://python.org)[Python](https://python.org)")
        self.compare(rv, expected, rv)


class CommentTests(Syntax):
    """
    4. Comments
    -----------

    """

    @Syntax.example(label="4.01")
    def test_single_comment(self, markup: dict={}, output=""):
        """
        Any line beginning with a "#" is a comment.
        It is output in its entirety (including delimiter) as an HTML comment.

        # TOML
        markup."Single instance"  =    "# TODO"
        output = '''
        <blockquote>
        <!-- # TODO -->
        </blockquote>
        '''
        """
        return self.check(markup, output)


class UnorderedListTests(Syntax):
    """
    5. Lists
    --------

    """

    @Syntax.example(label="5.01")
    def test_minimal_list(self, markup: dict={}, output=""):
        """
        A line beginning with a '+' character constitutes an
        item in an unordered list.

        # TOML
        markup."Single list"  =  '''
        + Hat
        + Gloves
        '''
        output = '''
        <blockquote>
        <ul>
        <li><p>Hat</p></li>
        <li><p>Gloves</p></li>
        </ul>
        </blockquote>
        '''
        """
        return self.check(markup, output)


class OrderedListTests(Syntax):

    @Syntax.example(label="5.02")
    def test_numbered_list(self, markup: dict={}, output=""):
        """
        Ordered lists have lines which begin with one or more digits. Then a dot, and at least one space.

        # TOML
        markup."Single list"  =  '''
        1. Hat
        2. Gloves
        '''
        output = '''
        <blockquote>
        <ol>
        <li id="1"><p>Hat</p></li>
        <li id="2"><p>Gloves</p></li>
        </ol>
        </blockquote>
        '''
        """
        return self.check(markup, output)

    @Syntax.example(label="5.03")
    def test_zeropadded_list(self, markup: dict={}, output=""):
        """
        Ordered list numbering is exactly as declared. No normalization is performed.

        # TOML
        markup."Single list"  =  '''
        01. Hat
        02. Gloves
        '''
        output = '''
        <blockquote>
        <ol>
        <li id="01"><p>Hat</p></li>
        <li id="02"><p>Gloves</p></li>
        </ol>
        </blockquote>
        '''
        """
        return self.check(markup, output)

    def test_list_matching_positive(self):
        examples = [
            "+Hat", "+ Hat", "+ <Hat>",
            "1.Hat", "1. Hat", "1. <Hat>",
            "01.Hat", "01. Hat", "01. <Hat>",
        ]
        sm = SpeechMark()
        for line in examples:
            with self.subTest(line=line):
                rv = sm.list_matcher.match(line)
                self.assertTrue(rv)
                d = rv.groupdict()
                self.assertEqual(1, len(d))

    def test_list_matching_negative(self):
        examples = [ "<> +", ]
        sm = SpeechMark()
        for line in examples:
            with self.subTest(line=line):
                rv = sm.list_matcher.match(line)
                self.assertFalse(rv)


class CueTests(Syntax):
    """
    6. Cues
    -------

    A cue mark generates a new block.

    6.01
    ````
    A generated ``blockquote`` tag may store the original cue string in its ``cite`` attribute.
    The string must be appropriately escaped.

    """

    @Syntax.example(label="6.02")
    def test_single_link(self, markup: dict={}, output=""):
        """
        All components of a cue are optional.

        # TOML
        markup."Anonymous cue"  =    "<> Once upon a time, far, far away..."
        output = '''
        <blockquote cite="&lt;&gt;">
        <p>Once upon a time, far, far away...</p>
        </blockquote>
        '''
        """
        return self.check(markup, output)

    def test_anonymous_cue(self):
        cue = ""
        line = f"<{cue}> Hello!"
        expected = textwrap.dedent(f"""
        <blockquote cite="&lt;&gt;">
        <p>Hello!</p>
        </blockquote>
        """)
        sm = SpeechMark()
        rv = sm.loads(line)
        self.compare(rv, expected, rv)

    def test_simple_cue(self):
        cue = role = "GUEST"
        line = f"<{cue}> Hello?"
        expected = textwrap.dedent(f"""
        <blockquote cite="&lt;{role}&gt;">
        <cite data-role="GUEST">{role}</cite>
        <p>Hello?</p>
        </blockquote>
        """)
        sm = SpeechMark()
        rv = sm.loads(line)
        self.compare(rv, expected, rv)

    def test_role_mode_cue(self):
        role = "GUEST"
        mode = "says"
        cue = f"{role}:{mode}"
        line = f"<{cue}> Hello?"
        expected = textwrap.dedent(f"""
        <blockquote cite="&lt;{cue}&gt;">
        <cite data-role="{role}" data-mode=":{mode}">{role}</cite>
        <p>Hello?</p>
        </blockquote>
        """)
        sm = SpeechMark()
        rv = sm.loads(line)
        self.compare(rv, expected, rv)

    def test_cue_matching_positive(self):
        examples = [
            "<>", "<> Hi!",
            "<role>", "<ROLE>",
            "<role:mode>", "<ROLE:MODE>",
            "<ROLE.d1.d2:mode>",
            "<ROLE:mode?p=0&q=a>",
            "<ROLE:mode#frag>",
            "<ROLE#frag>",
            "<ROLE.d1.d2:mode?p=0&q=a>",
            "<ROLE.d1.d2:mode?p=0&q=a#frag>",
        ]
        sm = SpeechMark()
        for line in examples:
            with self.subTest(line=line):
                rv = sm.cue_matcher.match(line)
                self.assertTrue(rv)
                d = rv.groupdict()
                self.assertEqual(5, len(d))

    def test_cue_matching_negative(self):
        examples = [
            "< >", "< >Hi!",
            "<role >", "< ROLE>"
        ]
        sm = SpeechMark()
        for line in examples:
            with self.subTest(line=line):
                rv = sm.cue_matcher.match(line)
                self.assertFalse(rv)


class ParagraphTests(Syntax):

    def test_minimal_paragraph(self, markup: dict={}, output=""):
        """
        Simple strings are encapsulated in paragraphs.

        # TOML
        markup."Plain string"  =   "Hello!"
        output = '''
        <blockquote>
        <p>Hello!</p>
        </blockquote>
        '''
        """
        return self.check(markup, output)

    def test_continuing_paragraph(self, markup: dict={}, output=""):
        """
        A paragraph continues until explicitly terminated.

        # TOML
        markup."Continuous string"  =   '''
        Hello!
        Hello!'''
        output = '''
        <blockquote>
        <p>Hello! Hello!</p>
        </blockquote>
        '''
        """
        return self.check(markup, output)

    @Syntax.example()
    def test_multiple_paragraphs(self, markup: dict={}, output=""):
        """
        A paragraph is terminated by a blank line.

        # TOML
        markup."Broken string"  =   '''
        Hello!

        Hello!'''
        output = '''
        <blockquote>
        <p>Hello!</p>
        <p>Hello!</p>
        </blockquote>
        '''
        """
        return self.check(markup, output)

    def test_cornercases_code(self):
        expected = textwrap.dedent("""
        <blockquote cite="&lt;&gt;">
        <p>Hello!</p>
        </blockquote>
        """)
        sm = SpeechMark()
        rv = sm.loads("<> Hello!")
        self.compare(rv, expected, rv)


class EscapingTests(Syntax):

    def test_text_escaping(self):
        sm = SpeechMark()
        for char in ">&<":
            text = f" M {char} B?"
            with self.subTest(text=text):
                rv = sm.loads(text)
                self.assertIn(html.escape(char), rv)

    def test_label_escaping(self):
        sm = SpeechMark()
        for char in ">&<":
            text = f"[M {char} B?](http://google.com)"
            with self.subTest(text=text):
                rv = sm.loads(text)
                self.assertIn(html.escape(char), rv)


class BlockTests(Syntax):

    @Syntax.example()
    def test_multiple_paragraphs(self, markup: dict={}, output=""):
        """
        A cue is used as an attribution of speech.

        # TOML
        markup."Checking in" = '''

        <GUEST> Hello?

        Is *anyone* there?

        '''
        output = '''
        <blockquote cite="&lt;GUEST&gt;">
        <cite data-role="GUEST">GUEST</cite>
        <p>Hello?</p>
        <p>Is <em>anyone</em> there?</p>
        </blockquote>
        '''
        """
        sm = SpeechMark()
        return self.check(markup, output)

    @Syntax.example()
    def test_choice_lists(self, markup: dict={}, output=""):
        """
        # TOML
        markup."Dialogue options" = '''
        <STAFF.suggesting#3> What would you like sir? We have some very good fish today.
            1. Order the Beef Wellington
            2. Go for the Cottage Pie
            3. Try the Dover Sole

        '''
        output = '''
        <blockquote cite="&lt;STAFF.suggesting#3&gt;">
        <cite data-role="STAFF" data-directives=".suggesting" data-fragments="#3">STAFF</cite>
        <p>What would you like sir? We have some very good fish today.</p>
        <ol>
        <li id="1"><p>Order the Beef Wellington</p></li>
        <li id="2"><p>Go for the Cottage Pie</p></li>
        <li id="3"><p>Try the Dover Sole</p></li>
        </ol>
        </blockquote>
        '''
        """
        sm = SpeechMark()
        return self.check(markup, output)


if __name__ == "__main__":
    from collections import defaultdict
    import inspect

    examples = defaultdict(list)
    for label, text, data, fn in sorted(Syntax.examples):
        info = dict(inspect.getmembers(fn)) # ["__self__"]["__class__"]
        cls = globals().get(info["__qualname__"].split(".")[0])
        examples[cls].append((label, text, data, fn))

    if __doc__:
        print(textwrap.dedent(__doc__))

    print(textwrap.dedent(Syntax.__doc__))
    for cls, entries in examples.items():
        if cls.__doc__:
            print(textwrap.dedent(cls.__doc__))
        for label, text, data, fn in entries:
            if not label:
                continue

            print(label)
            print("`" * len(label))
            print(textwrap.dedent(text))

            for note, snippet in data.get("markup", {}).items():
                print(f"{note}::\n")
                print(textwrap.indent(snippet, " " * 4))
                print()
                output = data.get("output", "")

                print("HTML5 output::\n")
                print(textwrap.indent(output, " " * 4))
                print()
