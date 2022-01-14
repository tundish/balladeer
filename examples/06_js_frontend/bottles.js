const app = Vue.createApp({
    data() {
        return {
            location: window.location,
            population: []
        }
    },
    computed: {
        unbroken() {
            return this.population.filter(bottle => bottle._states.Fruition.value == 1)
        }
    },
    async created() {
        url = window.location + "/assembly";
        const response = await fetch(url);
        const data = await response.json();
        this.population = data;
    }
})

view = app.mount("#app")
