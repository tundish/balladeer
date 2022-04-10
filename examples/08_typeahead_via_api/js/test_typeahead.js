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

    npx -y tape js/test_*.js

* tape
* jsdom

Examples: https://github.com/dwyl/learn-tape
*/
const test = require("tape");
const typeahead = require("./typeahead.js");
const commands = require("./commands.json");

test("check command fixture", function (t) {
    t.ok(Array.isArray(commands));
    t.ok(Array.isArray(commands[0]));
    t.equal(typeof commands[0][0], "string");
    t.equal(typeof commands[0][1], "object");
    t.end();
});
