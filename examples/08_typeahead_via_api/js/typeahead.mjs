/*
Typeahead functionality from URL endpoint.

*/

export function filter_commands(pairs, text="") {
    const cmds = pairs.map(pair => pair[0]);
    return new Set(cmds.filter(cmd => cmd.startsWith(text)));
}

export function handle_key_up(app, field) {
    return function(evt) {
        console.log(field.value);
    }
}
