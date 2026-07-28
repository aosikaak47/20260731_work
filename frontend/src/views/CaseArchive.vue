<template>
  <div class="case-archive">
    <div class="page-header">
      <h2>用例版本归档</h2>
      <p class="page-desc">管理归档的测试用例版本，支持搜索、筛选、恢复和删除操作</p>
    </div>
    
    <el-card>
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <span class="card-title">归档列表</span>
            <el-tag type="info" size="small" class="total-tag">共 {{ pagination.total }} 条</el-tag>
          </div>
          <div class="header-right">
            <el-button size="small" type="success" @click="handleBatchRestore" :disabled="selectedArchives.length === 0">
              <el-icon><component :is="icons.Refresh" /></el-icon>
              批量恢复 ({{ selectedArchives.length }})
            </el-button>
            <el-button size="small" type="danger" @click="handleBatchDelete" :disabled="selectedArchives.length === 0">
              <el-icon><component :is="icons.Delete" /></el-icon>
              批量删除 ({{ selectedArchives.length }})
            </el-button>
          </div>
        </div>
      </template>
      
      <div class="filter-bar">
        <el-input
          v-model="searchKeyword"
          placeholder="搜索用例名称..."
          :prefix-icon="icons.Search"
          size="small"
          class="search-input"
          @keyup.enter="handleSearch"
          clearable
          @clear="handleSearch"
        />
        <el-select v-model="filterModule" size="small" placeholder="所属模块" clearable @change="handleSearch">
          <el-option label="全部" value="" />
          <el-option v-for="module in moduleOptions" :key="module" :label="module" :value="module" />
        </el-select>
        <el-button size="small" @click="handleSearch">搜索</el-button>
        <el-button size="small" @click="handleReset">重置</el-button>
      </div>
      
      <el-table :data="filteredArchives" stripe border @selection-change="handleSelectionChange" v-loading="loading">
        <el-table-column type="selection" width="50" />
        <el-table-column label="序号" width="70" type="index" :index="(index) => (pagination.currentPage - 1) * pagination.pageSize + index + 1" />
        <el-table-column prop="name" label="用例名称" min-width="180" show-overflow-tooltip />
        <el-table-column prop="module" label="所属模块" width="130">
          <template #default="scope">
            <el-tag size="small" type="success">{{ scope.row.module || '未分类' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="version" label="版本" width="100">
          <template #default="scope">
            <el-tag size="small" type="warning">{{ scope.row.version || 'v1.0' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="archive_time" label="归档时间" width="160">
          <template #default="scope">
            {{ formatDate(scope.row.archive_time) }}
          </template>
        </el-table-column>
        <el-table-column prop="reason" label="归档原因" min-width="150" show-overflow-tooltip>
          <template #default="scope">
            <el-tag size="small" effect="plain">{{ scope.row.reason || '未说明' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" class-name="action-cell" fixed="right">
          <template #default="scope">
            <div class="action-btns">
              <el-button size="small" type="primary" @click="handleRestore(scope.row)">恢复</el-button>
              <el-button size="small" type="danger" @click="handleDelete(scope.row)">删除</el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>
      
      <el-pagination
        class="pagination"
        layout="total, sizes, prev, pager, next, jumper"
        :total="pagination.total"
        :page-size="pagination.pageSize"
        v-model:current-page="pagination.currentPage"
        :page-sizes="[5, 10, 20, 50]"
        @size-change="handlePageSizeChange"
        @current-change="handlePageChange"
      />
    </el-card>
    
    <el-dialog v-model="restoreDialogVisible" title="恢复归档用例" width="450px" :close-on-click-modal="false">
      <el-form :model="restoreForm" label-width="100px">
        <el-form-item label="用例名称">
          <span>{{ restoreCase.name }}</span>
        </el-form-item>
        <el-form-item label="恢复版本">
          <el-input v-model="restoreForm.version" placeholder="请输入新版本号，如 v1.1" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="restoreDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleConfirmRestore">确认恢复</el-button>
      </template>
    </el-dialog>
    
    <el-dialog v-model="batchRestoreDialogVisible" title="批量恢复归档用例" width="450px" :close-on-click-modal="false">
      <el-form :model="batchRestoreForm" label-width="100px">
        <el-form-item label="恢复数量">
          <span>{{ selectedArchives.length }} 条用例</span>
        </el-form-item>
        <el-form-item label="恢复版本">
          <el-input v-model="batchRestoreForm.version" placeholder="请输入新版本号，如 v1.1" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="batchRestoreDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleConfirmBatchRestore">确认恢复</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import * as icons from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const loading = ref(false)
const archives = ref([])
const selectedArchives = ref([])
const searchKeyword = ref('')
const filterModule = ref('')

const pagination = reactive({
  currentPage: 1,
  pageSize: 10,
  total: 0
})

const restoreDialogVisible = ref(false)
const batchRestoreDialogVisible = ref(false)
const restoreCase = reactive({})

const restoreForm = reactive({
  version: ''
})

const batchRestoreForm = reactive({
  version: ''
})

const moduleOptions = computed(() => {
  const modules = new Set(archives.value.map(a => a.module).filter(Boolean))
  return Array.from(modules)
})

const filteredArchives = computed(() => {
  let result = archives.value
  
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    result = result.filter(a => a.name.toLowerCase().includes(keyword))
  }
  
  if (filterModule.value) {
    result = result.filter(a => a.module === filterModule.value)
  }
  
  pagination.total = result.length
  
  const start = (pagination.currentPage - 1) * pagination.pageSize
  return result.slice(start, start + pagination.pageSize)
})

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  try {
    const date = new Date(dateStr)
    return date.toLocaleString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' })
  } catch {
    return dateStr.substring(0, 19).replace('T', ' ')
  }
}

const loadArchives = async () => {
  loading.value = true
  try {
    const params = new URLSearchParams()
    if (searchKeyword.value) params.append('keyword', searchKeyword.value)
    if (filterModule.value) params.append('module', filterModule.value)
    
    const response = await fetch(`/api/v1/archives?${params.toString()}`)
    const data = await response.json()
    archives.value = data.archives || data.test_cases || []
    pagination.total = archives.value.length
  } catch (error) {
    console.error('加载归档列表失败:', error)
    ElMessage.error('加载归档列表失败')
  } finally {
    loading.value = false
  }
}

const handleSelectionChange = (val) => {
  selectedArchives.value = val
}

const handleSearch = () => {
  pagination.currentPage = 1
  loadArchives()
}

const handleReset = () => {
  searchKeyword.value = ''
  filterModule.value = ''
  pagination.currentPage = 1
  loadArchives()
}

const handlePageSizeChange = (size) => {
  pagination.pageSize = size
  pagination.currentPage = 1
}

const handlePageChange = (page) => {
  pagination.currentPage = page
}

const handleRestore = (row) => {
  Object.assign(restoreCase, row)
  restoreForm.version = row.version || 'v1.0'
  restoreDialogVisible.value = true
}

const handleConfirmRestore = async () => {
  try {
    const response = await fetch(`/api/v1/archives/${restoreCase.id}/restore`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ version: restoreForm.version })
    })
    const data = await response.json()
    if (data.success) {
      ElMessage.success('恢复成功')
      restoreDialogVisible.value = false
      loadArchives()
    } else {
      ElMessage.error(data.message || '恢复失败')
    }
  } catch (error) {
    console.error('恢复失败:', error)
    ElMessage.error('恢复失败，请检查网络连接')
  }
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除归档用例 "${row.name}" 吗？此操作不可恢复。`,
      '删除确认',
      { confirmButtonText: '确定删除', cancelButtonText: '取消', type: 'warning' }
    )
    
    const response = await fetch(`/api/v1/archives/${row.id}`, { method: 'DELETE' })
    const data = await response.json()
    if (data.success) {
      ElMessage.success('删除成功')
      loadArchives()
    } else {
      ElMessage.error(data.message || '删除失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
      ElMessage.error('删除失败')
    }
  }
}

const handleBatchRestore = () => {
  if (!selectedArchives.value.length) {
    ElMessage.warning('请选择要恢复的用例')
    return
  }
  batchRestoreForm.version = 'v1.0'
  batchRestoreDialogVisible.value = true
}

const handleConfirmBatchRestore = async () => {
  const archiveIds = selectedArchives.value.map(a => a.id)
  
  try {
    const response = await fetch('/api/v1/archives/batch_restore', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ archive_ids: archiveIds, version: batchRestoreForm.version })
    })
    const data = await response.json()
    if (data.success) {
      ElMessage.success(`成功恢复 ${archiveIds.length} 条用例`)
      batchRestoreDialogVisible.value = false
      loadArchives()
      selectedArchives.value = []
    } else {
      ElMessage.error(data.message || '批量恢复失败')
    }
  } catch (error) {
    console.error('批量恢复失败:', error)
    ElMessage.error('批量恢复失败，请检查网络连接')
  }
}

const handleBatchDelete = async () => {
  if (!selectedArchives.value.length) {
    ElMessage.warning('请选择要删除的用例')
    return
  }
  
  try {
    await ElMessageBox.confirm(
      `确定要删除选中的 ${selectedArchives.value.length} 条归档用例吗？此操作不可恢复。`,
      '批量删除确认',
      { confirmButtonText: '确定删除', cancelButtonText: '取消', type: 'warning' }
    )
    
    const archiveIds = selectedArchives.value.map(a => a.id)
    
    const response = await fetch('/api/v1/archives/batch_delete', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ archive_ids: archiveIds })
    })
    const data = await response.json()
    if (data.success) {
      ElMessage.success(`成功删除 ${archiveIds.length} 条归档用例`)
      loadArchives()
      selectedArchives.value = []
    } else {
      ElMessage.error(data.message || '批量删除失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('批量删除失败:', error)
      ElMessage.error('批量删除失败')
    }
  }
}

onMounted(() => {
  loadArchives()
})
</script>

<style scoped>
.case-archive {
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

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-right {
  display: flex;
  gap: 8px;
}

.card-title {
  font-size: 16px;
  font-weight: 600;
}

.total-tag {
  font-weight: normal;
}

.filter-bar {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
}

.search-input {
  width: 250px;
}

.pagination {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}
</style>