const app = Vue.createApp({
data() {
    return {
        population: []
    }
},
async created() {
    url = window.location + "/assembly";
    const response = await fetch(url);
    const data = await response.json();
    this.population = data;
},
});

app.component("diorama", {
props: {
    population: {
        type: Array,
        required: true
    }
},
template:  `
            <ul>
            <li v-for="bottle in unbroken">{{ bottle.colour }} </li>
            </ul>`,
data() {
    return {
    }
},
computed: {
    unbroken() {
        return this.population.filter(bottle => bottle._states.Fruition.value == 1);
    }
}
});

view = app.mount("#app");
