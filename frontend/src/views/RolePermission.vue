<template>
  <div class="role-permission">
    <div class="page-header">
      <h2>角色权限管理</h2>
      <p class="page-desc">管理系统角色、权限分配与用户授权</p>
    </div>

    <el-card>
      <template #header>
        <div class="card-header">
          <span class="card-title">角色列表</span>
          <el-button type="primary" :icon="icons.Plus" @click="handleAdd">
            新增角色
          </el-button>
        </div>
      </template>

      <el-table v-loading="loading" :data="roles" stripe border style="width: 100%">
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column prop="name" label="角色名称" width="150" />
        <el-table-column prop="code" label="角色代码" width="140" />
        <el-table-column prop="description" label="角色描述" min-width="200" show-overflow-tooltip />
        <el-table-column label="状态" width="90" align="center">
          <template #default="scope">
            <el-tag :type="scope.row.status === '启用' ? 'success' : 'info'" size="small">
              {{ scope.row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="user_count" label="关联用户" width="90" align="center" />
        <el-table-column prop="permission_count" label="权限数" width="80" align="center" />
        <el-table-column label="操作" width="240" class-name="action-cell" fixed="right">
          <template #default="scope">
            <div class="action-btns">
              <el-button size="small" @click="handlePermissions(scope.row)">
                <el-icon><component :is="icons.Key" /></el-icon>
                权限
              </el-button>
              <el-button size="small" @click="handleEdit(scope.row)">
                <el-icon><component :is="icons.Edit" /></el-icon>
                编辑
              </el-button>
              <el-button size="small" type="danger" @click="handleDelete(scope.row)">
                <el-icon><component :is="icons.Delete" /></el-icon>
                删除
              </el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-wrapper">
        <el-pagination
          class="pagination"
          layout="total, sizes, prev, pager, next, jumper"
          :total="pagination.total"
          v-model:page-size="pagination.pageSize"
          v-model:current-page="pagination.currentPage"
          :page-sizes="[10, 20, 50]"
          @size-change="handleSizeChange"
          @current-change="loadRoles"
        />
      </div>
    </el-card>

    <el-dialog v-model="roleDialogVisible" :title="isEdit ? '编辑角色' : '新增角色'" width="520px" :close-on-click-modal="false">
      <el-form ref="roleFormRef" :model="roleForm" :rules="roleRules" label-width="100px">
        <el-form-item label="角色名称" prop="name">
          <el-input v-model="roleForm.name" placeholder="请输入角色名称" maxlength="50" show-word-limit />
        </el-form-item>
        <el-form-item label="角色代码" prop="code">
          <el-input v-model="roleForm.code" placeholder="请输入英文代码，如 admin" :disabled="isEdit" />
        </el-form-item>
        <el-form-item label="角色描述" prop="description">
          <el-input v-model="roleForm.description" type="textarea" :rows="3" placeholder="请输入角色描述" maxlength="200" show-word-limit />
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-radio-group v-model="roleForm.status">
            <el-radio value="启用">启用</el-radio>
            <el-radio value="禁用">禁用</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="roleDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="roleSubmitting" @click="handleSubmitRole">确定</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="permDialogVisible" :title="`权限配置 - ${currentRole?.name || ''}`" width="600px" :close-on-click-modal="false">
      <div v-loading="permLoading" class="perm-container">
        <div class="perm-toolbar">
          <el-input
            v-model="permFilter"
            placeholder="搜索权限"
            :prefix-icon="icons.Search"
            clearable
            style="width: 220px"
          />
          <div class="perm-actions">
            <el-checkbox v-model="expandAll" @change="toggleExpandAll">全部展开</el-checkbox>
            <el-button link type="primary" @click="checkAllPermissions">全选</el-button>
            <el-button link type="info" @click="clearAllPermissions">清空</el-button>
          </div>
        </div>
        <el-tree
          ref="permTreeRef"
          :data="permissionTree"
          :props="{ label: 'name', children: 'children' }"
          show-checkbox
          node-key="id"
          :default-checked-keys="checkedPermissionKeys"
          :filter-node-method="filterNode"
          :expand-on-click-node="false"
          default-expand-all
          class="perm-tree"
        >
          <template #default="{ node, data }">
            <span class="tree-node">
              <el-icon :size="14" v-if="data.children && data.children.length">
                <component :is="icons.Folder" />
              </el-icon>
              <el-icon :size="14" v-else>
                <component :is="icons.Document" />
              </el-icon>
              <span class="tree-label">{{ node.label }}</span>
            </span>
          </template>
        </el-tree>
      </div>
      <template #footer>
        <el-button @click="permDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="permSubmitting" @click="handleSavePermissions">
          保存权限
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, nextTick, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import * as icons from '@element-plus/icons-vue'

const loading = ref(false)
const roles = ref([])
const roleFormRef = ref(null)
const roleDialogVisible = ref(false)
const isEdit = ref(false)
const roleSubmitting = ref(false)
const editingRoleId = ref(null)

const roleForm = reactive({
  name: '',
  code: '',
  description: '',
  status: '启用'
})

const roleRules = {
  name: [{ required: true, message: '请输入角色名称', trigger: 'blur' }],
  code: [
    { required: true, message: '请输入角色代码', trigger: 'blur' },
    { pattern: /^[a-zA-Z_][a-zA-Z0-9_]*$/, message: '只能包含英文字母、数字和下划线，且以字母或下划线开头', trigger: 'blur' }
  ],
  description: [{ max: 200, message: '描述不能超过 200 个字符', trigger: 'blur' }]
}

const pagination = reactive({
  currentPage: 1,
  pageSize: 10,
  total: 0
})

const permDialogVisible = ref(false)
const permLoading = ref(false)
const permSubmitting = ref(false)
const permTreeRef = ref(null)
const permFilter = ref('')
const expandAll = ref(true)
const currentRole = ref(null)
const permissionTree = ref([])
const checkedPermissionKeys = ref([])

watch(permFilter, (val) => {
  permTreeRef.value?.filter(val)
})

const filterNode = (value, data) => {
  if (!value) return true
  return data.name.includes(value)
}

const loadRoles = async () => {
  loading.value = true
  try {
    const res = await fetch(`/api/v1/roles?page=${pagination.currentPage}&page_size=${pagination.pageSize}`)
    const json = await res.json()
    roles.value = json.roles || json.data?.roles || []
    pagination.total = json.total ?? json.data?.total ?? 0
  } catch (e) {
    console.error('加载角色列表失败:', e)
    ElMessage.error('加载角色列表失败')
  } finally {
    loading.value = false
  }
}

const handleSizeChange = () => {
  pagination.currentPage = 1
  loadRoles()
}

const loadPermissionTree = async () => {
  permLoading.value = true
  try {
    const res = await fetch('/api/v1/permissions/tree')
    const json = await res.json()
    permissionTree.value = json.tree || json.data?.tree || json.permissions || json.data?.permissions || []
  } catch (e) {
    console.error('加载权限树失败:', e)
    ElMessage.error('加载权限树失败')
  } finally {
    permLoading.value = false
  }
}

const handleAdd = () => {
  isEdit.value = false
  editingRoleId.value = null
  Object.assign(roleForm, { name: '', code: '', description: '', status: '启用' })
  roleDialogVisible.value = true
  nextTick(() => roleFormRef.value?.clearValidate())
}

const handleEdit = (row) => {
  isEdit.value = true
  editingRoleId.value = row.id
  Object.assign(roleForm, {
    name: row.name,
    code: row.code,
    description: row.description || '',
    status: row.status
  })
  roleDialogVisible.value = true
  nextTick(() => roleFormRef.value?.clearValidate())
}

const handleSubmitRole = async () => {
  if (!roleFormRef.value) return
  await roleFormRef.value.validate(async (valid) => {
    if (!valid) return
    roleSubmitting.value = true
    try {
      const url = isEdit.value
        ? `/api/v1/roles/${editingRoleId.value}`
        : '/api/v1/roles'
      const method = isEdit.value ? 'PUT' : 'POST'
      const res = await fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(roleForm)
      })
      const json = await res.json()
      const data = json.data || json
      if (json.success) {
        ElMessage.success(isEdit.value ? '更新角色成功' : '创建角色成功')
        roleDialogVisible.value = false
        await loadRoles()
      } else {
        ElMessage.error(json.detail || json.message || '操作失败')
      }
    } catch (e) {
      console.error('保存角色失败:', e)
      ElMessage.error('保存角色失败')
    } finally {
      roleSubmitting.value = false
    }
  })
}

const handleDelete = (row) => {
  if (row.user_count > 0) {
    ElMessageBox.confirm(
      `该角色下还有 ${row.user_count} 个关联用户，删除后这些用户将失去该角色权限。确定要删除吗？`,
      '删除确认',
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'warning'
      }
    ).then(() => doDelete(row)).catch(() => {})
  } else {
    ElMessageBox.confirm(
      `确定要删除角色「${row.name}」吗？此操作不可恢复。`,
      '删除确认',
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'warning'
      }
    ).then(() => doDelete(row)).catch(() => {})
  }
}

const doDelete = async (row) => {
  try {
    const res = await fetch(`/api/v1/roles/${row.id}`, { method: 'DELETE' })
    const json = await res.json()
    const data = json.data || json
    if (json.success) {
      ElMessage.success('删除成功')
      await loadRoles()
    } else {
      ElMessage.error(json.detail || json.message || '删除失败')
    }
  } catch (e) {
    console.error('删除角色失败:', e)
    ElMessage.error('删除失败')
  }
}

const handlePermissions = async (row) => {
  currentRole.value = row
  permDialogVisible.value = true
  permFilter.value = ''

  if (permissionTree.value.length === 0) {
    await loadPermissionTree()
  }

  try {
    const res = await fetch(`/api/v1/roles/${row.id}/permissions`)
    const json = await res.json()
    const data = json.data || json
    checkedPermissionKeys.value = data.permission_ids || json.permission_ids || data.permissions || json.permissions || []
  } catch (e) {
    console.error('加载角色权限失败:', e)
    checkedPermissionKeys.value = []
  }

  nextTick(() => {
    if (permTreeRef.value) {
      permTreeRef.value.setCheckedKeys(checkedPermissionKeys.value)
    }
  })
}

const toggleExpandAll = (val) => {
  const nodes = permTreeRef.value?.store?.nodesMap
  if (!nodes) return
  Object.values(nodes).forEach(node => {
    node.expanded = val
  })
}

const checkAllPermissions = () => {
  const allKeys = []
  const collect = (nodes) => {
    nodes.forEach(n => {
      if (!n.children || n.children.length === 0) {
        allKeys.push(n.id)
      } else {
        collect(n.children)
      }
    })
  }
  collect(permissionTree.value)
  permTreeRef.value?.setCheckedKeys(allKeys)
}

const clearAllPermissions = () => {
  permTreeRef.value?.setCheckedKeys([])
}

const handleSavePermissions = async () => {
  permSubmitting.value = true
  try {
    const checkedKeys = permTreeRef.value?.getCheckedKeys(true) || []
    const res = await fetch(`/api/v1/roles/${currentRole.value.id}/permissions`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ permission_ids: checkedKeys })
    })
    const json = await res.json()
    const data = json.data || json
    if (json.success) {
      ElMessage.success('权限保存成功')
      permDialogVisible.value = false
      await loadRoles()
    } else {
      ElMessage.error(json.detail || json.message || '保存失败')
    }
  } catch (e) {
    console.error('保存权限失败:', e)
    ElMessage.error('保存权限失败')
  } finally {
    permSubmitting.value = false
  }
}

onMounted(() => {
  loadRoles()
})
</script>

<style scoped>
.role-permission {
  padding: 20px;
}

.page-header {
  margin-bottom: 24px;
}

.page-header h2 {
  font-size: 24px;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 4px;
}

.page-desc {
  font-size: 14px;
  color: #6b7280;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.card-title {
  font-size: 16px;
  font-weight: 600;
}

.pagination-wrapper {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}

.pagination {
  justify-content: flex-end;
}

.perm-container {
  min-height: 300px;
}

.perm-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
  padding-bottom: 12px;
  border-bottom: 1px solid #ebeef5;
}

.perm-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.perm-tree {
  max-height: 420px;
  overflow-y: auto;
  padding: 8px 12px;
  border: 1px solid #ebeef5;
  border-radius: 6px;
}

.tree-node {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
}

.tree-label {
  font-weight: 500;
}
</style>