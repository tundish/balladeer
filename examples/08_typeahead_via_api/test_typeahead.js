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

    npx -y tape test_*.js

* tape
* jsdom

*/
var test = require('tape');

test('timing test', function (t) {
    t.plan(2);

    t.equal(typeof Date.now, 'function');
    var start = Date.now();

    setTimeout(function () {
        t.equal(Date.now() - start, 100);
    }, 100);
});

test('test using promises', async function (t) {
    const result = await someAsyncThing();
    t.ok(result);
});
