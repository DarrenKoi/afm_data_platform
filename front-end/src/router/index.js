/**
 * router/index.js
 *
 * Manual route configuration
 */

import { createRouter, createWebHistory } from 'vue-router'
import MainPage from '@/pages/MainPage.vue'
import ResultPage from '@/pages/ResultPage.vue'
import DataTrendPage from '@/pages/DataTrendPage.vue'
import AboutPage from '@/pages/AboutPage.vue'
import ContactPage from '@/pages/ContactPage.vue'

const routes = [
  {
    path: '/',
    name: 'MainPage',
    component: MainPage
  },
  {
    path: '/about',
    name: 'AboutPage',
    component: AboutPage
  },
  {
    path: '/contact',
    name: 'ContactPage',
    component: ContactPage
  },
  {
    path: '/result/:recipeId/:groupKey',
    name: 'ResultPage',
    component: ResultPage
  },
  {
    path: '/result/data_trend',
    name: 'DataTrendPage',
    component: DataTrendPage
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

export default router
