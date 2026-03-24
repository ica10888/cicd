import axios from 'axios'

const http = axios.create({ baseURL: '/api', timeout: 10000 })

// 请求拦截器：自动附加 token
http.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Token ${token}`
  }
  return config
})

// 响应拦截器：token 失效时跳转登录
http.interceptors.response.use(
  res => res,
  err => {
    if (err.response?.status === 401) {
      localStorage.clear()
      window.location.href = '/login'
    }
    return Promise.reject(err)
  }
)

export const login = (data) => http.post('/login/', data)
export const getApps = () => http.get('/apps/')
export const createApp = (data) => http.post('/apps/', data)
export const updateApp = (id, data) => http.put(`/apps/${id}/`, data)
export const deleteApp = (id) => http.delete(`/apps/${id}/`)
export const getUsers = () => http.get('/users/')
export const createUser = (data) => http.post('/users/', data)
export const updateUser = (id, data) => http.put(`/users/${id}/`, data)
export const deleteUser = (id) => http.delete(`/users/${id}/`)
export const getRoles = () => http.get('/roles/')
export const createRole = (data) => http.post('/roles/', data)
export const updateRole = (id, data) => http.put(`/roles/${id}/`, data)
export const deleteRole = (id) => http.delete(`/roles/${id}/`)
export const getPermissions = (params) => http.get('/permissions/', { params })
export const createPermission = (data) => http.post('/permissions/', data)
export const updatePermission = (id, data) => http.put(`/permissions/${id}/`, data)
export const deletePermission = (id) => http.delete(`/permissions/${id}/`)
