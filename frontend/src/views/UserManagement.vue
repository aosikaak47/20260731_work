<template>
  <div class="user-management">
    <div class="page-header">
      <div class="header-left">
        <div class="header-icon">
          <el-icon :size="22"><component :is="icons.User" /></el-icon>
        </div>
        <div class="header-text">
          <h2>用户管理</h2>
          <p class="page-desc">管理平台用户账号</p>
        </div>
      </div>
    </div>
    
    <el-card>
      <template #header>
        <div class="card-header">
          <span class="card-title">用户列表</span>
          <el-button type="primary" @click="handleAdd">
            <el-icon><component :is="icons.Plus" /></el-icon>
            新增用户
          </el-button>
        </div>
      </template>
      
      <div class="filter-bar">
        <el-select v-model="filterRole" placeholder="角色" clearable class="filter-select">
          <el-option label="全部" value="" />
          <el-option v-for="role in roles" :key="role.id" :label="role.name" :value="String(role.id)" />
        </el-select>
        <el-select v-model="filterStatus" placeholder="状态" clearable class="filter-select">
          <el-option label="全部" value="" />
          <el-option label="正常" value="正常" />
          <el-option label="禁用" value="禁用" />
        </el-select>
        <el-input 
          v-model="searchKeyword" 
          placeholder="搜索用户名、邮箱..." 
          class="search-input"
          clearable
        >
          <template #prefix>
            <el-icon><component :is="icons.Search" /></el-icon>
          </template>
        </el-input>
      </div>
      
      <el-table :data="pagedUsers" stripe border :row-style="{ height: '44px' }" v-loading="loading">
        <el-table-column type="selection" width="50" />
        <el-table-column prop="id" label="ID" width="60" align="center" />
        <el-table-column prop="username" label="用户名" width="120" sortable />
        <el-table-column prop="real_name" label="真实姓名" width="120" />
        <el-table-column prop="email" label="邮箱" width="200" sortable :show-overflow-tooltip="true" />
        <el-table-column label="角色" width="120">
          <template #default="scope">
            <el-tag size="small" effect="plain">{{ getRoleName(scope.row.role_id) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="90" align="center">
          <template #default="scope">
            <el-tag size="small" :type="scope.row.status === '正常' ? 'success' : 'info'" effect="plain">{{ scope.row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="last_login" label="最后登录" width="160" sortable />
        <el-table-column label="操作" width="220" class-name="action-cell" fixed="right">
          <template #default="scope">
            <div class="action-btns">
              <el-button size="small" text @click="handleEdit(scope.row)">编辑</el-button>
              <el-button size="small" text @click="handleResetPwd(scope.row)">重置密码</el-button>
              <el-button size="small" text type="success" v-if="scope.row.status === '禁用'" @click="handleToggle(scope.row)">启用</el-button>
              <el-button size="small" text type="warning" v-else @click="handleToggle(scope.row)">禁用</el-button>
              <el-button size="small" text type="danger" @click="handleDelete(scope.row)">删除</el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>
      
      <div class="pagination">
        <el-pagination
          layout="total, sizes, prev, pager, next, jumper"
          :total="filteredUsers.length"
          :page-size="pageSize"
          :current-page="currentPage"
          :page-sizes="[10, 20, 50, 100]"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <el-dialog v-model="dialogVisible" :title="editingUser ? '编辑用户' : '新增用户'" width="550px" :close-on-click-modal="false">
      <el-form :model="userForm" :rules="formRules" ref="userFormRef" label-width="100px">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="userForm.username" placeholder="请输入用户名" :disabled="!!editingUser" />
        </el-form-item>
        <el-form-item label="真实姓名" prop="real_name">
          <el-input v-model="userForm.real_name" placeholder="请输入真实姓名" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="userForm.email" placeholder="请输入邮箱" />
        </el-form-item>
        <el-form-item v-if="!editingUser" label="密码" prop="password">
          <el-input v-model="userForm.password" type="password" placeholder="请输入密码（至少6位）" show-password />
        </el-form-item>
        <el-form-item label="角色" prop="role_id">
          <el-select v-model="userForm.role_id" placeholder="请选择角色">
            <el-option v-for="role in roles" :key="role.id" :label="role.name" :value="role.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-select v-model="userForm.status">
            <el-option label="正常" value="正常" />
            <el-option label="禁用" value="禁用" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSave">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="resetPwdVisible" title="重置密码" width="450px" :close-on-click-modal="false">
      <el-form :model="resetPwdForm" :rules="resetPwdRules" ref="resetPwdFormRef" label-width="100px">
        <el-form-item label="用户名">
          <el-input :model-value="resetPwdForm.username" disabled />
        </el-form-item>
        <el-form-item label="新密码" prop="new_password">
          <el-input v-model="resetPwdForm.new_password" type="password" placeholder="请输入新密码（至少6位）" show-password />
        </el-form-item>
        <el-form-item label="确认密码" prop="confirm_password">
          <el-input v-model="resetPwdForm.confirm_password" type="password" placeholder="请再次输入新密码" show-password />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="resetPwdVisible = false">取消</el-button>
        <el-button type="primary" @click="handleResetPwdSave">确认重置</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, reactive } from 'vue'
import * as icons from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useProjects } from '../composables/useProjects'

const { loading: projectsLoading } = useProjects()

const loading = ref(false)
const users = ref([])
const roles = ref([])
const searchKeyword = ref('')
const filterRole = ref('')
const filterStatus = ref('')

const dialogVisible = ref(false)
const editingUser = ref(null)
const userFormRef = ref(null)

const userForm = reactive({
  username: '',
  real_name: '',
  email: '',
  password: '',
  role_id: null,
  status: '正常'
})

const formRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  real_name: [{ required: true, message: '请输入真实姓名', trigger: 'blur' }],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入有效的邮箱地址', trigger: ['blur', 'change'] }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少6位', trigger: 'blur' }
  ],
  role_id: [{ required: true, message: '请选择角色', trigger: 'change' }]
}

const resetPwdVisible = ref(false)
const resetPwdFormRef = ref(null)
const resetPwdForm = reactive({
  user_id: null,
  username: '',
  new_password: '',
  confirm_password: ''
})

const resetPwdRules = {
  new_password: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少6位', trigger: 'blur' }
  ],
  confirm_password: [
    { required: true, message: '请再次输入新密码', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value !== resetPwdForm.new_password) {
          callback(new Error('两次输入的密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
}

const currentPage = ref(1)
const pageSize = ref(10)

const loadUsers = async () => {
  loading.value = true
  try {
    const response = await fetch('/api/v1/users')
    const json = await response.json()
    users.value = json.users || json.data?.users || []
  } catch (error) {
    console.error('加载用户列表失败:', error)
    ElMessage.error('加载用户列表失败')
    users.value = []
  } finally {
    loading.value = false
  }
}

const loadRoles = async () => {
  try {
    const response = await fetch('/api/v1/roles')
    const json = await response.json()
    roles.value = json.roles || json.data?.roles || []
  } catch (error) {
    console.error('加载角色列表失败:', error)
    roles.value = []
  }
}

const getRoleName = (roleId) => {
  if (!roleId) return '-'
  const role = roles.value.find(r => String(r.id) === String(roleId))
  return role ? role.name : `角色${roleId}`
}

const filteredUsers = computed(() => {
  let result = users.value
  if (filterRole.value) {
    result = result.filter(u => String(u.role_id) === filterRole.value)
  }
  if (filterStatus.value) {
    result = result.filter(u => u.status === filterStatus.value)
  }
  if (searchKeyword.value) {
    const kw = searchKeyword.value.toLowerCase()
    result = result.filter(u =>
      (u.username && u.username.toLowerCase().includes(kw)) ||
      (u.real_name && u.real_name.toLowerCase().includes(kw)) ||
      (u.email && u.email.toLowerCase().includes(kw))
    )
  }
  return result
})

const pagedUsers = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredUsers.value.slice(start, end)
})

const handleSizeChange = (size) => {
  pageSize.value = size
  currentPage.value = 1
}

const handleCurrentChange = (page) => {
  currentPage.value = page
}

const resetUserForm = () => {
  userForm.username = ''
  userForm.real_name = ''
  userForm.email = ''
  userForm.password = ''
  userForm.role_id = null
  userForm.status = '正常'
}

const handleAdd = () => {
  editingUser.value = null
  resetUserForm()
  dialogVisible.value = true
}

const handleEdit = (row) => {
  editingUser.value = row
  userForm.username = row.username || row.name || ''
  userForm.real_name = row.real_name || row.realName || ''
  userForm.email = row.email || ''
  userForm.password = ''
  userForm.role_id = row.role_id
  userForm.status = row.status
  dialogVisible.value = true
}

const handleSave = async () => {
  if (!userFormRef.value) return
  try {
    await userFormRef.value.validate()
  } catch {
    return
  }

  const payload = {
    username: userForm.username,
    real_name: userForm.real_name,
    email: userForm.email,
    role_id: userForm.role_id,
    status: userForm.status
  }

  if (!editingUser.value) {
    payload.password = userForm.password
  }

  try {
    if (editingUser.value) {
      const response = await fetch(`/api/v1/users/${editingUser.value.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      })
      const json = await response.json()
      const data = json.data || json
      if (json.success !== false) {
        ElMessage.success('用户更新成功')
        dialogVisible.value = false
        await loadUsers()
      } else {
        ElMessage.error(json.detail || json.message || '更新失败')
      }
    } else {
      const response = await fetch('/api/v1/users', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      })
      const json = await response.json()
      const data = json.data || json
      if (json.success !== false) {
        ElMessage.success('用户创建成功')
        dialogVisible.value = false
        await loadUsers()
      } else {
        ElMessage.error(json.detail || json.message || '创建失败')
      }
    }
  } catch (error) {
    console.error('保存用户失败:', error)
    ElMessage.error('保存失败，请检查网络连接')
  }
}

const handleToggle = async (row) => {
  const newStatus = row.status === '正常' ? '禁用' : '正常'
  const action = newStatus === '正常' ? '启用' : '禁用'
  try {
    await ElMessageBox.confirm(`确定要${action}用户 "${row.username}" 吗？`, `确认${action}`, {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    try {
      const response = await fetch(`/api/v1/users/${row.id}/toggle-status`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status: newStatus })
      })
      const json = await response.json()
      const data = json.data || json
      if (json.success !== false) {
        ElMessage.success(`用户已${action}`)
        await loadUsers()
      } else {
        ElMessage.error(json.detail || json.message || `${action}失败`)
      }
    } catch (error) {
      console.error(`${action}用户失败:`, error)
      ElMessage.error(`${action}失败，请检查网络连接`)
    }
  } catch {
    // User cancelled
  }
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(`确定要删除用户 "${row.username}" 吗？此操作不可恢复！`, '确认删除', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    try {
      const response = await fetch(`/api/v1/users/${row.id}`, {
        method: 'DELETE'
      })
      const json = await response.json()
      const data = json.data || json
      if (json.success !== false) {
        ElMessage.success('用户删除成功')
        if (pagedUsers.value.length === 1 && currentPage.value > 1) {
          currentPage.value--
        }
        await loadUsers()
      } else {
        ElMessage.error(json.detail || json.message || '删除失败')
      }
    } catch (error) {
      console.error('删除用户失败:', error)
      ElMessage.error('删除失败，请检查网络连接')
    }
  } catch {
    // User cancelled
  }
}

const handleResetPwd = (row) => {
  resetPwdForm.user_id = row.id
  resetPwdForm.username = row.username
  resetPwdForm.new_password = ''
  resetPwdForm.confirm_password = ''
  resetPwdVisible.value = true
}

const handleResetPwdSave = async () => {
  if (!resetPwdFormRef.value) return
  try {
    await resetPwdFormRef.value.validate()
  } catch {
    return
  }

  try {
    const response = await fetch(`/api/v1/users/${resetPwdForm.user_id}/reset-password`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        new_password: resetPwdForm.new_password
      })
    })
    const json = await response.json()
    const data = json.data || json
    if (json.success !== false) {
      ElMessage.success('密码重置成功')
      resetPwdVisible.value = false
    } else {
      ElMessage.error(json.detail || json.message || '密码重置失败')
    }
  } catch (error) {
    console.error('密码重置失败:', error)
    ElMessage.error('密码重置失败，请检查网络连接')
  }
}

onMounted(async () => {
  await Promise.all([loadUsers(), loadRoles()])
})
</script>

<style scoped>
.user-management {
}

.page-header {
  margin-bottom: 24px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.header-icon {
  width: 48px;
  height: 48px;
  background: linear-gradient(135deg, var(--theme-primary) 0%, var(--theme-primary-dark) 100%);
  border-radius: var(--radius-lg);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  flex-shrink: 0;
}

.header-text h2 {
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  margin: 0 0 4px 0;
  line-height: 1.4;
}

.page-desc {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  margin: 0;
  line-height: 1.5;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.card-title {
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-semibold);
}

.filter-bar {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
  align-items: center;
}

.filter-select {
  width: 140px;
}

.search-input {
  width: 260px;
}

.pagination {
  display: flex;
  justify-content: flex-end;
  margin-top: var(--spacing-4);
}

.action-btns {
  display: flex;
  gap: 4px;
  flex-wrap: nowrap;
}
</style>