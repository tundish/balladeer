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
            <ul style="display: flex;">
            <li v-for="bottle in unbroken" style="flex-direction: row;">
            <div class="bottle">
                <img src="/img/bottle.svg" alt="A green bottle" style="width: 3rem;"/>
                {{ bottle.colour }}
            </div>
            </li>
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
