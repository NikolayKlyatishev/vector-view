import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import App from './App.vue'
import './style.css'

// Импорт компонентов
import DatabaseView from './components/DatabaseView.vue'
import TableView from './components/TableView.vue'

const routes = [
  { path: '/', component: DatabaseView },
  { path: '/table/:tableName', component: TableView, props: true }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

const app = createApp(App)
app.use(router)
app.mount('#app')
