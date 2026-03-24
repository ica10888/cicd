<template>
  <div class="perm-page">
    <el-header class="header">
      <span class="title">应用管理系统</span>
      <div class="user-info">
        <el-tag type="danger">管理员</el-tag>
        <span style="margin-left:8px">{{ currentUser.username }}</span>
        <el-button text @click="$router.push('/apps')" style="margin-left:16px">应用列表</el-button>
        <el-button text @click="logout" style="margin-left:8px">退出</el-button>
      </div>
    </el-header>

    <el-main>
      <el-row :gutter="20">
        <!-- Left: Role list -->
        <el-col :span="7">
          <el-card>
            <template #header>
              <div style="display:flex;justify-content:space-between;align-items:center">
                <span>角色列表</span>
                <el-button size="small" type="primary" @click="openRoleCreate">+ 新建</el-button>
              </div>
            </template>
            <el-menu :default-active="String(activeRoleId)" @select="onRoleSelect">
              <el-menu-item
                v-for="r in roles" :key="r.id" :index="String(r.id)"
              >
                <div style="display:flex;justify-content:space-between;align-items:center;width:100%">
                  <span>
                    <el-tag size="small" :type="roleTagType(r.role_type)" style="margin-right:6px">
                      {{ r.role_type_display }}
                    </el-tag>
                    {{ r.name }}
                  </span>
                  <el-button size="small" type="danger" text @click.stop="handleDeleteRole(r)">删除</el-button>
                </div>
              </el-menu-item>
              <div v-if="!roles.length" style="text-align:center;color:#999;padding:20px">暂无角色</div>
            </el-menu>
          </el-card>
        </el-col>

        <!-- Right: Permission matrix -->
        <el-col :span="17">
          <el-card v-loading="permLoading">
            <template #header>
              <div style="display:flex;justify-content:space-between;align-items:center">
                <span>权限配置{{ activeRole ? ` — ${activeRole.name}` : '' }}</span>
                <el-button size="small" type="primary" :disabled="!activeRoleId" @click="openPermCreate">
                  + 添加应用权限
                </el-button>
              </div>
            </template>

            <div v-if="!activeRoleId" style="text-align:center;color:#999;padding:40px">
              请先在左侧选择一个角色
            </div>

            <el-table v-else :data="permissions" border>
              <el-table-column label="应用" min-width="140">
                <template #default="{ row }">
                  <el-tag>{{ row.app_name }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column label="查询" width="80" align="center">
                <template #default="{ row }">
                  <el-checkbox v-model="row.can_read" @change="savePermission(row)" />
                </template>
              </el-table-column>
              <el-table-column label="新增" width="80" align="center">
                <template #default="{ row }">
                  <el-checkbox v-model="row.can_create" @change="savePermission(row)" />
                </template>
              </el-table-column>
              <el-table-column label="修改" width="80" align="center">
                <template #default="{ row }">
                  <el-checkbox v-model="row.can_update" @change="savePermission(row)" />
                </template>
              </el-table-column>
              <el-table-column label="删除" width="80" align="center">
                <template #default="{ row }">
                  <el-checkbox v-model="row.can_delete" @change="savePermission(row)" />
                </template>
              </el-table-column>
              <el-table-column label="操作" width="80" align="center">
                <template #default="{ row }">
                  <el-button size="small" type="danger" text @click="handleDeletePerm(row)">移除</el-button>
                </template>
              </el-table-column>
            </el-table>
          </el-card>
        </el-col>
      </el-row>
    </el-main>

    <!-- Create Role Dialog -->
    <el-dialog v-model="roleDialogVisible" title="新建角色" width="420px">
      <el-form :model="roleForm" :rules="roleRules" ref="roleFormRef" label-width="90px">
        <el-form-item label="角色名称" prop="name">
          <el-input v-model="roleForm.name" placeholder="如：前端开发组" />
        </el-form-item>
        <el-form-item label="角色类型" prop="role_type">
          <el-select v-model="roleForm.role_type" style="width:100%">
            <el-option label="开发人员" value="developer" />
            <el-option label="测试人员" value="tester" />
            <el-option label="运维人员" value="ops" />
          </el-select>
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="roleForm.description" type="textarea" :rows="2" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="roleDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="roleSaving" @click="handleSaveRole">保存</el-button>
      </template>
    </el-dialog>

    <!-- Add Permission Dialog -->
    <el-dialog v-model="permDialogVisible" title="添加应用权限" width="460px">
      <el-form :model="permForm" :rules="permRules" ref="permFormRef" label-width="90px">
        <el-form-item label="应用" prop="app">
          <el-select v-model="permForm.app" style="width:100%" placeholder="选择应用（不选表示所有应用）" clearable>
            <el-option v-for="a in apps" :key="a.id" :label="a.name" :value="a.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="权限">
          <el-checkbox v-model="permForm.can_read">查询</el-checkbox>
          <el-checkbox v-model="permForm.can_create">新增</el-checkbox>
          <el-checkbox v-model="permForm.can_update">修改</el-checkbox>
          <el-checkbox v-model="permForm.can_delete">删除</el-checkbox>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="permDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="permSaving" @click="handleSavePerm">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getApps, getRoles, createRole, deleteRole,
         getPermissions, createPermission, updatePermission, deletePermission } from '../api/index.js'

const router = useRouter()
const currentUser = reactive(JSON.parse(localStorage.getItem('user') || '{}'))

const roles = ref([])
const apps = ref([])
const permissions = ref([])
const activeRoleId = ref(null)
const activeRole = computed(() => roles.value.find(r => r.id === activeRoleId.value))
const permLoading = ref(false)

// Role dialog
const roleDialogVisible = ref(false)
const roleSaving = ref(false)
const roleFormRef = ref()
const roleForm = reactive({ name: '', role_type: '', description: '' })
const roleRules = {
  name: [{ required: true, message: '请输入角色名称', trigger: 'blur' }],
  role_type: [{ required: true, message: '请选择角色类型', trigger: 'change' }],
}

// Permission dialog
const permDialogVisible = ref(false)
const permSaving = ref(false)
const permFormRef = ref()
const permForm = reactive({ app: null, can_read: true, can_create: false, can_update: false, can_delete: false })
const permRules = {}

async function fetchRoles() {
  const { data } = await getRoles()
  if (data.code === 200) roles.value = data.data.results
}

async function fetchApps() {
  const { data } = await getApps()
  if (data.code === 200) apps.value = data.data.results
}

async function fetchPermissions() {
  if (!activeRoleId.value) return
  permLoading.value = true
  try {
    const { data } = await getPermissions({ role_id: activeRoleId.value })
    if (data.code === 200) permissions.value = data.data.results
  } finally {
    permLoading.value = false
  }
}

function onRoleSelect(id) {
  activeRoleId.value = Number(id)
  fetchPermissions()
}

function openRoleCreate() {
  Object.assign(roleForm, { name: '', role_type: '', description: '' })
  roleDialogVisible.value = true
}

async function handleSaveRole() {
  await roleFormRef.value.validate()
  roleSaving.value = true
  try {
    const { data } = await createRole({ ...roleForm })
    if (data.code === 200) {
      ElMessage.success('创建成功')
      roleDialogVisible.value = false
      fetchRoles()
    } else {
      ElMessage.error(data.msg)
    }
  } finally {
    roleSaving.value = false
  }
}

async function handleDeleteRole(role) {
  await ElMessageBox.confirm(`确认删除角色 "${role.name}"？`, '提示', { type: 'warning' })
  const { data } = await deleteRole(role.id)
  if (data.code === 200) {
    ElMessage.success('删除成功')
    if (activeRoleId.value === role.id) { activeRoleId.value = null; permissions.value = [] }
    fetchRoles()
  }
}

function openPermCreate() {
  Object.assign(permForm, { app: null, can_read: true, can_create: false, can_update: false, can_delete: false })
  permDialogVisible.value = true
}

async function handleSavePerm() {
  permSaving.value = true
  try {
    const payload = { role: activeRoleId.value, app: permForm.app || null,
                      can_read: permForm.can_read, can_create: permForm.can_create,
                      can_update: permForm.can_update, can_delete: permForm.can_delete }
    const { data } = await createPermission(payload)
    if (data.code === 200) {
      ElMessage.success('添加成功')
      permDialogVisible.value = false
      fetchPermissions()
    } else {
      ElMessage.error(data.msg)
    }
  } finally {
    permSaving.value = false
  }
}

async function savePermission(row) {
  const { data } = await updatePermission(row.id, {
    can_read: row.can_read, can_create: row.can_create,
    can_update: row.can_update, can_delete: row.can_delete,
  })
  if (data.code === 200) ElMessage.success('已保存')
  else ElMessage.error(data.msg)
}

async function handleDeletePerm(row) {
  await ElMessageBox.confirm(`确认移除该应用的权限配置？`, '提示', { type: 'warning' })
  const { data } = await deletePermission(row.id)
  if (data.code === 200) { ElMessage.success('已移除'); fetchPermissions() }
}

function roleTagType(t) {
  return { developer: 'primary', tester: 'warning', ops: 'success' }[t] || 'info'
}

function logout() { localStorage.clear(); router.push('/login') }

onMounted(() => {
  if (!currentUser.id || currentUser.role !== 'admin') { router.push('/login'); return }
  fetchRoles()
  fetchApps()
})
</script>

<style scoped>
.perm-page { min-height: 100vh; background: #f5f7fa; }
.header {
  display: flex; align-items: center; justify-content: space-between;
  background: #fff; box-shadow: 0 1px 4px rgba(0,0,0,.1); padding: 0 24px;
}
.title { font-size: 18px; font-weight: bold; color: #303133; }
.user-info { display: flex; align-items: center; }
</style>
