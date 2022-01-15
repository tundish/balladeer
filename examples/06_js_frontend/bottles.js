const app = Vue.createApp({
})

app.component("diorama", {
template:  `
            <ul>
            <li v-for="bottle in unbroken">{{ bottle.colour }} </li>
            </ul>`,
async created() {
    url = window.location + "/assembly";
    const response = await fetch(url);
    const data = await response.json();
    this.population = data;
},
data() {
    return {
        population: []
    }
},
computed: {
    unbroken() {
        return this.population.filter(bottle => bottle._states.Fruition.value == 1)
    }
}
})

view = app.mount("#app")
