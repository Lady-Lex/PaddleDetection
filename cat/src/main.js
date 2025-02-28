// import './assets/main.css';

import { createApp, ref } from 'vue';
import App from './App.vue';
const app = createApp(App);

import ElementPlus from 'element-plus';
import 'element-plus/dist/index.css';
app.use(ElementPlus)

// import 'codemirror/lib/codemirror.css';
// import VueCodeMirror from 'vue-codemirror';
// Vue.use(VueCodeMirror);

const user = ref({})
app.config.globalProperties.$user = user

app.mount('#app');