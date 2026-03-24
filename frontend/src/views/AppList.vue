<template>
  <div class="app-list-page">
    <!-- Header -->
    <el-header class="header">
      <span class="title">应用管理系统</span>
      <div class="user-info">
        <el-tag :type="isAdmin ? 'danger' : 'primary'">{{ isAdmin ? '管理员' : '普通用户' }}</el-tag>
        <span style="margin-left:8px">{{ currentUser.username }}</span>
        <el-button text @click="logout" style="margin-left:16px">退出</el-button>
        <el-button v-if="isAdmin" text @click="$router.push('/permissions')" style="margin-left:8px">权限管理</el-button>
      </div>
    </el-header>

    <el-main>
      <!-- Toolbar -->
      <div class="toolbar">
        <span class="section-title">应用列表</span>
        <el-button v-if="isAdmin" type="primary" @click="openCreate">+ 新建应用</el-button>
      </div>

      <!-- App Table -->
      <el-table :data="apps" v-loading="loading" border stripe>
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="name" label="应用名称" />
        <el-table-column prop="version" label="版本" width="100" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="statusType(row.status)">{{ statusLabel(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="描述" show-overflow-tooltip />
        <el-table-column prop="repo_url" label="仓库地址" show-overflow-tooltip />
        <el-table-column prop="create_time" label="创建时间" width="180">
          <template #default="{ row }">{{ formatDate(row.create_time) }}</template>
        </el-table-column>
        <el-table-column v-if="isAdmin" label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="openEdit(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-main>

    <!-- Create/Edit Dialog -->
    <el-dialog v-model="dialogVisible" :title="editId ? '编辑应用' : '新建应用'" width="500px">
      <el-form :model="appForm" :rules="appRules" ref="appFormRef" label-width="90px">
        <el-form-item label="应用名称" prop="name">
          <el-input v-model="appForm.name" />
        </el-form-item>
        <el-form-item label="版本号" prop="version">
          <el-input v-model="appForm.version" />
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-select v-model="appForm.status" style="width:100%">
            <el-option label="运行中" value="running" />
            <el-option label="已停止" value="stopped" />
            <el-option label="部署中" value="deploying" />
            <el-option label="异常" value="error" />
          </el-select>
        </el-form-item>
        <el-form-item label="仓库地址">
          <el-input v-model="appForm.repo_url" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="appForm.description" type="textarea" :rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="handleSave">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getApps, createApp, updateApp, deleteApp } from '../api/index.js'

const router = useRouter()
const currentUser = reactive(JSON.parse(localStorage.getItem('user') || '{}'))
const isAdmin = computed(() => currentUser.role === 'admin')

const apps = ref([])
const loading = ref(false)
const dialogVisible = ref(false)
const saving = ref(false)
const editId = ref(null)
const appFormRef = ref()

const appForm = reactive({ name: '', version: '1.0.0', status: 'stopped', repo_url: '', description: '' })
const appRules = {
  name: [{ required: true, message: '请输入应用名称', trigger: 'blur' }],
  version: [{ required: true, message: '请输入版本号', trigger: 'blur' }],
  status: [{ required: true, message: '请选择状态', trigger: 'change' }],
}

async function fetchApps() {
  loading.value = true
  try {
    const { data } = await getApps()
    if (data.code === 200) apps.value = data.data.results
  } finally {
    loading.value = false
  }
}

function openCreate() {
  editId.value = null
  Object.assign(appForm, { name: '', version: '1.0.0', status: 'stopped', repo_url: '', description: '' })
  dialogVisible.value = true
}

function openEdit(row) {
  editId.value = row.id
  Object.assign(appForm, { name: row.name, version: row.version, status: row.status, repo_url: row.repo_url, description: row.description })
  dialogVisible.value = true
}

async function handleSave() {
  await appFormRef.value.validate()
  saving.value = true
  try {
    const fn = editId.value ? updateApp(editId.value, appForm) : createApp(appForm)
    const { data } = await fn
    if (data.code === 200) {
      ElMessage.success(data.msg)
      dialogVisible.value = false
      fetchApps()
    } else {
      ElMessage.error(data.msg)
    }
  } finally {
    saving.value = false
  }
}

async function handleDelete(row) {
  await ElMessageBox.confirm(`确认删除应用 "${row.name}"？`, '提示', { type: 'warning' })
  const { data } = await deleteApp(row.id)
  if (data.code === 200) {
    ElMessage.success('删除成功')
    fetchApps()
  }
}

function logout() {
  localStorage.clear()
  router.push('/login')
}

function statusType(s) {
  return { running: 'success', stopped: 'info', deploying: 'warning', error: 'danger' }[s] || 'info'
}
function statusLabel(s) {
  return { running: '运行中', stopped: '已停止', deploying: '部署中', error: '异常' }[s] || s
}
function formatDate(d) {
  return d ? new Date(d).toLocaleString('zh-CN') : '-'
}

onMounted(() => {
  if (!currentUser.id) { router.push('/login'); return }
  fetchApps()
})
</script>

<style scoped>
.app-list-page { min-height: 100vh; background: #f5f7fa; }
.header {
  display: flex; align-items: center; justify-content: space-between;
  background: #fff; box-shadow: 0 1px 4px rgba(0,0,0,.1); padding: 0 24px;
}
.title { font-size: 18px; font-weight: bold; color: #303133; }
.user-info { display: flex; align-items: center; }
.toolbar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.section-title { font-size: 16px; font-weight: 600; }
</style>
