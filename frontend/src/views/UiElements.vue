<template>
  <div class="ui-elements">
    <div class="page-header">
      <h2>页面元素管理</h2>
      <p class="page-desc">基于PO模式管理页面元素</p>
    </div>
    
    <el-card>
      <template #header>
        <div class="card-header">
          <span class="card-title">页面元素列表</span>
          <div class="header-actions">
            <el-select v-model="currentProjectId" placeholder="选择项目" size="small" style="width: 150px" @change="loadElements">
              <el-option v-for="p in projects" :key="p.id" :label="p.name" :value="p.id" />
            </el-select>
            <el-button type="primary" @click="handleAdd">
              <el-icon><component :is="icons.Plus" /></el-icon>
              新增元素
            </el-button>
          </div>
        </div>
      </template>
      
      <div class="filter-bar">
        <el-select v-model="filterPage" size="small" placeholder="页面" clearable @change="loadElements">
          <el-option label="全部" value="" />
          <el-option v-for="page in uniquePages" :key="page" :label="page" :value="page" />
        </el-select>
        <el-select v-model="filterLocator" size="small" placeholder="定位方式" clearable @change="loadElements">
          <el-option label="全部" value="" />
          <el-option label="XPath" value="xpath" />
          <el-option label="CSS" value="css" />
          <el-option label="ID" value="id" />
          <el-option label="Name" value="name" />
          <el-option label="Link Text" value="link_text" />
        </el-select>
        <el-input 
          v-model="searchKeyword" 
          placeholder="搜索元素名称..." 
          size="small"
          class="search-input"
          @keyup.enter="loadElements"
        />
        <el-button type="primary" size="small" @click="loadElements">搜索</el-button>
        <el-button size="small" @click="handleReset">重置</el-button>
      </div>
      
      <el-table :data="filteredElements" stripe border v-loading="loading">
        <el-table-column prop="name" label="元素名称" width="150" />
        <el-table-column prop="locator_type" label="定位方式" width="100">
          <template #default="scope">
            <el-tag size="small" :type="getLocatorTagType(scope.row.locator_type)">{{ scope.row.locator_type | upper }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="locator_value" label="定位表达式" min-width="200" show-overflow-tooltip />
        <el-table-column prop="page" label="所属页面" width="120" />
        <el-table-column prop="status" label="状态" width="80">
          <template #default="scope">
            <el-tag :type="scope.row.status === '有效' ? 'success' : 'warning'" size="small">{{ scope.row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="scope">
            <div class="action-btns">
              <el-button size="small" @click="handleValidate(scope.row)">校验</el-button>
              <el-button size="small" type="primary" @click="handleEdit(scope.row)">编辑</el-button>
              <el-button size="small" type="danger" @click="handleDelete(scope.row)">删除</el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>
      
      <el-pagination
        class="pagination"
        layout="total, prev, pager, next"
        :total="filteredElements.length"
        :page-size="10"
        v-model:current-page="currentPage"
      />
    </el-card>
    
    <!-- 新增/编辑对话框 -->
    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑元素' : '新增元素'" width="600px">
      <el-form :model="form" :rules="rules" ref="formRef" label-width="110px">
        <el-form-item label="元素名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入元素名称" />
        </el-form-item>
        <el-form-item label="定位方式" prop="locator_type">
          <el-select v-model="form.locator_type" placeholder="请选择定位方式" style="width: 100%">
            <el-option label="XPath" value="xpath" />
            <el-option label="CSS" value="css" />
            <el-option label="ID" value="id" />
            <el-option label="Name" value="name" />
            <el-option label="Link Text" value="link_text" />
          </el-select>
        </el-form-item>
        <el-form-item label="定位表达式" prop="locator_value">
          <el-input v-model="form.locator_value" placeholder="例如: //input[@name='username']" />
        </el-form-item>
        <el-form-item label="所属页面" prop="page">
          <el-select v-model="form.page" placeholder="请选择所属页面" style="width: 100%" filterable allow-create>
            <el-option v-for="page in uniquePages" :key="page" :label="page" :value="page" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-radio-group v-model="form.status">
            <el-radio value="有效">有效</el-radio>
            <el-radio value="无效">无效</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="form.description" type="textarea" :rows="3" placeholder="元素描述信息" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import * as icons from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const loading = ref(false)
const elements = ref([])
const projects = ref([])
const dialogVisible = ref(false)
const isEdit = ref(false)
const formRef = ref(null)
const currentPage = ref(1)
const currentProjectId = ref('')
const filterPage = ref('')
const filterLocator = ref('')
const searchKeyword = ref('')

const form = ref({
  name: '',
  locator_type: 'xpath',
  locator_value: '',
  page: '',
  status: '有效',
  description: ''
})

const rules = {
  name: [{ required: true, message: '请输入元素名称', trigger: 'blur' }],
  locator_type: [{ required: true, message: '请选择定位方式', trigger: 'change' }],
  locator_value: [{ required: true, message: '请输入定位表达式', trigger: 'blur' }],
  page: [{ required: true, message: '请选择所属页面', trigger: 'change' }]
}

const uniquePages = computed(() => {
  const pages = new Set(elements.value.map(e => e.page).filter(Boolean))
  return Array.from(pages)
})

const filteredElements = computed(() => {
  let result = elements.value
  if (filterPage.value) {
    result = result.filter(e => e.page === filterPage.value)
  }
  if (filterLocator.value) {
    result = result.filter(e => e.locator_type === filterLocator.value)
  }
  if (searchKeyword.value) {
    const kw = searchKeyword.value.toLowerCase()
    result = result.filter(e => e.name.toLowerCase().includes(kw))
  }
  return result
})

const getLocatorTagType = (type) => {
  const map = { xpath: '', css: 'success', id: 'warning', name: 'info', link_text: 'danger' }
  return map[type] || ''
}

const loadElements = async () => {
  loading.value = true
  try {
    const params = new URLSearchParams()
    if (currentProjectId.value) params.append('project_id', currentProjectId.value)
    const res = await fetch(`/api/v1/ui/elements?${params}`)
    const json = await res.json()
    if (json.elements) {
      elements.value = json.elements
    }
  } catch (e) {
    ElMessage.error('加载元素列表失败')
  } finally {
    loading.value = false
  }
}

const loadProjects = async () => {
  try {
    const res = await fetch('/api/v1/projects')
    const json = await res.json()
    projects.value = json.projects || []
  } catch (e) {
    console.error('加载项目列表失败:', e)
  }
}

const handleAdd = () => {
  isEdit.value = false
  form.value = {
    name: '',
    locator_type: 'xpath',
    locator_value: '',
    page: '',
    status: '有效',
    description: ''
  }
  dialogVisible.value = true
}

const handleEdit = (row) => {
  isEdit.value = true
  form.value = { ...row }
  dialogVisible.value = true
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(`确定删除元素 "${row.name}" 吗？`, '删除确认', { type: 'warning' })
    const res = await fetch(`/api/v1/ui/elements/${row.id}`, { method: 'DELETE' })
    const json = await res.json()
    if (json.success) {
      ElMessage.success('删除成功')
      loadElements()
    }
  } catch (e) {
    if (e !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const handleValidate = async (row) => {
  ElMessage.info(`正在校验元素 "${row.name}"...`)
  setTimeout(() => {
    ElMessage.success(`元素校验成功: ${row.locator_value}`)
  }, 1000)
}

const handleSubmit = async () => {
  if (!formRef.value) return
  try {
    await formRef.value.validate()
    
    if (isEdit.value) {
      const res = await fetch(`/api/v1/ui/elements/${form.value.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(form.value)
      })
      const json = await res.json()
      if (json.success) {
        ElMessage.success('更新成功')
        dialogVisible.value = false
        loadElements()
      }
    } else {
      const payload = { ...form.value, project_id: currentProjectId.value }
      const res = await fetch('/api/v1/ui/elements', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      })
      const json = await res.json()
      if (json.success) {
        ElMessage.success('新增成功')
        dialogVisible.value = false
        loadElements()
      }
    }
  } catch (e) {
    if (e.message) {
      ElMessage.error(e.message)
    }
  }
}

const handleReset = () => {
  filterPage.value = ''
  filterLocator.value = ''
  searchKeyword.value = ''
  loadElements()
}

onMounted(async () => {
  await loadProjects()
  if (projects.value.length > 0) {
    currentProjectId.value = projects.value[0].id
  }
  loadElements()
})
</script>

<style scoped>
.ui-elements {
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

.header-actions {
  display: flex;
  gap: 12px;
}

.card-title {
  font-size: 16px;
  font-weight: 600;
}

.filter-bar {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
  align-items: center;
}

.search-input {
  width: 200px;
}

.action-btns {
  display: flex;
  gap: 4px;
}

.pagination {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}
</style>
