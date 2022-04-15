/*
Text input 'typeahead' functionality with data from a URL endpoint.

It's possible to achieve a typeahead without any Javascript; simply render the
the datalist element on the server side.

Done that way, there are only limited options for styling.
This demo gets you started with populating the data list in JS.
You can incorporate more advanced features based on this prototype.

*/

export function filter_commands(pairs, text="") {
    const cmds = pairs.map(pair => pair[0]);
    return new Set(cmds.filter(cmd => cmd.startsWith(text)));
}

export function fill_options(node, commands=[]) {
    for (const command of commands) {
        let option = node.ownerDocument.createElement("option");
        option.setAttribute("value", command);
        option.innerHTML = command;
        node.append(option);
    }
    return node;
}

export function handle_key_up(app, field) {
    /*
    If you need more flexibility, remove the list attribute from
    the input field and use this event handler to implement your
    own custom behaviour:

    input.onkeyup = handle_key_up(this, input);

    */
    return function(evt) {
        console.log(field.value);
    }
}
