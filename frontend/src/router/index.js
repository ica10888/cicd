import { createRouter, createWebHistory } from 'vue-router'
import UserLogin from '../views/UserLogin.vue'
import AdminLogin from '../views/AdminLogin.vue'
import AppList from '../views/AppList.vue'
import PermissionManage from '../views/PermissionManage.vue'

const routes = [
  { path: '/', redirect: '/login' },
  { path: '/login', component: UserLogin },
  { path: '/admin/login', component: AdminLogin },
  { path: '/apps', component: AppList },
  { path: '/permissions', component: PermissionManage },
]

export default createRouter({
  history: createWebHistory(),
  routes,
})
