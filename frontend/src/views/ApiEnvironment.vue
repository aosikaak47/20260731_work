<template>
  <div class="api-environment">
    <div class="page-header">
      <h2>接口环境管理</h2>
      <p class="page-desc">管理接口测试环境，支持多环境切换和变量配置</p>
    </div>
    
    <el-card>
      <template #header>
        <div class="card-header">
          <span class="card-title">环境列表</span>
          <div class="header-actions">
            <el-input v-model="searchKeyword" placeholder="搜索环境名称或URL" class="search-input" @keyup.enter="loadEnvironments">
              <template #prefix>
                <el-icon><component :is="icons.Search" /></el-icon>
              </template>
            </el-input>
            <el-button type="primary" @click="handleAdd">
              <el-icon><component :is="icons.Plus" /></el-icon>
              新增环境
            </el-button>
          </div>
        </div>
      </template>
      
      <el-table :data="filteredEnvironments" stripe border>
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="name" label="环境名称" width="120" />
        <el-table-column prop="base_url" label="基础URL" min-width="200" show-overflow-tooltip />
        <el-table-column prop="status" label="状态" width="80">
          <template #default="scope">
            <el-tag :type="scope.row.status === '启用' ? 'success' : 'info'">{{ scope.row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="timeout" label="超时时间(秒)" width="100" />
        <el-table-column prop="retry" label="重试次数" width="100" />
        <el-table-column prop="created_at" label="创建时间" width="150" />
        <el-table-column label="操作" width="280" class-name="action-cell">
          <template #default="scope">
            <div class="action-btns">
              <el-button size="small" @click="handleEdit(scope.row)">编辑</el-button>
              <el-button size="small" @click="handleClone(scope.row)">复制</el-button>
              <el-button size="small" type="success" v-if="scope.row.status === '禁用'" @click="handleToggle(scope.row)">启用</el-button>
              <el-button size="small" type="warning" v-else @click="handleToggle(scope.row)">禁用</el-button>
              <el-button size="small" type="danger" @click="handleDelete(scope.row)">删除</el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>
      
      <el-pagination
        class="pagination"
        layout="total, prev, pager, next"
        :total="filteredEnvironments.length"
        :page-size="10"
        v-model:current-page="currentPage"
      />
    </el-card>

    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑环境' : '新增环境'" width="600px">
      <el-form :model="envForm" label-width="100px">
        <el-form-item label="环境名称" required>
          <el-input v-model="envForm.name" placeholder="请输入环境名称" />
        </el-form-item>
        <el-form-item label="基础URL" required>
          <el-input v-model="envForm.base_url" placeholder="请输入基础URL" />
        </el-form-item>
        <el-form-item label="状态">
          <el-radio-group v-model="envForm.status">
            <el-radio label="启用" />
            <el-radio label="禁用" />
          </el-radio-group>
        </el-form-item>
        <el-form-item label="超时时间">
          <el-input-number v-model="envForm.timeout" :min="1" :max="300" placeholder="秒" />
        </el-form-item>
        <el-form-item label="重试次数">
          <el-input-number v-model="envForm.retry" :min="0" :max="10" placeholder="次" />
        </el-form-item>
        
        <el-form-item label="环境变量">
          <div class="variables-container">
            <div v-for="(varItem, index) in envForm.variables" :key="index" class="variable-row">
              <el-input v-model="varItem.key" placeholder="变量名" class="var-input" />
              <el-input v-model="varItem.value" placeholder="变量值" class="var-input" />
              <el-input v-model="varItem.description" placeholder="描述" class="var-input" />
              <el-button type="danger" size="small" @click="removeVariable(index)">
                <el-icon><component :is="icons.Delete" /></el-icon>
              </el-button>
            </div>
            <el-button type="primary" size="small" @click="addVariable">
              <el-icon><component :is="icons.Plus" /></el-icon>
              添加变量
            </el-button>
          </div>
        </el-form-item>
        
        <el-form-item label="请求头">
          <div class="headers-container">
            <div v-for="(header, index) in envForm.headers" :key="index" class="header-row">
              <el-input v-model="header.key" placeholder="Header名" class="header-input" />
              <el-input v-model="header.value" placeholder="Header值" class="header-input" />
              <el-button type="danger" size="small" @click="removeHeader(index)">
                <el-icon><component :is="icons.Delete" /></el-icon>
              </el-button>
            </div>
            <el-button type="primary" size="small" @click="addHeader">
              <el-icon><component :is="icons.Plus" /></el-icon>
              添加请求头
            </el-button>
          </div>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSave">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import * as icons from '@element-plus/icons-vue'

const environments = ref([])
const searchKeyword = ref('')
const currentPage = ref(1)
const dialogVisible = ref(false)
const isEdit = ref(false)
const editingEnv = ref(null)

const envForm = ref({
  name: '',
  base_url: '',
  status: '启用',
  timeout: 30,
  retry: 3,
  variables: [],
  headers: []
})

const filteredEnvironments = computed(() => {
  if (!searchKeyword.value) return environments.value
  const keyword = searchKeyword.value.toLowerCase()
  return environments.value.filter(env => 
    env.name.toLowerCase().includes(keyword) || 
    env.base_url.toLowerCase().includes(keyword)
  )
})

const loadEnvironments = async () => {
  try {
    const response = await fetch('/api/v1/environments')
    const data = await response.json()
    environments.value = data.environments || []
  } catch (error) {
    console.error('加载环境列表失败:', error)
  }
}

const resetForm = () => {
  envForm.value = {
    name: '',
    base_url: '',
    status: '启用',
    timeout: 30,
    retry: 3,
    variables: [],
    headers: []
  }
}

const handleAdd = () => {
  isEdit.value = false
  editingEnv.value = null
  resetForm()
  dialogVisible.value = true
}

const handleEdit = (row) => {
  isEdit.value = true
  editingEnv.value = row
  envForm.value = {
    name: row.name,
    base_url: row.base_url,
    status: row.status,
    timeout: row.timeout,
    retry: row.retry,
    variables: row.variables ? JSON.parse(JSON.stringify(row.variables)) : [],
    headers: row.headers ? JSON.parse(JSON.stringify(row.headers)) : []
  }
  dialogVisible.value = true
}

const handleClone = async (row) => {
  try {
    const response = await fetch(`/api/v1/environments/${row.id}/clone`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' }
    })
    const data = await response.json()
    if (data.success) {
      alert(data.message)
      loadEnvironments()
    }
  } catch (error) {
    console.error('复制环境失败:', error)
  }
}

const handleToggle = async (row) => {
  try {
    const response = await fetch(`/api/v1/environments/${row.id}/toggle`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' }
    })
    const data = await response.json()
    if (data.success) {
      row.status = data.environment.status
      alert(data.message)
    }
  } catch (error) {
    console.error('切换状态失败:', error)
  }
}

const handleDelete = async (row) => {
  if (!confirm(`确定要删除环境「${row.name}」吗？`)) return
  try {
    const response = await fetch(`/api/v1/environments/${row.id}`, {
      method: 'DELETE'
    })
    const data = await response.json()
    if (data.success) {
      alert(data.message)
      loadEnvironments()
    }
  } catch (error) {
    console.error('删除环境失败:', error)
  }
}

const handleSave = async () => {
  if (!envForm.value.name || !envForm.value.base_url) {
    alert('环境名称和基础URL不能为空')
    return
  }
  
  try {
    const url = isEdit.value ? `/api/v1/environments/${editingEnv.value.id}` : '/api/v1/environments'
    const method = isEdit.value ? 'PUT' : 'POST'
    
    const response = await fetch(url, {
      method: method,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(envForm.value)
    })
    
    const data = await response.json()
    if (data.success) {
      alert(data.message)
      dialogVisible.value = false
      loadEnvironments()
    } else {
      alert(data.message || '保存失败')
    }
  } catch (error) {
    console.error('保存环境失败:', error)
    alert('保存环境失败，请检查网络连接')
  }
}

const addVariable = () => {
  envForm.value.variables.push({ key: '', value: '', description: '' })
}

const removeVariable = (index) => {
  envForm.value.variables.splice(index, 1)
}

const addHeader = () => {
  envForm.value.headers.push({ key: '', value: '' })
}

const removeHeader = (index) => {
  envForm.value.headers.splice(index, 1)
}

loadEnvironments()
</script>

<style scoped>
.api-environment {
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

.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.search-input {
  width: 200px;
}

.pagination {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}

.variables-container,
.headers-container {
  max-height: 200px;
  overflow-y: auto;
}

.variable-row,
.header-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.var-input {
  width: 120px;
}

.header-input {
  width: 150px;
}
</style>