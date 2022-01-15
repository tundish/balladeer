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
            <avatar v-bind:bottle="bottle" v-on:change-product="display_product"></avatar>
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
},
methods: {
    display_product(bottle) {
        console.log(bottle.colour)
    }
}
});


app.component("avatar", {
props: {
    bottle: {
        type: Object,
        required: true
    }
},
template:  `
            <div class="bottle" v-on:mouseover="on_hover">
                <img src="/img/bottle.svg" alt="A green bottle" style="width: 3rem;"/>
                {{ bottle.colour }}
            </div>`,
data() {
    return {
    }
},
computed: {
},
methods: {
    on_hover() {
        this.$emit("change-product", this.bottle)
    }
}
});

view = app.mount("#app");
