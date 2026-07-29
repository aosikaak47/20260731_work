<template>
  <div class="ui-tasks">
    <div class="page-header">
      <h2>UI测试任务</h2>
      <p class="page-desc">管理UI自动化测试任务，支持多浏览器执行和实时结果查看</p>
    </div>

    <el-card>
      <template #header>
        <div class="card-header">
          <span class="card-title">任务列表</span>
          <div class="header-actions">
            <el-input
              v-model="searchKeyword"
              placeholder="搜索任务名称或项目"
              size="small"
              class="search-input"
              clearable
            >
              <template #prefix>
                <el-icon><component :is="icons.Search" /></el-icon>
              </template>
            </el-input>
            <el-select v-model="filterStatus" placeholder="任务状态" size="small" class="filter-select" clearable>
              <el-option label="待执行" value="pending" />
              <el-option label="执行中" value="running" />
              <el-option label="已完成" value="completed" />
              <el-option label="失败" value="failed" />
            </el-select>
            <el-button type="primary" @click="handleAdd">
              <el-icon><component :is="icons.Plus" /></el-icon>
              新建任务
            </el-button>
          </div>
        </div>
      </template>

      <div v-if="!loading && filteredTasks.length === 0" class="empty-state">
        <el-icon :size="48" class="empty-icon"><component :is="icons.Box" /></el-icon>
        <span>暂无任务</span>
        <el-button size="small" type="primary" @click="handleAdd">新建任务</el-button>
      </div>

      <el-table v-else :data="filteredTasks" stripe border v-loading="loading">
        <el-table-column prop="name" label="任务名称" min-width="180" show-overflow-tooltip />
        <el-table-column prop="project" label="项目" width="140" show-overflow-tooltip />
        <el-table-column prop="browser_type" label="浏览器" width="110">
          <template #default="scope">
            <el-tag size="small" :type="getBrowserTagType(scope.row.browser_type)">
              {{ getBrowserLabel(scope.row.browser_type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="headless" label="模式" width="90">
          <template #default="scope">
            <el-tag size="small" :type="scope.row.headless ? 'info' : 'success'">
              {{ scope.row.headless ? '无头' : '有头' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="case_count" label="用例数" width="90" align="center">
          <template #default="scope">
            <span>{{ (scope.row.case_ids || []).length || scope.row.case_count || 0 }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="scope">
            <el-tag :type="getStatusType(scope.row.status)" size="small">
              {{ getStatusLabel(scope.row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="last_run_status" label="上次结果" width="100">
          <template #default="scope">
            <el-tag v-if="scope.row.last_run_status" :type="getLastRunTagType(scope.row.last_run_status)" size="small">
              {{ scope.row.last_run_status }}
            </el-tag>
            <span v-else class="text-gray">未执行</span>
          </template>
        </el-table-column>
        <el-table-column prop="last_run_time" label="上次执行时间" width="170">
          <template #default="scope">
            <span>{{ scope.row.last_run_time || '-' }}</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="320" class-name="action-cell" fixed="right">
          <template #default="scope">
            <div class="action-btns">
              <el-button
                size="small"
                type="primary"
                :disabled="scope.row.status === 'running'"
                @click="handleExecute(scope.row)"
              >
                <el-icon><component :is="icons.VideoPlay" /></el-icon>
                执行
              </el-button>
              <el-button
                size="small"
                :disabled="!scope.row.last_run_status"
                @click="handleViewResult(scope.row)"
              >
                <el-icon><component :is="icons.View" /></el-icon>
                结果
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
          layout="total, prev, pager, next"
          :total="filteredTasks.length"
          :page-size="10"
          v-model:current-page="currentPage"
        />
      </div>
    </el-card>

    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑UI测试任务' : '新建UI测试任务'"
      width="640px"
      :close-on-click-modal="false"
    >
      <el-form :model="taskForm" label-width="110px" :rules="formRules" ref="formRef">
        <el-form-item label="任务名称" prop="name">
          <el-input v-model="taskForm.name" placeholder="请输入任务名称" maxlength="64" show-word-limit />
        </el-form-item>
        <el-form-item label="项目" prop="project">
          <el-select v-model="taskForm.project" placeholder="请选择项目" filterable allow-create>
            <el-option
              v-for="p in projectOptions"
              :key="p"
              :label="p"
              :value="p"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="描述">
          <el-input
            v-model="taskForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入任务描述（可选）"
            maxlength="255"
            show-word-limit
          />
        </el-form-item>
        <el-form-item label="关联用例" prop="case_ids">
          <el-select
            v-model="taskForm.case_ids"
            multiple
            filterable
            collapse-tags
            collapse-tags-tooltip
            placeholder="请选择要执行的UI用例"
            style="width: 100%"
          >
            <el-option
              v-for="c in caseList"
              :key="c.id"
              :label="c.name"
              :value="c.id"
            >
              <span style="float: left">{{ c.name }}</span>
              <span style="float: right; color: #8492a6; font-size: 12px">{{ c.project || '' }}</span>
            </el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="浏览器类型" prop="browser_type">
          <el-select v-model="taskForm.browser_type" placeholder="请选择浏览器">
            <el-option label="Chrome" value="chrome" />
            <el-option label="Firefox" value="firefox" />
            <el-option label="Edge" value="edge" />
            <el-option label="Safari" value="safari" />
          </el-select>
        </el-form-item>
        <el-form-item label="执行模式" prop="headless">
          <el-radio-group v-model="taskForm.headless">
            <el-radio :value="false">有头模式</el-radio>
            <el-radio :value="true">无头模式</el-radio>
          </el-radio-group>
          <div class="form-tip">
            <el-icon :size="14"><component :is="icons.InfoFilled" /></el-icon>
            <span>无头模式不会显示浏览器窗口，适合CI环境</span>
          </div>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="handleSave">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog
      v-model="executeDialogVisible"
      title="执行UI测试任务"
      width="680px"
      :close-on-click-modal="false"
    >
      <div v-if="executing" class="execute-progress">
        <div class="progress-header">
          <el-icon class="is-loading" :size="20"><component :is="icons.Loading" /></el-icon>
          <span>任务「{{ executingTask?.name }}」正在执行...</span>
        </div>
        <el-progress
          :percentage="executeProgress"
          :status="executeProgress >= 100 ? 'success' : ''"
          :stroke-width="14"
        />
        <div class="progress-log">
          <div v-for="(line, idx in executeLogs" :key="idx" class="log-line">
            <span class="log-time">{{ line.time }}</span>
            <span class="log-msg" :class="line.level">{{ line.message }}</span>
          </div>
        </div>
      </div>

      <div v-else-if="executeResult" class="execute-result">
        <div class="result-summary">
          <el-tag :type="executeResult.success ? 'success' : 'danger'" size="large">
            {{ executeResult.success ? '执行成功' : '执行失败' }}
          </el-tag>
          <span class="summary-item">总用例: {{ executeResult.total ?? 0 }}</span>
          <span class="summary-item pass">通过: {{ executeResult.passed ?? 0 }}</span>
          <span class="summary-item fail">失败: {{ executeResult.failed ?? 0 }}</span>
          <span class="summary-item">耗时: {{ executeResult.duration || '-' }}</span>
        </div>

        <el-divider content-position="left">用例详情</el-divider>
        <el-table :data="executeResult.details || []" size="small" max-height="260">
          <el-table-column prop="name" label="用例名称" show-overflow-tooltip />
          <el-table-column prop="status" label="结果" width="90">
            <template #default="scope">
              <el-tag
                :type="scope.row.status === 'passed' ? 'success' : 'danger'"
                size="small"
              >
                {{ scope.row.status === 'passed' ? '通过' : '失败' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="duration" label="耗时" width="90" />
          <el-table-column prop="message" label="备注" show-overflow-tooltip />
        </el-table>

        <div v-if="executeResult.error_message" class="error-section">
          <div class="section-title">错误信息</div>
          <pre class="error-log">{{ executeResult.error_message }}</pre>
        </div>
      </div>

      <template #footer>
        <el-button @click="handleCloseExecute">{{ executing ? '后台执行' : '关闭' }}</el-button>
      </template>
    </el-dialog>

    <el-dialog
      v-model="resultDialogVisible"
      title="上次执行结果"
      width="620px"
    >
      <div v-if="currentResult" class="result-container">
        <div class="result-summary">
          <div class="summary-item">
            <div class="summary-value">{{ currentResult.total ?? 0 }}</div>
            <div class="summary-label">总用例</div>
          </div>
          <div class="summary-item pass">
            <div class="summary-value">{{ currentResult.passed ?? 0 }}</div>
            <div class="summary-label">通过</div>
          </div>
          <div class="summary-item fail">
            <div class="summary-value">{{ currentResult.failed ?? 0 }}</div>
            <div class="summary-label">失败</div>
          </div>
          <div class="summary-item">
            <div class="summary-value">{{ currentResult.duration || '-' }}</div>
            <div class="summary-label">耗时</div>
          </div>
        </div>

        <el-divider content-position="left">用例详情</el-divider>
        <el-table :data="currentResult.details || []" size="small" max-height="260">
          <el-table-column prop="name" label="用例名称" show-overflow-tooltip />
          <el-table-column prop="status" label="结果" width="90">
            <template #default="scope">
              <el-tag
                :type="scope.row.status === 'passed' ? 'success' : 'danger'"
                size="small"
              >
                {{ scope.row.status === 'passed' ? '通过' : '失败' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="duration" label="耗时" width="90" />
          <el-table-column prop="message" label="备注" show-overflow-tooltip />
        </el-table>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import * as icons from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const loading = ref(false)
const saving = ref(false)
const searchKeyword = ref('')
const filterStatus = ref('')
const currentPage = ref(1)

const tasks = ref([])
const caseList = ref([])

const dialogVisible = ref(false)
const isEdit = ref(false)
const editingTask = ref(null)
const formRef = ref(null)

const executeDialogVisible = ref(false)
const executing = ref(false)
const executeProgress = ref(0)
const executeLogs = ref([])
const executeResult = ref(null)
const executingTask = ref(null)

const resultDialogVisible = ref(false)
const currentResult = ref(null)

const projectOptions = computed(() => {
  const set = new Set()
  tasks.value.forEach(t => t.project && set.add(t.project))
  caseList.value.forEach(c => c.project && set.add(c.project))
  return Array.from(set)
})

const defaultForm = () => ({
  name: '',
  project: '',
  description: '',
  case_ids: [],
  browser_type: 'chrome',
  headless: true
})

const taskForm = ref(defaultForm())

const formRules = {
  name: [{ required: true, message: '请输入任务名称', trigger: 'blur' }],
  project: [{ required: true, message: '请选择项目', trigger: 'change' }],
  case_ids: [{ required: true, type: 'array', min: 1, message: '请至少选择一个用例', trigger: 'change' }],
  browser_type: [{ required: true, message: '请选择浏览器类型', trigger: 'change' }]
}

const filteredTasks = computed(() => {
  return tasks.value.filter(t => {
    const matchKeyword =
      !searchKeyword.value ||
      (t.name && t.name.toLowerCase().includes(searchKeyword.value.toLowerCase())) ||
      (t.project && t.project.toLowerCase().includes(searchKeyword.value.toLowerCase()))
    const matchStatus = !filterStatus.value || t.status === filterStatus.value
    return matchKeyword && matchStatus
  })
})

function getStatusType(status) {
  const map = { pending: 'info', running: 'warning', completed: 'success', failed: 'danger' }
  return map[status] || 'info'
}

function getStatusLabel(status) {
  const map = { pending: '待执行', running: '执行中', completed: '已完成', failed: '失败' }
  return map[status] || status
}

function getLastRunTagType(lastRunStatus) {
  if (!lastRunStatus) return 'info'
  const s = lastRunStatus.toLowerCase()
  if (s.includes('成功') || s === 'passed' || s === 'success') return 'success'
  if (s.includes('失败') || s === 'failed' || s === 'error') return 'danger'
  return 'info'
}

function getBrowserTagType(browser) {
  const map = { chrome: 'primary', firefox: 'warning', edge: 'success', safari: 'info' }
  return map[browser] || ''
}

function getBrowserLabel(browser) {
  const map = { chrome: 'Chrome', firefox: 'Firefox', edge: 'Edge', safari: 'Safari' }
  return map[browser] || browser || '-'
}

async function loadTasks() {
  loading.value = true
  try {
    const response = await fetch('/api/v1/ui/tasks')
    const data = await response.json()
    tasks.value = data.tasks || data.data || data.items || []
  } catch (error) {
    console.error('加载UI测试任务失败:', error)
    ElMessage.error('加载任务列表失败')
  } finally {
    loading.value = false
  }
}

async function loadCases() {
  try {
    const response = await fetch('/api/v1/ui/cases')
    const data = await response.json()
    caseList.value = data.cases || data.data || data.items || []
  } catch (error) {
    console.error('加载UI用例列表失败:', error)
  }
}

function handleAdd() {
  isEdit.value = false
  editingTask.value = null
  taskForm.value = defaultForm()
  dialogVisible.value = true
}

function handleEdit(row) {
  isEdit.value = true
  editingTask.value = row
  taskForm.value = {
    name: row.name || '',
    project: row.project || '',
    description: row.description || '',
    case_ids: row.case_ids ? [...row.case_ids] : [],
    browser_type: row.browser_type || 'chrome',
    headless: row.headless !== false
  }
  dialogVisible.value = true
}

function handleSave() {
  if (!formRef.value) return
  formRef.value.validate(async (valid) => {
    if (!valid) return
    saving.value = true
    try {
      const url = isEdit.value
        ? `/api/v1/ui/tasks/${editingTask.value.id}`
        : '/api/v1/ui/tasks'
      const method = isEdit.value ? 'PUT' : 'POST'
      const response = await fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(taskForm.value)
      })
      const data = await response.json()
      if (data.success !== false) {
        ElMessage.success(isEdit.value ? '更新成功' : '创建成功')
        dialogVisible.value = false
        loadTasks()
      } else {
        ElMessage.error(data.message || '保存失败')
      }
    } catch (error) {
      console.error('保存任务失败:', error)
      ElMessage.error('保存失败')
    } finally {
      saving.value = false
    }
  })
}

function handleDelete(row) {
  ElMessageBox.confirm(`确定要删除任务「${row.name}」吗？此操作不可恢复。`, '删除确认', {
    confirmButtonText: '删除',
    cancelButtonText: '取消',
    type: 'warning'
  })
    .then(async () => {
      try {
        const response = await fetch(`/api/v1/ui/tasks/${row.id}`, {
          method: 'DELETE'
        })
        const data = await response.json()
        if (data.success !== false) {
          ElMessage.success('删除成功')
          loadTasks()
        } else {
          ElMessage.error(data.message || '删除失败')
        }
      } catch (error) {
        console.error('删除任务失败:', error)
        ElMessage.error('删除失败')
      }
    })
    .catch(() => {})
}

function handleExecute(row) {
  executingTask.value = row
  executeResult.value = null
  executeLogs.value = []
  executeProgress.value = 0
  executing.value = true
  executeDialogVisible.value = true

  addLog('info', `开始执行任务「${row.name}」`)

  fetch(`/api/v1/ui/tasks/${row.id}/execute`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' }
  })
    .then(async (response) => {
      const reader = response.body ? response.body.getReader() : null
      if (!reader) {
        return response.json()
      }

      const decoder = new TextDecoder()
      let buffer = ''
      while (true) {
        const { done, value } = await reader.read()
        if (done) break
        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split(/\r?\n/)
        buffer = lines.pop() || ''
        for (const line of lines) {
          if (!line.trim()) continue
          try {
            const evt = JSON.parse(line)
            if (evt.progress !== undefined) {
              executeProgress.value = evt.progress
            }
            if (evt.log) {
              addLog(evt.level || 'info', evt.log)
            }
            if (evt.result) {
              executeResult.value = evt.result
            }
          } catch {
            addLog('info', line)
          }
        }
      }
      if (buffer.trim()) {
        try {
          const evt = JSON.parse(buffer)
          if (evt.result) executeResult.value = evt.result
        } catch {
          addLog('info', buffer)
        }
      }
      return null
    })
    .then((finalData) => {
      if (finalData && !executeResult.value) {
        executeResult.value = finalData
      }
      executeProgress.value = 100
      executing.value = false
      addLog(executeResult.value?.success === false ? 'error' : 'success', '任务执行完成')
      loadTasks()
    })
    .catch((error) => {
      console.error('执行任务失败:', error)
      executing.value = false
      executeProgress.value = 100
      executeResult.value = { success: false, error_message: error.message || '请求失败' }
      addLog('error', '执行任务失败')
      loadTasks()
    })
}

function addLog(level, message) {
  const now = new Date()
  const time = now.toLocaleTimeString('zh-CN', { hour12: false })
  executeLogs.value.push({ time, level, message })
}

function handleCloseExecute() {
  executeDialogVisible.value = false
}

function handleViewResult(row) {
  if (!row.last_run_status && !row.last_run_result) {
    ElMessage.warning('该任务暂无执行结果')
    return
  }
  currentResult.value = row.last_run_result || {
    total: row.case_count || 0,
    passed: row.last_run_status === '成功' || row.last_run_status === 'success' ? (row.case_count || 0) : 0,
    failed: row.last_run_status === '失败' || row.last_run_status === 'failed' ? (row.case_count || 0) : 0,
    duration: row.last_run_duration || '-',
    details: []
  }
  resultDialogVisible.value = true
}

onMounted(() => {
  loadTasks()
  loadCases()
})
</script>

<style scoped>
.ui-tasks {
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
  flex-wrap: wrap;
  gap: 12px;
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
  width: 240px;
}

.filter-select {
  width: 130px;
}

.text-gray {
  color: #9ca3af;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px;
  color: #9ca3af;
  gap: 12px;
}

.empty-icon {
  color: #c0c4cc;
}

.action-btns {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.form-tip {
  display: flex;
  align-items: center;
  gap: 4px;
  margin-top: 6px;
  font-size: 12px;
  color: #6b7280;
}

.pagination-wrapper {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}

.execute-progress {
  padding: 8px 0;
}

.progress-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
  font-weight: 500;
  color: #374151;
}

.progress-log {
  margin-top: 16px;
  background: #1f2937;
  border-radius: 6px;
  padding: 12px;
  max-height: 260px;
  overflow-y: auto;
  font-family: Consolas, Monaco, monospace;
  font-size: 12px;
}

.log-line {
  margin-bottom: 4px;
  display: flex;
  gap: 8px;
}

.log-time {
  color: #9ca3af;
}

.log-msg {
  color: #e5e7eb;
}

.log-msg.success {
  color: #10b981;
}

.log-msg.error {
  color: #ef4444;
}

.log-msg.warning {
  color: #f59e0b;
}

.execute-result,
.result-container {
  padding: 8px 0;
}

.result-summary {
  display: flex;
  align-items: center;
  gap: 24px;
  margin-bottom: 8px;
  flex-wrap: wrap;
}

.summary-item {
  font-size: 14px;
  color: #6b7280;
}

.summary-item.pass {
  color: #67c23a;
  font-weight: 600;
}

.summary-item.fail {
  color: #f56c6c;
  font-weight: 600;
}

.summary-value {
  font-size: 28px;
  font-weight: 600;
  color: #1f2937;
}

.summary-item.pass .summary-value {
  color: #67c23a;
}

.summary-item.fail .summary-value {
  color: #f56c6c;
}

.summary-label {
  font-size: 13px;
  color: #6b7280;
  margin-top: 4px;
}

.error-section {
  margin-top: 16px;
}

.section-title {
  font-weight: 600;
  color: #374151;
  margin-bottom: 8px;
}

.error-log {
  background: #1f2937;
  color: #ef4444;
  padding: 12px;
  border-radius: 4px;
  font-size: 12px;
  max-height: 200px;
  overflow-y: auto;
  white-space: pre-wrap;
  word-break: break-all;
}
</style>
