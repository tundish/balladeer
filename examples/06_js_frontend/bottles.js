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
            <div id="product" style="height: calc(30vh + 1rem);">
            <img v-if="this.selected" v-bind:src="this.products[this.selected.colour].image" alt="A green bottle"
            style="height: 30vh; width: auto;"/>
            <p v-if="this.selected">{{ this.products[this.selected.colour].details }}</p>
            </div>
            <ul style="display: flex;">
            <li v-for="bottle in unbroken" style="flex-direction: row;">
            <avatar v-bind:bottle="bottle" v-on:change-product="display_product"></avatar>
            </li>
            </ul>`,
data() {
    return {
        selected: null,
        products: {
            "#00FF00": {
                details: "Soda bottle",
                image: "https://i.pinimg.com/originals/b4/a9/2c/b4a92c9a015b6e7956f15fad06ad0e7f.jpg"
            },
            "#00EE00": {
                details: "Seltzer bottle",
                image: "https://i.pinimg.com/originals/65/12/36/6512367421478d0f9f4322cfe9c7ecbb.jpg"
            },
            "#00DD00": {
                details: "Spring Water bottle",
                image: "https://i.pinimg.com/originals/34/71/81/347181f915bbed4fdea575b189447540.jpg"
            }
        }
    }
},
computed: {
    unbroken() {
        return this.population.filter(bottle => bottle._states.Fruition.value == 1);
    }
},
methods: {
    display_product(bottle) {
        this.selected = bottle
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
            <svg width="64" height="128" viewBox="0 0 16.933333 33.866668">
                <g transform="translate(0,-263.13332)">
                <path v-bind:style="{fill: bottle.colour}"
                   id="bottle_icon"
                   d="m 3.5529357,277.11367 2.197229,-3.2128 c 0.7226776,-2.79225 0.3073479,-8.64619 0.496336,-8.88243 0.9921875,-0.18899 3.9692343,-0.18904 4.2999633,0.0472 0,0 -0.141256,8.032 0.520202,8.69346 l 2.173848,3.07105 c 0,0 1.228423,1.58374 1.559152,3.23739 0,0 0.425223,12.07259 0,15.0964 0.188988,0.8032 -11.4829654,0.99219 -12.664141,0 -0.6142113,-2.50409 0,-15.0964 0,-15.0964 0,-1.22842 1.4174107,-2.95387 1.4174107,-2.95387 z"
                   style="fill-opacity:1;stroke:#000000;stroke-width:0.8;stroke-linecap:round;stroke-miterlimit:4;stroke-dasharray:none;stroke-dashoffset:0;paint-order:fill markers stroke" />
                </g>
            </svg>
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
