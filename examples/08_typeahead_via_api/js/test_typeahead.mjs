/*
Test Driven Development of Javascript in a minimal, Pythonic style

 <venv>/bin/python -m unittest balladeer/test/test_drama.py

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

Install test dependencies:

    npm install tape

Run unit tests:

    npx -y tape js/test_*.mjs

* tape
* jsdom

Examples: https://github.com/dwyl/learn-tape
*/

import test from "tape";
import {filter_commands} from "./typeahead.mjs";

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
