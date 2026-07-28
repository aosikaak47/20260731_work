<template>
  <div class="case-list">
    <div class="page-header">
      <div class="header-left">
        <h2>测试用例集管理</h2>
        <p class="page-desc">管理项目所有测试用例，支持从用例库迁移、模块树管理、筛选、编辑、批量操作</p>
      </div>
      <div class="header-right">
        <span class="filter-label">选择项目：</span>
        <el-select
          v-model="currentProjectId"
          placeholder="请选择项目"
          class="project-select"
          @change="handleProjectChange"
        >
          <el-option
            v-for="proj in projects"
            :key="proj.id"
            :label="proj.name"
            :value="proj.id"
          />
        </el-select>
      </div>
    </div>
    
    <div class="case-container">
      <div class="left-panel">
        <el-card class="module-tree-card">
          <template #header>
            <div class="card-header">
              <span class="card-title">模块树</span>
              <el-button size="small" @click="handleAddModule">
                <el-icon><component :is="icons.Plus" /></el-icon>
                新增
              </el-button>
            </div>
          </template>
          
          <el-tree
            :data="moduleTree"
            :props="{ label: 'name', children: 'children' }"
            :expand-on-click-node="false"
            highlight-current
            @node-click="handleModuleClick"
            default-expand-all
            node-key="id"
          >
            <template #default="{ node, data }">
              <span class="tree-node">
                <el-icon :size="14"><component :is="node.children ? icons.Folder : icons.Document" /></el-icon>
                {{ node.label }}
                <span class="case-count" v-if="getCaseCount(data.id) > 0">{{ getCaseCount(data.id) }}</span>
                <el-icon :size="12" class="node-actions" @click.stop="handleEditModule(node)">
                  <component :is="icons.Edit" />
                </el-icon>
                <el-icon :size="12" class="node-actions" @click.stop="handleDeleteModule(node)">
                  <component :is="icons.Delete" />
                </el-icon>
              </span>
            </template>
          </el-tree>
        </el-card>
        
        
      </div>
      
      <div class="right-panel">
        <el-card>
          <template #header>
            <div class="card-header">
              <div class="search-bar">
                <el-input 
                  v-model="searchKeyword" 
                  placeholder="搜索用例名称..." 
                  :prefix-icon="icons.Search"
                  class="search-input"
                  @keyup.enter="handleSearch"
                />
                <el-button @click="handleSearch">搜索</el-button>
                <el-button @click="handleReset">重置</el-button>
                <el-button type="primary" @click="handleOpenImportDialog">
                  <el-icon><component :is="icons.Download" /></el-icon>
                  从用例库导入
                </el-button>
              </div>
              <div class="filter-bar">
                <el-select v-model="filterModule" placeholder="模块" class="filter-select">
                  <el-option label="全部" value="" />
                  <el-option v-for="module in flatModules" :key="module.id" :label="module.name" :value="module.id" />
                </el-select>
                <el-select v-model="filterPriority" placeholder="优先级" class="filter-select">
                  <el-option label="全部" value="" />
                  <el-option label="高" value="高" />
                  <el-option label="中" value="中" />
                  <el-option label="低" value="低" />
                </el-select>
                <el-select v-model="filterType" placeholder="用例类型" class="filter-select">
                  <el-option label="全部" value="" />
                  <el-option label="功能" value="功能" />
                  <el-option label="异常" value="异常" />
                  <el-option label="边界" value="边界" />
                  <el-option label="安全" value="安全" />
                  <el-option label="性能" value="性能" />
                  <el-option label="接口" value="接口" />
                </el-select>
              </div>
            </div>
          </template>
          
          <div class="batch-actions">
            <el-button size="small" @click="handleBatchMove" :disabled="selectedCases.length === 0">
              <el-icon><component :is="icons.ArrowRight" /></el-icon>
              批量迁移
            </el-button>
            <el-button size="small" @click="handleBatchPriority" :disabled="selectedCases.length === 0">
              <el-icon><component :is="icons.CollectionTag" /></el-icon>
              批量调整优先级
            </el-button>
            <el-button size="small" type="warning" @click="handleBatchPass" :disabled="selectedCases.length === 0">
              <el-icon><component :is="icons.Check" /></el-icon>
              批量执行通过
            </el-button>
            <el-button size="small" @click="handleBatchArchive" :disabled="selectedCases.length === 0">
              <el-icon><component :is="icons.CollectionTag" /></el-icon>
              批量归档
            </el-button>
            <el-button size="small" type="success" @click="handleBatchExport" :disabled="selectedCases.length === 0">
              <el-icon><component :is="icons.Download" /></el-icon>
              批量导出
            </el-button>
            <el-button size="small" @click="handleExcelImport">
              <el-icon><component :is="icons.Upload" /></el-icon>
              Excel导入
            </el-button>
            <input ref="fileInputRef" type="file" accept=".xlsx,.xls" style="display:none" @change="handleFileChange" />
            <el-button size="small" type="danger" @click="handleBatchDelete" :disabled="selectedCases.length === 0">
              <el-icon><component :is="icons.Delete" /></el-icon>
              批量删除 ({{ selectedCases.length }})
            </el-button>
          </div>
          
          <el-table :data="cases" stripe border :row-style="{ height: '44px' }" @selection-change="handleSelectionChange">
            <el-table-column type="selection" width="50" />
            <el-table-column label="序号" width="60" align="center">
              <template #default="scope">
                <span class="index-badge">{{ (pagination.currentPage - 1) * pagination.pageSize + scope.$index + 1 }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="name" label="用例名称" min-width="200" sortable :show-overflow-tooltip="true" />
            <el-table-column prop="module" label="所属模块" width="120">
              <template #default="scope">
                <el-tag size="small" type="success" effect="plain">{{ getModuleName(scope.row.module_id) || scope.row.module }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="priority" label="优先级" width="80" align="center">
              <template #default="scope">
                <el-tag size="small" :type="scope.row.priority === '高' ? 'danger' : scope.row.priority === '中' ? 'warning' : 'info'" effect="plain">
                  {{ scope.row.priority }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="type" label="用例类型" width="100" align="center">
              <template #default="scope">
                <el-tag size="small" :type="getTagType(scope.row.type)" effect="plain">{{ scope.row.type }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="preconditions" label="前置条件" min-width="150" :show-overflow-tooltip="true" />
            <el-table-column prop="expected_result" label="预期结果" min-width="150" :show-overflow-tooltip="true" />
            <el-table-column prop="created_at" label="创建时间" width="160" sortable>
              <template #default="scope">
                {{ formatDate(scope.row.created_at) }}
              </template>
            </el-table-column>
            <el-table-column prop="status" label="状态" width="90" align="center">
              <template #default="scope">
                <el-tag size="small" :type="getStatusTagType(scope.row.status)" effect="plain">{{ scope.row.status }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="200" class-name="action-cell" fixed="right">
              <template #default="scope">
                <div class="action-btns">
                  <el-button size="small" text @click="handleView(scope.row)">查看</el-button>
                  <el-button size="small" text @click="handleEdit(scope.row)">编辑</el-button>
                  <el-button size="small" text @click="handleCopy(scope.row)">复制</el-button>
                  <el-button size="small" text type="danger" @click="handleDelete(scope.row)">删除</el-button>
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
      </div>
    </div>
    
    <el-dialog v-model="viewDialogVisible" title="查看测试用例" width="600px" :close-on-click-modal="false">
      <el-descriptions :column="2" border>
        <el-descriptions-item label="用例名称">{{ viewCase.name }}</el-descriptions-item>
        <el-descriptions-item label="所属模块">{{ getModuleName(viewCase.module_id) || viewCase.module }}</el-descriptions-item>
        <el-descriptions-item label="用例类型"><el-tag :type="getTagType(viewCase.type)">{{ viewCase.type }}</el-tag></el-descriptions-item>
        <el-descriptions-item label="优先级"><el-tag :type="viewCase.priority === '高' ? 'danger' : viewCase.priority === '中' ? 'warning' : 'info'">{{ viewCase.priority }}</el-tag></el-descriptions-item>
        <el-descriptions-item label="状态" :span="2"><el-tag :type="getStatusTagType(viewCase.status)">{{ viewCase.status }}</el-tag></el-descriptions-item>
        <el-descriptions-item label="前置条件" :span="2">{{ viewCase.preconditions || '-' }}</el-descriptions-item>
        <el-descriptions-item label="测试步骤" :span="2">
          <div v-if="Array.isArray(viewCase.steps)">
            <p v-for="(step, i) in viewCase.steps" :key="i">{{ i + 1 }}. {{ step }}</p>
          </div>
          <span v-else>{{ viewCase.steps || '-' }}</span>
        </el-descriptions-item>
        <el-descriptions-item label="预期结果" :span="2">{{ viewCase.expected_result || '-' }}</el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ formatDate(viewCase.created_at) }}</el-descriptions-item>
        <el-descriptions-item label="更新时间">{{ formatDate(viewCase.updated_at) }}</el-descriptions-item>
      </el-descriptions>
      <template #footer>
        <el-button @click="viewDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>
    
    <el-dialog v-model="editDialogVisible" title="编辑测试用例" width="600px" :close-on-click-modal="false">
      <el-form :model="editForm" label-width="100px">
        <el-form-item label="用例名称" required>
          <el-input v-model="editForm.name" />
        </el-form-item>
        <el-form-item label="所属模块" required>
          <el-select v-model="editForm.module_id">
            <el-option v-for="module in flatModules" :key="module.id" :label="module.name" :value="module.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="用例类型">
          <el-select v-model="editForm.type">
            <el-option label="功能" value="功能" />
            <el-option label="异常" value="异常" />
            <el-option label="边界" value="边界" />
            <el-option label="安全" value="安全" />
            <el-option label="性能" value="性能" />
            <el-option label="接口" value="接口" />
          </el-select>
        </el-form-item>
        <el-form-item label="优先级">
          <el-select v-model="editForm.priority">
            <el-option label="高" value="高" />
            <el-option label="中" value="中" />
            <el-option label="低" value="低" />
          </el-select>
        </el-form-item>
        <el-form-item label="前置条件">
          <el-input v-model="editForm.preconditions" type="textarea" :rows="3" />
        </el-form-item>
        <el-form-item label="测试步骤">
          <el-input v-model="editForm.stepsText" type="textarea" :rows="4" placeholder="每个步骤一行" />
        </el-form-item>
        <el-form-item label="预期结果">
          <el-input v-model="editForm.expected_result" type="textarea" :rows="3" />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="editForm.status">
            <el-option label="未执行" value="未执行" />
            <el-option label="执行中" value="执行中" />
            <el-option label="通过" value="通过" />
            <el-option label="失败" value="失败" />
            <el-option label="阻塞" value="阻塞" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSaveEdit">保存</el-button>
      </template>
    </el-dialog>
    
    <el-dialog v-model="moduleDialogVisible" :title="editingModule ? '编辑模块' : '新增模块'" width="400px">
      <el-form :model="moduleForm" label-width="80px">
        <el-form-item label="所属项目">
          <el-tag v-if="currentProject" type="success">{{ currentProject.name }}</el-tag>
          <span v-else class="no-project">请先在页面顶部选择项目</span>
        </el-form-item>
        <el-form-item label="模块名称" required>
          <el-input v-model="moduleForm.name" />
        </el-form-item>
        <el-form-item label="父模块">
          <el-select v-model="moduleForm.parent_id" placeholder="无（顶级模块）">
            <el-option label="无（顶级模块）" value="" />
            <el-option v-for="module in flatModules" :key="module.id" :label="module.name" :value="module.id" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="moduleDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSaveModule" :disabled="!currentProjectId">保存</el-button>
      </template>
    </el-dialog>
    
    <el-dialog v-model="batchMoveDialogVisible" title="批量迁移用例" width="400px">
      <el-form :model="batchMoveForm" label-width="100px">
        <el-form-item label="目标模块" required>
          <el-select v-model="batchMoveForm.target_module_id">
            <el-option v-for="module in flatModules" :key="module.id" :label="module.name" :value="module.id" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="batchMoveDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleConfirmBatchMove">确认迁移</el-button>
      </template>
    </el-dialog>
    
    <el-dialog v-model="batchPriorityDialogVisible" title="批量调整优先级" width="400px">
      <el-form :model="batchPriorityForm" label-width="100px">
        <el-form-item label="目标优先级" required>
          <el-select v-model="batchPriorityForm.priority">
            <el-option label="高" value="高" />
            <el-option label="中" value="中" />
            <el-option label="低" value="低" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="batchPriorityDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleConfirmBatchPriority">确认调整</el-button>
      </template>
    </el-dialog>
    
    <el-dialog v-model="importDialogVisible" title="从用例库导入" width="900px" :close-on-click-modal="false">
      <div class="import-dialog-content">
        <div class="import-left">
          <div class="import-section-header">
            <span>用例库列表</span>
            <el-button size="small" @click="loadLibraryCases">
              <el-icon><component :is="icons.Refresh" /></el-icon>
              刷新
            </el-button>
          </div>
          <div v-if="libraryCases.length === 0" class="empty-library">
            <el-icon :size="48" color="#909399"><component :is="icons.MessageBox" /></el-icon>
            <span>用例库为空，请先在AI用例生成页面导入用例</span>
          </div>
          <el-table v-else :data="libraryCases" stripe @selection-change="handleLibrarySelectionChange">
            <el-table-column type="selection" width="50" />
            <el-table-column prop="name" label="用例名称" min-width="200" show-overflow-tooltip />
            <el-table-column prop="module" label="所属模块" width="120">
              <template #default="scope">
                <el-tag size="small" type="success">{{ scope.row.module || '未分类' }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="type" label="用例类型" width="100">
              <template #default="scope">
                <el-tag :type="getTagType(scope.row.type)">{{ scope.row.type }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="priority" label="优先级" width="80">
              <template #default="scope">
                <el-tag :type="scope.row.priority === '高' ? 'danger' : scope.row.priority === '中' ? 'warning' : 'info'">
                  {{ scope.row.priority }}
                </el-tag>
              </template>
            </el-table-column>
          </el-table>
        </div>
        <div class="import-right">
          <div class="import-section-header">
            <span>目标模块</span>
          </div>
          <el-tree
            :data="moduleTree"
            :props="{ label: 'name', children: 'children' }"
            :expand-on-click-node="false"
            highlight-current
            @node-click="handleImportModuleClick"
            default-expand-all
            node-key="id"
          >
            <template #default="{ node, data }">
              <span class="tree-node">
                <el-icon :size="14"><component :is="node.children ? icons.Folder : icons.Document" /></el-icon>
                {{ node.label }}
                <span class="case-count" v-if="getCaseCount(data.id) > 0">{{ getCaseCount(data.id) }}</span>
              </span>
            </template>
          </el-tree>
          <div class="selected-module-info">
            <span>已选择模块：</span>
            <el-tag type="primary" v-if="importTargetModuleId">{{ getModuleName(importTargetModuleId) }}</el-tag>
            <span v-else class="no-selection">请选择目标模块</span>
          </div>
        </div>
      </div>
      <template #footer>
        <el-button @click="importDialogVisible = false">取消</el-button>
        <el-button 
          type="primary" 
          @click="handleConfirmImport"
          :disabled="!selectedLibraryCases.length || !importTargetModuleId"
        >
          <el-icon><component :is="icons.ArrowRight" /></el-icon>
          导入选中用例 ({{ selectedLibraryCases.length }})
        </el-button>
      </template>
    </el-dialog>
    
    <el-dialog v-model="archiveDialogVisible" title="批量归档用例" width="450px" :close-on-click-modal="false">
      <el-form :model="archiveForm" label-width="100px">
        <el-form-item label="归档数量">
          <span>{{ selectedCases.length }} 条用例</span>
        </el-form-item>
        <el-form-item label="归档原因" required>
          <el-input v-model="archiveForm.reason" type="textarea" :rows="3" placeholder="请输入归档原因" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="archiveDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleConfirmArchive">确认归档</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import * as icons from '@element-plus/icons-vue'
import * as XLSX from 'xlsx'
import { ElMessage } from 'element-plus'
import { useProjects } from '../composables/useProjects'

const { projects, currentProjectId, currentProject, loadProjects, setCurrentProject } = useProjects()

const searchKeyword = ref('')
const filterModule = ref('')
const filterPriority = ref('')
const filterType = ref('')
const selectedModuleId = ref('')
const selectedCases = ref([])
const libraryCases = ref([])

const pagination = reactive({
  currentPage: 1,
  pageSize: 10,
  total: 0
})

const moduleTree = ref([])
const cases = ref([])
const viewCase = reactive({})
const editingCase = ref(null)
const editingModule = ref(null)

const viewDialogVisible = ref(false)
const editDialogVisible = ref(false)
const moduleDialogVisible = ref(false)
const batchMoveDialogVisible = ref(false)
const batchPriorityDialogVisible = ref(false)
const importDialogVisible = ref(false)
const importTargetModuleId = ref('')
const fileInputRef = ref(null)
const archiveDialogVisible = ref(false)

const archiveForm = reactive({
  reason: ''
})

const editForm = reactive({
  name: '',
  module_id: '',
  type: '功能',
  priority: '中',
  preconditions: '',
  stepsText: '',
  expected_result: '',
  status: '未执行'
})

const moduleForm = reactive({
  name: '',
  parent_id: ''
})

const batchMoveForm = reactive({
  target_module_id: ''
})

const batchPriorityForm = reactive({
  priority: '中'
})

const flatModules = computed(() => {
  const result = []
  const flatten = (nodes, prefix = '') => {
    nodes.forEach(node => {
      result.push({ id: node.id, name: prefix ? `${prefix} / ${node.name}` : node.name })
      if (node.children) {
        flatten(node.children, prefix ? `${prefix} / ${node.name}` : node.name)
      }
    })
  }
  flatten(moduleTree.value)
  return result
})

const selectedLibraryCases = ref([])

const getCaseCount = (moduleId) => {
  return cases.value.filter(c => c.module_id === moduleId).length
}

const getModuleName = (moduleId) => {
  if (!moduleId) return ''
  let name = ''
  const find = (nodes) => {
    nodes.forEach(node => {
      if (node.id === moduleId) {
        name = node.name
      } else if (node.children) {
        find(node.children)
      }
    })
  }
  find(moduleTree.value)
  return name
}

const getTagType = (type) => {
  const types = { '功能': 'primary', '异常': 'danger', '边界': 'warning', '安全': 'info', '性能': 'success', '接口': 'success' }
  return types[type] || 'info'
}

const getStatusTagType = (status) => {
  const types = { '未执行': 'info', '执行中': 'warning', '通过': 'success', '失败': 'danger', '阻塞': 'error' }
  return types[status] || 'info'
}

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  try {
    const date = new Date(dateStr)
    return date.toLocaleString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' })
  } catch {
    return dateStr.substring(0, 19).replace('T', ' ')
  }
}

const loadModules = async () => {
  try {
    const params = new URLSearchParams()
    if (currentProjectId.value) params.append('project_id', currentProjectId.value)
    const response = await fetch(`/api/v1/modules${params.toString() ? '?' + params.toString() : ''}`)
    const data = await response.json()
    moduleTree.value = data.modules || []
  } catch (error) {
    console.error('加载模块树失败:', error)
  }
}

const loadCases = async () => {
  try {
    const params = new URLSearchParams()
    if (currentProjectId.value) params.append('project_id', currentProjectId.value)
    if (selectedModuleId.value) params.append('module_id', selectedModuleId.value)
    if (searchKeyword.value) params.append('keyword', searchKeyword.value)
    if (filterPriority.value) params.append('priority', filterPriority.value)
    if (filterType.value) params.append('case_type', filterType.value)
    params.append('page', pagination.currentPage)
    params.append('page_size', pagination.pageSize)
    
    const response = await fetch(`/api/v1/managed_cases?${params.toString()}`)
    const data = await response.json()
    cases.value = data.test_cases || []
    pagination.total = data.total || 0
  } catch (error) {
    console.error('加载用例失败:', error)
  }
}

const handleProjectChange = () => {
  setCurrentProject(currentProjectId.value)
  selectedModuleId.value = ''
  filterModule.value = ''
  searchKeyword.value = ''
  filterPriority.value = ''
  filterType.value = ''
  pagination.currentPage = 1
  loadModules()
  loadCases()
}

const loadLibraryCases = async () => {
  try {
    const response = await fetch('/api/v1/case_library')
    const data = await response.json()
    libraryCases.value = (data.test_cases || []).map(c => ({ ...c, selected: false }))
  } catch (error) {
    console.error('加载用例库失败:', error)
  }
}

const handleModuleClick = (data) => {
  selectedModuleId.value = data.id
  filterModule.value = data.id
  pagination.currentPage = 1
  loadCases()
}

const handleAddModule = () => {
  if (!currentProjectId.value) {
    ElMessage.warning('请先选择项目')
    return
  }
  editingModule.value = null
  moduleForm.name = ''
  moduleForm.parent_id = ''
  moduleDialogVisible.value = true
}

const handleEditModule = (node) => {
  editingModule.value = node.data
  moduleForm.name = node.data.name
  moduleForm.parent_id = ''
  moduleDialogVisible.value = true
}

const handleDeleteModule = (node) => {
  if (confirm(`确定要删除模块 "${node.label}" 吗？此操作会删除该模块下的所有子模块和用例。`)) {
    const url = `/api/v1/modules/${node.data.id}?project_id=${currentProjectId.value}`
    fetch(url, { method: 'DELETE' })
      .then(response => response.json())
      .then(data => {
        if (data.success) {
          moduleTree.value = data.modules
          loadCases()
          alert('模块删除成功')
        }
      })
      .catch(error => console.error('删除模块失败:', error))
  }
}

const handleSaveModule = async () => {
  if (!moduleForm.name) {
    alert('模块名称不能为空')
    return
  }
  
  const url = editingModule.value ? `/api/v1/modules/${editingModule.value.id}` : '/api/v1/modules'
  const method = editingModule.value ? 'PUT' : 'POST'
  
  try {
    const payload = {
      ...moduleForm,
      project_id: currentProjectId.value
    }
    const response = await fetch(url, {
      method: method,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })
    const data = await response.json()
    if (data.success) {
      moduleTree.value = data.modules || []
      moduleDialogVisible.value = false
      alert(data.message)
    } else {
      alert(data.message || '保存失败')
    }
  } catch (error) {
    console.error('保存模块失败:', error)
    alert('保存模块失败，请检查网络连接')
  }
}

const handleSearch = () => {
  pagination.currentPage = 1
  loadCases()
}

const handleReset = () => {
  searchKeyword.value = ''
  filterModule.value = ''
  filterPriority.value = ''
  filterType.value = ''
  selectedModuleId.value = ''
  pagination.currentPage = 1
  loadCases()
}

const handleSelectionChange = (val) => {
  selectedCases.value = val
}

const handleOpenImportDialog = () => {
  importTargetModuleId.value = ''
  loadLibraryCases()
  importDialogVisible.value = true
}

const handleLibrarySelectionChange = (val) => {
  selectedLibraryCases.value = val
}

const handleImportModuleClick = (data) => {
  importTargetModuleId.value = data.id
}

const handleConfirmImport = async () => {
  if (!selectedLibraryCases.value.length) {
    alert('请选择要导入的用例')
    return
  }
  if (!importTargetModuleId.value) {
    alert('请选择目标模块')
    return
  }
  
  const caseIds = selectedLibraryCases.value.map(c => c.id)
  
  try {
    const response = await fetch('/api/v1/migrate_from_library', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
        case_ids: caseIds, 
        target_module_id: importTargetModuleId.value,
        project_id: currentProjectId.value || ''
      })
    })
    const data = await response.json()
    if (data.success) {
      ElMessage.success(data.message)
      importDialogVisible.value = false
      loadLibraryCases()
      loadCases()
      selectedLibraryCases.value = []
      importTargetModuleId.value = ''
    } else {
      ElMessage.error(data.message || '导入失败')
    }
  } catch (error) {
    console.error('导入失败:', error)
    ElMessage.error('导入失败，请检查网络连接')
  }
}

const handleBatchMove = () => {
  if (!selectedCases.value.length) {
    alert('请选择要迁移的用例')
    return
  }
  batchMoveForm.target_module_id = ''
  batchMoveDialogVisible.value = true
}

const handleConfirmBatchMove = () => {
  if (!batchMoveForm.target_module_id) {
    alert('请选择目标模块')
    return
  }
  
  const caseIds = selectedCases.value.map(c => c.id)
  
  fetch('/api/v1/managed_cases/batch_move', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ case_ids: caseIds, target_module_id: batchMoveForm.target_module_id })
  })
    .then(response => response.json())
    .then(data => {
      if (data.success) {
        alert(data.message)
        batchMoveDialogVisible.value = false
        loadCases()
        selectedCases.value = []
      }
    })
    .catch(error => console.error('批量迁移失败:', error))
}

const handleBatchPriority = () => {
  if (!selectedCases.value.length) {
    alert('请选择要调整优先级的用例')
    return
  }
  batchPriorityForm.priority = '中'
  batchPriorityDialogVisible.value = true
}

const handleConfirmBatchPriority = () => {
  const caseIds = selectedCases.value.map(c => c.id)
  
  fetch('/api/v1/managed_cases/batch_priority', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ case_ids: caseIds, priority: batchPriorityForm.priority })
  })
    .then(response => response.json())
    .then(data => {
      if (data.success) {
        alert(data.message)
        batchPriorityDialogVisible.value = false
        loadCases()
        selectedCases.value = []
      }
    })
    .catch(error => console.error('批量调整优先级失败:', error))
}

const handleBatchArchive = () => {
  if (!selectedCases.value.length) {
    ElMessage.warning('请选择要归档的用例')
    return
  }
  archiveForm.reason = ''
  archiveDialogVisible.value = true
}

const handleConfirmArchive = async () => {
  if (!archiveForm.reason.trim()) {
    ElMessage.warning('请输入归档原因')
    return
  }
  
  const caseIds = selectedCases.value.map(c => c.id)
  
  try {
    const response = await fetch('/api/v1/managed_cases/batch_archive', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ case_ids: caseIds, reason: archiveForm.reason })
    })
    const data = await response.json()
    if (data.success) {
      ElMessage.success(data.message || '归档成功')
      archiveDialogVisible.value = false
      loadCases()
      selectedCases.value = []
    } else {
      ElMessage.error(data.message || '归档失败')
    }
  } catch (error) {
    console.error('归档失败:', error)
    ElMessage.error('归档失败，请检查网络连接')
  }
}

const handleBatchPass = async () => {
  if (!selectedCases.value.length) {
    ElMessage.warning('请选择要执行通过的用例')
    return
  }
  
  const caseIds = selectedCases.value.map(c => c.id)
  
  try {
    const response = await fetch('/api/v1/managed_cases/batch_status', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ case_ids: caseIds, status: '通过' })
    })
    const data = await response.json()
    if (data.success) {
      ElMessage.success(`已将 ${selectedCases.value.length} 条用例状态更新为"通过"`)
      loadCases()
      selectedCases.value = []
    } else {
      ElMessage.error(data.message || '操作失败')
    }
  } catch (error) {
    console.error('批量执行通过失败:', error)
    ElMessage.error('操作失败，请检查网络连接')
  }
}

const handleBatchExport = () => {
  if (!selectedCases.value.length) {
    ElMessage.warning('请选择要导出的用例')
    return
  }
  
  const exportData = selectedCases.value.map((c, i) => ({
    '序号': i + 1,
    '用例名称': c.name || '',
    '所属模块': getModuleName(c.module_id) || c.module || '',
    '优先级': c.priority || '',
    '用例类型': c.type || '',
    '前置条件': c.preconditions || '',
    '测试步骤': Array.isArray(c.steps) ? c.steps.join('\n') : (c.steps || ''),
    '预期结果': c.expected_result || '',
    '状态': c.status || '',
    '创建时间': formatDate(c.created_at),
    '更新时间': formatDate(c.updated_at)
  }))
  
  const ws = XLSX.utils.json_to_sheet(exportData)
  ws['!cols'] = [
    { wch: 6 }, { wch: 30 }, { wch: 15 }, { wch: 8 }, { wch: 10 },
    { wch: 20 }, { wch: 30 }, { wch: 20 }, { wch: 8 }, { wch: 18 }, { wch: 18 }
  ]
  
  const wb = XLSX.utils.book_new()
  XLSX.utils.book_append_sheet(wb, ws, '测试用例')
  
  const fileName = `测试用例_${new Date().toLocaleDateString('zh-CN').replace(/\//g, '-')}.xlsx`
  XLSX.writeFile(wb, fileName)
  
  ElMessage.success(`成功导出 ${selectedCases.value.length} 条用例`)
}

const handleExcelImport = () => {
  fileInputRef.value.click()
}

const handleFileChange = async (event) => {
  const file = event.target.files[0]
  if (!file) return
  
  try {
    const data = await file.arrayBuffer()
    const workbook = XLSX.read(data, { type: 'array' })
    const sheetName = workbook.SheetNames[0]
    const worksheet = workbook.Sheets[sheetName]
    const jsonData = XLSX.utils.sheet_to_json(worksheet)
    
    const importCases = jsonData.map(row => ({
      name: row['用例名称'] || '',
      module: row['所属模块'] || '',
      priority: row['优先级'] || '中',
      type: row['用例类型'] || '功能',
      preconditions: row['前置条件'] || '',
      steps: row['测试步骤'] ? String(row['测试步骤']).split('\n').filter(s => s.trim()) : [],
      expected_result: row['预期结果'] || '',
      status: '未执行'
    })).filter(c => c.name)
    
    if (importCases.length === 0) {
      ElMessage.warning('未解析到有效的用例数据')
      return
    }
    
    const response = await fetch('/api/v1/managed_cases/import', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ cases: importCases })
    })
    const result = await response.json()
    
    if (result.success) {
      ElMessage.success(`成功导入 ${importCases.length} 条用例`)
      loadCases()
    } else {
      ElMessage.error(result.message || '导入失败')
    }
  } catch (error) {
    console.error('Excel导入失败:', error)
    ElMessage.error('Excel导入失败，请检查文件格式')
  } finally {
    event.target.value = ''
  }
}

const handleBatchDelete = () => {
  if (!selectedCases.value.length) {
    alert('请选择要删除的用例')
    return
  }
  
  if (confirm(`确定要删除选中的 ${selectedCases.value.length} 条用例吗？此操作不可恢复。`)) {
    const caseIds = selectedCases.value.map(c => c.id)
    
    fetch('/api/v1/managed_cases/batch_delete', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ case_ids: caseIds })
    })
      .then(response => response.json())
      .then(data => {
        if (data.success) {
          alert(data.message)
          loadCases()
          selectedCases.value = []
        }
      })
      .catch(error => console.error('批量删除失败:', error))
  }
}

const handleView = (row) => {
  Object.assign(viewCase, row)
  viewDialogVisible.value = true
}

const handleEdit = (row) => {
  editingCase.value = row
  editForm.name = row.name
  editForm.module_id = row.module_id || ''
  editForm.type = row.type || '功能'
  editForm.priority = row.priority || '中'
  editForm.preconditions = row.preconditions || ''
  editForm.stepsText = Array.isArray(row.steps) ? row.steps.join('\n') : (row.steps || '')
  editForm.expected_result = row.expected_result || ''
  editForm.status = row.status || '未执行'
  editDialogVisible.value = true
}

const handleSaveEdit = () => {
  if (!editForm.name) {
    alert('用例名称不能为空')
    return
  }
  
  const updates = {
    ...editForm,
    steps: editForm.stepsText.split('\n').filter(s => s.trim())
  }
  delete updates.stepsText
  
  fetch(`/api/v1/managed_cases/${editingCase.value.id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ updates })
  })
    .then(response => response.json())
    .then(data => {
      if (data.success) {
        alert(data.message)
        editDialogVisible.value = false
        loadCases()
      }
    })
    .catch(error => console.error('保存用例失败:', error))
}

const handleCopy = (row) => {
  const newCase = {
    ...row,
    id: '',
    name: `${row.name} (副本)`,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString()
  }
  
  fetch('/api/v1/managed_cases', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ case: newCase })
  })
    .then(response => response.json())
    .then(data => {
      if (data.success) {
        alert('用例复制成功')
        loadCases()
      }
    })
    .catch(error => console.error('复制用例失败:', error))
}

const handleDelete = (row) => {
  if (confirm(`确定要删除用例 "${row.name}" 吗？此操作不可恢复。`)) {
    fetch(`/api/v1/managed_cases/${row.id}`, { method: 'DELETE' })
      .then(response => response.json())
      .then(data => {
        if (data.success) {
          alert(data.message)
          loadCases()
        }
      })
      .catch(error => console.error('删除用例失败:', error))
  }
}

const handlePageSizeChange = (size) => {
  pagination.pageSize = size
  pagination.currentPage = 1
  loadCases()
}

const handlePageChange = (page) => {
  pagination.currentPage = page
  loadCases()
}

onMounted(async () => {
  await loadProjects()
  if (currentProjectId.value) {
    loadModules()
    loadCases()
  }
  loadLibraryCases()
})

watch(currentProjectId, () => {
  if (currentProjectId.value) {
    loadModules()
    loadCases()
  }
})
</script>

<style scoped>
.case-list {
  padding: 20px;
}

.page-header {
  margin-bottom: 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 16px;
}

.header-left {
  flex: 1;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 8px;
}

.filter-label {
  font-size: 14px;
  color: #6b7280;
  font-weight: 500;
}

.project-select {
  width: 220px;
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

.case-container {
  display: grid;
  grid-template-columns: 320px 1fr;
  gap: 20px;
}

.left-panel {
  position: sticky;
  top: 20px;
  align-self: flex-start;
}

.module-tree-card {
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

.tree-node {
  display: flex;
  align-items: center;
  gap: 6px;
}

.case-count {
  font-size: 12px;
  color: #67c23a;
  background: #f0f9eb;
  padding: 1px 6px;
  border-radius: 10px;
  margin-left: 4px;
}

.node-actions {
  opacity: 0;
  margin-left: 4px;
  cursor: pointer;
}

.el-tree-node:hover .node-actions {
  opacity: 1;
}

.empty-library {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 30px;
  color: #909399;
}

.empty-library span {
  margin-top: 12px;
  font-size: 14px;
}

.import-dialog-content {
  display: flex;
  gap: 20px;
  height: 450px;
}

.import-left {
  flex: 1;
  display: flex;
  flex-direction: column;
  border-right: 1px solid #f0f0f0;
  padding-right: 20px;
}

.import-right {
  flex: 0 0 320px;
  display: flex;
  flex-direction: column;
}

.import-section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
  font-size: 15px;
  font-weight: 600;
}

.import-right .el-tree {
  flex: 1;
  overflow-y: auto;
}

.selected-module-info {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #f0f0f0;
  font-size: 14px;
}

.no-selection {
  color: #909399;
}

.search-bar {
  display: flex;
  gap: 8px;
}

.search-input {
  width: 260px;
}

.filter-bar {
  display: flex;
  gap: 12px;
  align-items: center;
}

.filter-select {
  width: 140px;
}

.batch-actions {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
  padding-bottom: 16px;
  border-bottom: 1px solid #f0f0f0;
}

.pagination {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}

.index-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 22px;
  height: 22px;
  background: var(--color-bg-hover);
  border-radius: var(--radius-sm);
  font-size: 12px;
  color: var(--color-text-secondary);
  font-weight: var(--font-weight-medium);
}

.action-btns {
  display: flex;
  gap: 4px;
  flex-wrap: nowrap;
}
</style>