import { createApp } from "vue";
import "./styles/main.css";
import router from "./router";
import pinia from "./store";
import App from "./App.vue";

const app = createApp(App);

app.use(pinia);
app.use(router);

app.mount("#app");

