<template>
  <div class="login-page admin">
    <el-card class="login-card">
      <template #header>
        <div class="card-header">
          <div class="brand-logo">📱</div>
          <h1 class="brand-title">应用管理系统</h1>
          <div class="admin-badge-wrapper">
            <el-tag type="warning" class="admin-badge">管理员</el-tag>
          </div>
          <p class="login-subtitle">管理员登录</p>
        </div>
      </template>
      <el-form :model="form" :rules="rules" ref="formRef" label-width="80px">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="form.username" placeholder="请输入管理员账号" />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input v-model="form.password" type="password" placeholder="请输入密码" show-password />
        </el-form-item>
        <el-form-item>
          <el-button type="warning" :loading="loading" @click="handleLogin" class="login-button">
            管理员登录
          </el-button>
        </el-form-item>
        <el-form-item>
          <el-link type="info" @click="$router.push('/login')">← 普通用户登录</el-link>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { login } from '../api/index.js'

const router = useRouter()
const formRef = ref()
const loading = ref(false)
const form = reactive({ username: '', password: '' })
const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
}

async function handleLogin() {
  await formRef.value.validate()
  loading.value = true
  try {
    const { data } = await login({ ...form, role: 'admin' })
    if (data.code === 200) {
      sessionStorage.setItem('user', JSON.stringify(data.data))
      ElMessage.success('登录成功')
      router.push('/apps')
    } else {
      ElMessage.error(data.msg)
    }
  } catch {
    ElMessage.error('请求失败，请检查网络')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f7fa;
  padding: 20px;
}
.login-card {
  max-width: 400px;
  width: 100%;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}
.card-header {
  text-align: center;
  padding: 8px 0;
}
.brand-logo {
  font-size: 48px;
  margin-bottom: 12px;
}
.brand-title {
  font-size: 24px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 8px 0;
}
.admin-badge-wrapper {
  margin: 8px 0;
}
.admin-badge {
  font-size: 14px;
}
.login-subtitle {
  font-size: 16px;
  color: #909399;
  margin: 0;
}
.login-button {
  width: 100%;
}

@media (max-width: 768px) {
  .login-card {
    max-width: 100%;
  }
  .brand-logo {
    font-size: 40px;
  }
  .brand-title {
    font-size: 20px;
  }
}
</style>
