const app = Vue.createApp({
    data() {
        return {
            location: window.location,
            population: null
        }
    },
    async created() {
        url = window.location + "/assembly";
        const response = await fetch(url);
        const data = await response.json()
        this.population = data
    }
})

view = app.mount("#app")
