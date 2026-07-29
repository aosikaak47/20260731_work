<template>
  <div class="ui-cases">
    <div class="page-header">
      <h2>UI用例编排</h2>
      <p class="page-desc">拖拽式编排UI自动化测试场景</p>
    </div>

    <div class="main-toolbar">
      <div class="toolbar-left">
        <el-input
          v-model="searchKeyword"
          placeholder="搜索场景名称..."
          clearable
          style="width: 260px;"
        >
          <template #prefix>
            <el-icon><component :is="icons.Search" /></el-icon>
          </template>
        </el-input>
        <el-select
          v-model="filterProject"
          placeholder="选择项目"
          clearable
          style="width: 180px;"
        >
          <el-option
            v-for="p in projectOptions"
            :key="p"
            :label="p"
            :value="p"
          />
        </el-select>
      </div>
      <div class="toolbar-right">
        <el-button @click="loadCases">
          <el-icon><component :is="icons.Refresh" /></el-icon>
          刷新
        </el-button>
        <el-button type="primary" @click="handleAdd">
          <el-icon><component :is="icons.Plus" /></el-icon>
          新增场景
        </el-button>
      </div>
    </div>

    <el-table
      v-loading="loading"
      :data="filteredCases"
      stripe
      style="width: 100%;"
      @row-dblclick="handleEdit"
    >
      <el-table-column type="index" label="序号" width="60" />
      <el-table-column prop="name" label="场景名称" min-width="160">
        <template #default="{ row }">
          <span class="case-name">{{ row.name }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="project" label="所属项目" min-width="120">
        <template #default="{ row }">
          <el-tag size="small" type="info">{{ row.project || '-' }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="url" label="目标URL" min-width="200" show-overflow-tooltip>
        <template #default="{ row }">
          <span class="url-text">{{ row.url || '-' }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="description" label="描述" min-width="180" show-overflow-tooltip>
        <template #default="{ row }">
          {{ row.description || '-' }}
        </template>
      </el-table-column>
      <el-table-column label="步骤数" width="90" align="center">
        <template #default="{ row }">
          <el-badge :value="(row.steps || []).length" type="primary">
            <el-icon :size="16" color="#6366f1"><component :is="icons.List" /></el-icon>
          </el-badge>
        </template>
      </el-table-column>
      <el-table-column prop="updated_at" label="更新时间" width="170">
        <template #default="{ row }">
          <span class="time-text">{{ formatTime(row.updated_at) }}</span>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="240" fixed="right">
        <template #default="{ row }">
          <el-button type="success" size="small" @click="handleRun(row)">
            <el-icon><component :is="icons.VideoPlay" /></el-icon>
            执行
          </el-button>
          <el-button size="small" @click="handleEdit(row)">
            <el-icon><component :is="icons.Edit" /></el-icon>
            编辑
          </el-button>
          <el-button type="danger" size="small" @click="handleDelete(row)">
            <el-icon><component :is="icons.Delete" /></el-icon>
            删除
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <div class="pagination-wrapper">
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.pageSize"
        :page-sizes="[10, 20, 50]"
        :total="paginationTotal"
        layout="total, sizes, prev, pager, next, jumper"
        background
      />
    </div>

    <el-dialog
      v-model="dialogVisible"
      :title="isEditing ? '编辑场景' : '新增场景'"
      width="900px"
      :close-on-click-modal="false"
      top="5vh"
      @open="handleDialogOpen"
    >
      <div class="dialog-content">
        <el-form
          ref="formRef"
          :model="form"
          :rules="formRules"
          label-width="100px"
          class="case-form"
        >
          <el-row :gutter="16">
            <el-col :span="12">
              <el-form-item label="场景名称" prop="name">
                <el-input v-model="form.name" placeholder="请输入场景名称" maxlength="50" show-word-limit />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="所属项目" prop="project">
                <el-input v-model="form.project" placeholder="请输入项目名称" />
              </el-form-item>
            </el-col>
          </el-row>
          <el-row :gutter="16">
            <el-col :span="24">
              <el-form-item label="目标URL" prop="url">
                <el-input v-model="form.url" placeholder="https://example.com" />
              </el-form-item>
            </el-col>
          </el-row>
          <el-row :gutter="16">
            <el-col :span="24">
              <el-form-item label="场景描述">
                <el-input
                  v-model="form.description"
                  type="textarea"
                  :rows="2"
                  placeholder="请输入场景描述..."
                  maxlength="200"
                  show-word-limit
                />
              </el-form-item>
            </el-col>
          </el-row>
        </el-form>

        <div class="orchestration-section">
          <div class="section-header">
            <span class="section-title">步骤编排</span>
            <div class="section-actions">
              <el-button size="small" @click="handleAddStep('navigate')">
                <el-icon><component :is="icons.Position" /></el-icon>
                导航
              </el-button>
              <el-button size="small" @click="handleAddStep('click')">
                <el-icon><component :is="icons.Mouse" /></el-icon>
                点击
              </el-button>
              <el-button size="small" @click="handleAddStep('input')">
                <el-icon><component :is="icons.Operation" /></el-icon>
                输入
              </el-button>
              <el-button size="small" @click="handleAddStep('select')">
                <el-icon><component :is="icons.CaretBottom" /></el-icon>
                选择
              </el-button>
              <el-button size="small" @click="handleAddStep('wait')">
                <el-icon><component :is="icons.Clock" /></el-icon>
                等待
              </el-button>
              <el-button size="small" @click="handleAddStep('assert')">
                <el-icon><component :is="icons.CircleCheck" /></el-icon>
                断言
              </el-button>
              <el-button size="small" @click="handleAddStep('screenshot')">
                <el-icon><component :is="icons.Camera" /></el-icon>
                截图
              </el-button>
              <el-button size="small" @click="handleAddStep('scroll')">
                <el-icon><component :is="icons.ArrowDown" /></el-icon>
                滚动
              </el-button>
              <el-button size="small" @click="handleAddStep('switch')">
                <el-icon><component :is="icons.Share" /></el-icon>
                条件
              </el-button>
            </div>
          </div>

          <div class="orchestration-body">
            <div class="component-library">
              <div class="library-title">操作组件库</div>
              <div class="component-grid">
                <div
                  v-for="component in componentTypes"
                  :key="component.type"
                  class="component-item"
                  draggable="true"
                  @dragstart="handleDragStart(component)"
                >
                  <el-icon :size="16"><component :is="component.icon" /></el-icon>
                  <span>{{ component.name }}</span>
                </div>
              </div>
            </div>

            <div class="flow-canvas" @drop="handleDrop" @dragover.prevent>
              <div v-if="form.steps.length === 0" class="empty-canvas">
                <el-icon :size="48" class="empty-icon"><component :is="icons.Box" /></el-icon>
                <span>拖拽左侧组件到此处，或点击上方按钮添加步骤</span>
              </div>

              <div v-else class="steps-list">
                <div
                  v-for="(step, index) in form.steps"
                  :key="step.id"
                  class="step-card"
                  :class="{ 'step-card-active': activeStepId === step.id }"
                  @click="activeStepId = step.id"
                >
                  <div class="step-header">
                    <span class="step-num">{{ index + 1 }}</span>
                    <el-icon :size="16"><component :is="getStepIcon(step.type)" /></el-icon>
                    <span class="step-name">{{ step.name }}</span>
                    <div class="step-actions">
                      <el-button
                        size="small"
                        text
                        :disabled="index === 0"
                        @click.stop="moveStep(index, -1)"
                      >
                        <el-icon><component :is="icons.ArrowUp" /></el-icon>
                      </el-button>
                      <el-button
                        size="small"
                        text
                        :disabled="index === form.steps.length - 1"
                        @click.stop="moveStep(index, 1)"
                      >
                        <el-icon><component :is="icons.ArrowDown" /></el-icon>
                      </el-button>
                      <el-button size="small" text @click.stop="handleDuplicateStep(step)">
                        <el-icon><component :is="icons.CopyDocument" /></el-icon>
                      </el-button>
                      <el-button size="small" text type="danger" @click.stop="handleRemoveStep(step.id)">
                        <el-icon><component :is="icons.Close" /></el-icon>
                      </el-button>
                    </div>
                  </div>
                  <div class="step-body">
                    <el-form label-width="80px" :model="step" size="small">
                      <el-row :gutter="12">
                        <el-col :span="12">
                          <el-form-item label="元素">
                            <el-input
                              v-model="step.element"
                              :placeholder="getElementPlaceholder(step.type)"
                            />
                          </el-form-item>
                        </el-col>
                        <el-col :span="12">
                          <el-form-item label="参数">
                            <el-input
                              v-model="step.params"
                              :placeholder="getParamsPlaceholder(step.type)"
                            />
                          </el-form-item>
                        </el-col>
                      </el-row>
                      <el-row :gutter="12">
                        <el-col :span="8">
                          <el-form-item label="延时">
                            <el-input-number v-model="step.delay" :min="0" :max="60" :step="0.5" style="width: 100%;" />
                          </el-form-item>
                        </el-col>
                        <el-col :span="8">
                          <el-form-item label="重试">
                            <el-input-number v-model="step.retry" :min="0" :max="5" style="width: 100%;" />
                          </el-form-item>
                        </el-col>
                        <el-col :span="8">
                          <el-form-item label="超时">
                            <el-input-number v-model="step.timeout" :min="1" :max="300" style="width: 100%;" />
                          </el-form-item>
                        </el-col>
                      </el-row>
                    </el-form>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" :loading="submitting" @click="handleSubmit">
            {{ isEditing ? '保存修改' : '创建场景' }}
          </el-button>
        </div>
      </template>
    </el-dialog>

    <el-dialog
      v-model="executeDialogVisible"
      title="执行场景"
      width="700px"
      :close-on-click-modal="false"
    >
      <div class="execute-content">
        <div v-if="executing" class="executing-state">
          <el-icon :size="32" class="is-loading" color="#6366f1"><component :is="icons.Loading" /></el-icon>
          <p>正在执行场景 "{{ currentCase?.name }}" ...</p>
          <p class="executing-tip">请稍候，执行过程中请勿关闭此窗口</p>
        </div>

        <div v-else-if="executeResult" class="execute-result">
          <div class="result-header">
            <el-alert
              :title="executeResult.success ? '执行成功' : '执行失败'"
              :type="executeResult.success ? 'success' : 'error'"
              :closable="false"
              show-icon
            />
            <div class="result-stats">
              <span>总步骤: {{ executeResult.total_steps || 0 }}</span>
              <span>通过: <span class="stat-success">{{ executeResult.passed || 0 }}</span></span>
              <span>失败: <span class="stat-fail">{{ executeResult.failed || 0 }}</span></span>
              <span>耗时: {{ executeResult.duration || 0 }}s</span>
            </div>
          </div>

          <div class="log-panel">
            <div class="log-title">执行日志</div>
            <div class="log-content">
              <div
                v-for="(log, idx) in executeResult.logs || []"
                :key="idx"
                class="log-item"
                :class="log.level"
              >
                <span class="log-step">[{{ log.step || idx + 1 }}]</span>
                <span class="log-message">{{ log.message }}</span>
                <span v-if="log.duration" class="log-duration">{{ log.duration }}s</span>
                <el-icon
                  v-if="log.level === 'success'"
                  :size="14"
                  class="log-icon"
                ><component :is="icons.CircleCheck" /></el-icon>
                <el-icon
                  v-else-if="log.level === 'error'"
                  :size="14"
                  class="log-icon"
                ><component :is="icons.CircleClose" /></el-icon>
                <el-icon
                  v-else
                  :size="14"
                  class="log-icon"
                ><component :is="icons.InfoFilled" /></el-icon>
              </div>
            </div>
          </div>

          <div v-if="executeResult.screenshot" class="screenshot-panel">
            <div class="log-title">截图预览</div>
            <img :src="executeResult.screenshot" alt="screenshot" class="screenshot-img" />
          </div>
        </div>
      </div>

      <template #footer>
        <el-button @click="executeDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, reactive, markRaw } from 'vue'
import * as icons from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const API_BASE = '/api/v1/ui/cases'

const loading = ref(false)
const submitting = ref(false)
const searchKeyword = ref('')
const filterProject = ref('')
const projectOptions = ref([])
const cases = ref([])

const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0
})

const filteredAllCases = computed(() => {
  let result = cases.value
  if (filterProject.value) {
    result = result.filter(c => c.project === filterProject.value)
  }
  if (searchKeyword.value) {
    const kw = searchKeyword.value.toLowerCase()
    result = result.filter(c =>
      (c.name || '').toLowerCase().includes(kw) ||
      (c.url || '').toLowerCase().includes(kw) ||
      (c.description || '').toLowerCase().includes(kw)
    )
  }
  return result
})

const paginationTotal = computed(() => filteredAllCases.value.length)

const filteredCases = computed(() => {
  const start = (pagination.page - 1) * pagination.pageSize
  return filteredAllCases.value.slice(start, start + pagination.pageSize)
})

const dialogVisible = ref(false)
const isEditing = ref(false)
const formRef = ref(null)
const activeStepId = ref(null)

const defaultForm = () => ({
  id: null,
  name: '',
  project: '',
  url: '',
  description: '',
  steps: []
})

const form = ref(defaultForm())

const formRules = {
  name: [{ required: true, message: '请输入场景名称', trigger: 'blur' }],
  project: [{ required: true, message: '请输入项目名称', trigger: 'blur' }],
  url: [
    { required: true, message: '请输入目标URL', trigger: 'blur' },
    { type: 'url', message: '请输入合法的URL', trigger: 'blur' }
  ]
}

const executeDialogVisible = ref(false)
const executing = ref(false)
const executeResult = ref(null)
const currentCase = ref(null)

const componentTypes = [
  { type: 'navigate', name: '导航', icon: markRaw(icons.Position) },
  { type: 'click', name: '点击', icon: markRaw(icons.Mouse) },
  { type: 'input', name: '输入', icon: markRaw(icons.Operation) },
  { type: 'select', name: '选择', icon: markRaw(icons.CaretBottom) },
  { type: 'wait', name: '等待', icon: markRaw(icons.Clock) },
  { type: 'assert', name: '断言', icon: markRaw(icons.CircleCheck) },
  { type: 'screenshot', name: '截图', icon: markRaw(icons.Camera) },
  { type: 'scroll', name: '滚动', icon: markRaw(icons.ArrowDown) },
  { type: 'switch', name: '条件判断', icon: markRaw(icons.Share) }
]

const draggedComponent = ref(null)

const getStepIcon = (type) => {
  const c = componentTypes.value.find(c => c.type === type)
  return c ? c.icon : icons.CircleFilled
}

const getElementPlaceholder = (type) => {
  const map = {
    navigate: '页面URL',
    click: 'CSS选择器或元素ID',
    input: 'CSS选择器或元素ID',
    select: 'CSS选择器或元素ID',
    wait: '等待条件(元素/时间)',
    assert: '断言目标(元素/文本)',
    screenshot: '保存路径',
    scroll: '滚动目标元素',
    switch: '判断条件'
  }
  return map[type] || '元素选择器'
}

const getParamsPlaceholder = (type) => {
  const map = {
    navigate: 'https://example.com',
    click: '点击次数(默认1)',
    input: '输入的文本内容',
    select: '选择的值或索引',
    wait: '等待时长(秒)',
    assert: '预期值或文本',
    screenshot: '文件名(可选)',
    scroll: '滚动方向/像素',
    switch: '条件表达式'
  }
  return map[type] || '参数值'
}

const createStep = (type) => {
  const component = componentTypes.value.find(c => c.type === type)
  return {
    id: Date.now() + Math.random(),
    type,
    name: component ? component.name : '步骤',
    element: '',
    params: '',
    delay: 0,
    retry: 0,
    timeout: 30
  }
}

const loadCases = async () => {
  loading.value = true
  try {
    const res = await fetch(API_BASE)
    if (!res.ok) throw new Error('加载失败')
    const data = await res.json()
    const rawCases = data.cases || data.data || data || []
    cases.value = rawCases.map(c => ({
      ...c,
      project: c.project || c.project_id || ''
    }))
    const projects = new Set()
    cases.value.forEach(c => { if (c.project) projects.add(c.project) })
    projectOptions.value = Array.from(projects)
  } catch (e) {
    ElMessage.error('加载场景列表失败: ' + (e.message || e))
    cases.value = []
  } finally {
    loading.value = false
  }
}

const handleAdd = () => {
  isEditing.value = false
  form.value = defaultForm()
  dialogVisible.value = true
}

const handleEdit = (row) => {
  isEditing.value = true
  form.value = {
    id: row.id,
    name: row.name,
    project: row.project,
    url: row.url,
    description: row.description || '',
    steps: JSON.parse(JSON.stringify(row.steps || []))
  }
  dialogVisible.value = true
}

const handleDialogOpen = () => {
  activeStepId.value = form.value.steps.length > 0 ? form.value.steps[0].id : null
}

const handleDelete = (row) => {
  ElMessageBox.confirm(
    `确定要删除场景「${row.name}」吗？此操作不可恢复。`,
    '删除确认',
    {
      confirmButtonText: '确定删除',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      const res = await fetch(`${API_BASE}/${row.id}`, { method: 'DELETE' })
      if (!res.ok) throw new Error('删除失败')
      ElMessage.success('删除成功')
      loadCases()
    } catch (e) {
      ElMessage.error('删除失败')
    }
  }).catch(() => {})
}

const handleRun = async (row) => {
  currentCase.value = row
  executeResult.value = null
  executing.value = true
  executeDialogVisible.value = true

  try {
    const res = await fetch(`${API_BASE}/${row.id}/execute`, { method: 'POST' })
    if (!res.ok) throw new Error('执行失败')
    const data = await res.json()
    executeResult.value = data.data || data
  } catch (e) {
    executeResult.value = {
      success: false,
      logs: [
        { level: 'error', message: '执行请求失败：' + e.message, step: 0 }
      ],
      total_steps: 0,
      passed: 0,
      failed: 0,
      duration: 0
    }
  } finally {
    executing.value = false
  }
}

const handleDragStart = (component) => {
  draggedComponent.value = component
}

const handleDrop = () => {
  if (draggedComponent.value) {
    form.value.steps.push(createStep(draggedComponent.value.type))
    draggedComponent.value = null
  }
}

const handleAddStep = (type) => {
  form.value.steps.push(createStep(type))
}

const handleRemoveStep = (id) => {
  form.value.steps = form.value.steps.filter(s => s.id !== id)
  if (activeStepId.value === id) {
    activeStepId.value = form.value.steps.length > 0 ? form.value.steps[0].id : null
  }
}

const handleDuplicateStep = (step) => {
  const newStep = JSON.parse(JSON.stringify(step))
  newStep.id = Date.now() + Math.random()
  const idx = form.value.steps.findIndex(s => s.id === step.id)
  form.value.steps.splice(idx + 1, 0, newStep)
}

const moveStep = (index, direction) => {
  const newIndex = index + direction
  if (newIndex < 0 || newIndex >= form.value.steps.length) return
  const temp = form.value.steps[index]
  form.value.steps.splice(index, 1)
  form.value.steps.splice(newIndex, 0, temp)
}

const handleSubmit = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (!valid) {
      ElMessage.warning('请检查表单填写')
      return
    }

    submitting.value = true
    try {
      const payload = {
        name: form.value.name,
        project_id: form.value.project,
        url: form.value.url,
        description: form.value.description,
        steps: form.value.steps.map(s => ({
          type: s.type,
          name: s.name,
          element: s.element,
          params: s.params,
          delay: s.delay,
          retry: s.retry,
          timeout: s.timeout
        }))
      }

      if (isEditing.value) {
        const res = await fetch(`${API_BASE}/${form.value.id}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        })
        if (!res.ok) throw new Error('保存失败')
        ElMessage.success('更新成功')
      } else {
        const res = await fetch(API_BASE, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        })
        if (!res.ok) throw new Error('创建失败')
        ElMessage.success('创建成功')
      }

      dialogVisible.value = false
      loadCases()
    } catch (e) {
      ElMessage.error(isEditing.value ? '保存失败' : '创建失败')
    } finally {
      submitting.value = false
    }
  })
}

const formatTime = (t) => {
  if (!t) return '-'
  const d = new Date(t)
  if (isNaN(d.getTime())) return t
  const pad = (n) => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`
}

onMounted(() => {
  loadCases()
})
</script>

<style scoped>
.ui-cases {
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

.main-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  flex-wrap: wrap;
  gap: 12px;
}

.toolbar-left {
  display: flex;
  gap: 12px;
}

.toolbar-right {
  display: flex;
  gap: 8px;
}

.pagination-wrapper {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}

.case-name {
  font-weight: 500;
  color: #1f2937;
}

.url-text {
  font-family: 'Monaco', 'Menlo', monospace;
  font-size: 12px;
  color: #6366f1;
}

.time-text {
  color: #6b7280;
  font-size: 13px;
}

.dialog-content {
  max-height: 70vh;
  overflow-y: auto;
}

.case-form {
  margin-bottom: 16px;
}

.orchestration-section {
  border-top: 1px solid #e5e7eb;
  padding-top: 16px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  flex-wrap: wrap;
  gap: 8px;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
}

.section-actions {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.orchestration-body {
  display: grid;
  grid-template-columns: 160px 1fr;
  gap: 16px;
}

.component-library {
  background-color: #f9fafb;
  border-radius: 8px;
  padding: 12px;
}

.library-title {
  font-size: 13px;
  font-weight: 600;
  color: #374151;
  margin-bottom: 10px;
}

.component-grid {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.component-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 10px;
  background-color: #fff;
  border-radius: 6px;
  cursor: grab;
  font-size: 13px;
  transition: all 0.15s;
  border: 1px solid transparent;
}

.component-item:hover {
  border-color: #6366f1;
  background-color: #f5f3ff;
}

.flow-canvas {
  min-height: 300px;
  border: 2px dashed #d1d5db;
  border-radius: 8px;
  padding: 12px;
  background-color: #fafafa;
}

.empty-canvas {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 240px;
  color: #9ca3af;
  gap: 12px;
}

.empty-icon {
  color: #c0c4cc;
}

.steps-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.step-card {
  background-color: #fff;
  border-radius: 8px;
  border: 2px solid #e5e7eb;
  transition: border-color 0.2s;
}

.step-card:hover {
  border-color: #a5b4fc;
}

.step-card-active {
  border-color: #6366f1;
}

.step-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background-color: #f9fafb;
  border-radius: 6px 6px 0 0;
  border-bottom: 1px solid #e5e7eb;
}

.step-num {
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background-color: #6366f1;
  color: white;
  font-size: 11px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.step-name {
  flex: 1;
  font-weight: 500;
  font-size: 14px;
}

.step-actions {
  display: flex;
  gap: 2px;
}

.step-body {
  padding: 10px 12px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}

.execute-content {
  min-height: 200px;
}

.executing-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 0;
  color: #6b7280;
  gap: 12px;
}

.executing-state p {
  margin: 0;
}

.executing-tip {
  font-size: 13px;
  color: #9ca3af;
}

.execute-result {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.result-header {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.result-stats {
  display: flex;
  gap: 16px;
  font-size: 13px;
  color: #6b7280;
}

.stat-success {
  color: #10b981;
  font-weight: 600;
}

.stat-fail {
  color: #ef4444;
  font-weight: 600;
}

.log-panel {
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  overflow: hidden;
}

.log-title {
  padding: 8px 12px;
  background-color: #f3f4f6;
  font-size: 13px;
  font-weight: 600;
  color: #374151;
}

.log-content {
  max-height: 260px;
  overflow-y: auto;
  padding: 8px 12px;
  background-color: #1e1e2e;
  font-family: 'Monaco', 'Menlo', monospace;
  font-size: 12px;
}

.log-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 4px 0;
  color: #d1d5db;
  word-break: break-all;
}

.log-item.info {
  color: #93c5fd;
}

.log-item.success {
  color: #6ee7b7;
}

.log-item.error {
  color: #fca5a5;
}

.log-step {
  color: #9ca3af;
}

.log-duration {
  margin-left: auto;
  color: #9ca3af;
  font-size: 11px;
}

.log-icon {
  flex-shrink: 0;
}

.screenshot-panel {
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  overflow: hidden;
}

.screenshot-img {
  width: 100%;
  max-height: 300px;
  object-fit: contain;
  background-color: #f9fafb;
}
</style>
