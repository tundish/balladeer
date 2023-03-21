/*
Test Driven Development of Javascript in a minimal, Pythonic style

Install Node
------------

Visit https://github.com/nvm-sh/nvm to find the latest stable version of NVM.
Then install it like this:

    curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.1/install.sh | bash
    source ~/.bashrc
    command -v nvm

Now install the latest version of node.js:

    nvm install node
    command -v corepack

Install dependencies
--------------------

Install test dependencies:

    npm install tape jsdom

Run tests
---------

Run unit tests:

    npx -y tape js/test_*.mjs

For more on Tape testing: https://github.com/dwyl/learn-tape

*/

import jsdom from "jsdom";
import test from "tape";
import {fill_options, filter_commands} from "./typeahead.mjs";

import commands from "./commands.json" assert {type: "json"};


test("check command fixture", function (t) {
    t.ok(Array.isArray(commands));
    t.ok(Array.isArray(commands[0]));
    t.equal(typeof commands[0][0], "string");
    t.equal(typeof commands[0][1], "object");
    t.end();
});

test("filter with no previous text", function (t) {
    const rv = filter_commands(commands);
    t.notEqual(rv.size, commands.length);
    t.equal(rv.size, 9);
    t.end();
});

test("filter with previous 'break' command", function (t) {
    const rv = filter_commands(commands, "break");
    t.notEqual(rv.size, commands.length);
    t.equal(rv.size, 8);
    t.end();
});

test("filter with previous 'l' character", function (t) {
    const rv = filter_commands(commands, "l");
    t.notEqual(rv.size, commands.length);
    t.equal(rv.size, 1);
    t.end();
});

test("fill options into empty datalist", function (t) {
    const dom = new jsdom.JSDOM(
        '<!DOCTYPE html><body><datalist id="parent"></datalist></body></html>'
    );
    let node = dom.window.document.getElementById("parent");
    let options = filter_commands(commands);
    const rv = fill_options(node, commands);
    t.same(rv, node);
    t.equal(rv.childNodes.length, commands.length);
    t.end();
});

