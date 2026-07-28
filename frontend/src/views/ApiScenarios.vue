<template>
  <div class="api-scenarios">
    <div class="page-header">
      <div class="header-left">
        <h2>业务场景编排</h2>
        <p class="page-desc">拖拽式编排接口业务场景，支持多接口串联</p>
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
    
    <div class="scenario-container">
      <div class="left-panel">
        <el-card class="api-library-card">
          <template #header>
            <span class="card-title">接口用例库</span>
            <el-input 
              v-model="apiSearch" 
              placeholder="搜索接口..." 
              size="small"
              class="api-search"
            >
              <template #prefix>
                <el-icon><component :is="icons.Search" /></el-icon>
              </template>
            </el-input>
          </template>
          
          <div class="api-list">
            <div 
              v-for="api in filteredApiLibrary" 
              :key="api.id" 
              class="api-item"
              draggable="true"
              @dragstart="handleDragStart(api)"
            >
              <el-tag :type="getMethodType(api.method)" size="small">{{ api.method }}</el-tag>
              <span>{{ api.name }}</span>
            </div>
          </div>
        </el-card>
        
        <el-card class="scenario-list-card">
          <template #header>
            <span class="card-title">场景列表</span>
            <div class="scenario-actions">
              <el-button size="small" type="primary" @click="handleAddScenario">
                <el-icon><component :is="icons.Plus" /></el-icon>
                新建场景
              </el-button>
              <el-button size="small" @click="handleEditScenario(selectedScenario)" :disabled="!selectedScenario">
                <el-icon><component :is="icons.Edit" /></el-icon>
                编辑
              </el-button>
              <el-button size="small" @click="handleDeleteScenario" :disabled="!selectedScenario">
                <el-icon><component :is="icons.Delete" /></el-icon>
                删除
              </el-button>
            </div>
          </template>
          
          <div class="scenario-list">
            <div 
              v-for="scenario in scenarios" 
              :key="scenario.id" 
              class="scenario-item"
              :class="{ active: selectedScenario?.id === scenario.id }"
              @click="handleSelectScenario(scenario)"
            >
              <span class="scenario-name">{{ scenario.name }}</span>
              <el-tag :type="scenario.status === '已启用' ? 'success' : 'info'" size="small">{{ scenario.status }}</el-tag>
              <el-icon class="edit-icon" @click.stop="handleEditScenario(scenario)"><component :is="icons.Edit" /></el-icon>
            </div>
          </div>
        </el-card>
      </div>
      
      <div class="center-panel">
        <el-card class="canvas-card">
          <template #header>
            <div class="card-header">
              <span class="card-title">流程画布</span>
              <div class="canvas-actions">
                <el-button size="small" @click="handleAddStep">
                  <el-icon><component :is="icons.Plus" /></el-icon>
                  添加步骤
                </el-button>
                <el-button size="small" @click="handleClear">
                  <el-icon><component :is="icons.Delete" /></el-icon>
                  清空
                </el-button>
                <el-button size="small" @click="handleMoveUp" :disabled="!selectedStep || steps.indexOf(selectedStep) === 0">
                  <el-icon><component :is="icons.Top" /></el-icon>
                  上移
                </el-button>
                <el-button size="small" @click="handleMoveDown" :disabled="!selectedStep || steps.indexOf(selectedStep) === steps.length - 1">
                  <el-icon><component :is="icons.Bottom" /></el-icon>
                  下移
                </el-button>
              </div>
            </div>
          </template>
          
          <div class="canvas" @drop="handleDrop" @dragover.prevent>
            <div v-if="steps.length === 0" class="empty-canvas">
              <el-icon :size="48" class="empty-icon"><component :is="icons.Box" /></el-icon>
              <span>拖拽左侧接口到此处，或点击添加步骤</span>
            </div>
            
            <div v-else class="steps-container">
              <div 
                v-for="(step, index) in steps" 
                :key="step.id" 
                class="step-item"
                :class="{ active: selectedStep?.id === step.id }"
                @click="selectedStep = step"
              >
                <div class="step-header">
                  <span class="step-number">{{ index + 1 }}</span>
                  <span class="step-name">{{ step.name }}</span>
                  <div class="step-badges">
                    <el-tag v-if="step.skip" type="info" size="small">跳过</el-tag>
                    <el-tag v-if="step.retryCount > 0" size="small">重试{{ step.retryCount }}次</el-tag>
                    <el-tag v-if="step.waitTime > 0" size="small">等待{{ step.waitTime }}s</el-tag>
                  </div>
                  <el-icon class="step-actions" @click.stop="handleRemoveStep(step.id)">
                    <component :is="icons.Close" />
                  </el-icon>
                </div>
                <div class="step-config">
                  <el-tag :type="getMethodType(step.method)" size="small">{{ step.method }}</el-tag>
                  <span class="step-url">{{ step.url }}</span>
                </div>
                <div v-if="step.extract_params && step.extract_params.length > 0" class="step-extract">
                  <el-icon :size="14"><component :is="icons.Key" /></el-icon>
                  <span>提取变量: {{ step.extract_params.map(e => e.key).join(', ') }}</span>
                </div>
                <div v-if="index < steps.length - 1" class="step-arrow">
                  <el-icon :size="20"><component :is="icons.ArrowDown" /></el-icon>
                </div>
              </div>
            </div>
          </div>
        </el-card>
        
        <div class="bottom-actions">
          <el-button @click="handleDebug">
            <el-icon><component :is="icons.VideoPlay" /></el-icon>
            调试场景
          </el-button>
          <el-button type="primary" @click="handleSave">
            <el-icon><component :is="icons.FolderChecked" /></el-icon>
            保存场景
          </el-button>
          <el-button type="success" @click="handleExecute">
            <el-icon><component :is="icons.VideoPlay" /></el-icon>
            立即执行
          </el-button>
          <el-button @click="handleSchedule">
            <el-icon><component :is="icons.Clock" /></el-icon>
            定时配置
          </el-button>
        </div>
      </div>
      
      <div class="right-panel">
        <el-card class="config-card">
          <template #header>
            <span class="card-title">步骤配置</span>
          </template>
          
          <el-form v-if="selectedStep" label-width="100px">
            <el-form-item label="步骤名称">
              <el-input v-model="selectedStep.name" />
            </el-form-item>
            <el-form-item label="关联接口">
              <el-select v-model="selectedStep.api_case_id" placeholder="选择接口">
                <el-option v-for="api in apiLibrary" :key="api.id" :label="api.name" :value="api.id" />
              </el-select>
            </el-form-item>
            <el-form-item label="请求方法">
              <el-select v-model="selectedStep.method">
                <el-option label="GET" value="GET" />
                <el-option label="POST" value="POST" />
                <el-option label="PUT" value="PUT" />
                <el-option label="DELETE" value="DELETE" />
                <el-option label="PATCH" value="PATCH" />
              </el-select>
            </el-form-item>
            <el-form-item label="请求URL">
              <el-input v-model="selectedStep.url" />
            </el-form-item>
            <el-form-item label="前置等待">
              <el-input-number v-model="selectedStep.waitTime" :min="0" :max="60" />
              <span style="margin-left: 8px;">秒</span>
            </el-form-item>
            <el-form-item label="失败重试">
              <el-input-number v-model="selectedStep.retryCount" :min="0" :max="5" />
              <span style="margin-left: 8px;">次</span>
            </el-form-item>
            <el-form-item label="是否跳过">
              <el-switch v-model="selectedStep.skip" />
            </el-form-item>
            <el-form-item label="请求参数">
              <el-input 
                v-model="selectedStep.request_body" 
                type="textarea" 
                :rows="4" 
                placeholder="JSON格式请求体，支持变量替换，如 {&quot;userId&quot;: &quot;{userId}&quot;}"
              />
              <div class="request-body-hint">
                <el-icon :size="12"><component :is="icons.InfoFilled" /></el-icon>
                <span>支持使用前序步骤提取的变量，如 {&quot;id&quot;: &quot;{userId}&quot;}</span>
              </div>
            </el-form-item>
            <el-form-item label="参数提取">
              <div class="extract-container">
                <div v-for="(ext, index) in selectedStep.extract_params" :key="index" class="extract-row">
                  <el-input v-model="ext.key" placeholder="变量名" class="extract-input" />
                  <el-input v-model="ext.path" placeholder="JSON路径" class="extract-input" />
                  <el-button type="danger" size="small" @click="selectedStep.extract_params.splice(index, 1)">
                    <el-icon><component :is="icons.Delete" /></el-icon>
                  </el-button>
                </div>
                <el-button type="primary" size="small" @click="selectedStep.extract_params.push({key: '', path: ''})">
                  <el-icon><component :is="icons.Plus" /></el-icon>
                  添加提取
                </el-button>
              </div>
              <div class="extract-hint">
                <el-icon :size="12"><component :is="icons.InfoFilled" /></el-icon>
                <span>提取的变量可在后续步骤URL中使用，如 /api/users/{userId}</span>
              </div>
            </el-form-item>
          </el-form>
          
          <div v-else class="no-selection">
            <el-icon :size="32" class="empty-icon"><component :is="icons.Setting" /></el-icon>
            <span>选择步骤进行配置</span>
          </div>
        </el-card>
        
        <el-card class="basic-info-card" v-if="selectedScenario">
          <template #header>
            <span class="card-title">场景信息</span>
          </template>
          <el-form label-width="80px">
            <el-form-item label="场景名称">
              <el-input v-model="selectedScenario.name" />
            </el-form-item>
            <el-form-item label="描述">
              <el-input v-model="selectedScenario.description" type="textarea" :rows="3" />
            </el-form-item>
            <el-form-item label="状态">
              <el-radio-group v-model="selectedScenario.status">
                <el-radio label="已启用" />
                <el-radio label="已禁用" />
              </el-radio-group>
            </el-form-item>
            <el-form-item label="创建时间">
              <span class="form-text">{{ selectedScenario.created_at || '-' }}</span>
            </el-form-item>
            <el-form-item label="更新时间">
              <span class="form-text">{{ selectedScenario.updated_at || '-' }}</span>
            </el-form-item>
          </el-form>
        </el-card>
      </div>
    </div>

    <el-dialog v-model="scenarioDialogVisible" :title="isEditScenario ? '编辑场景' : '新建场景'" width="500px">
      <el-form :model="scenarioForm" label-width="100px">
        <el-form-item label="场景名称" required>
          <el-input v-model="scenarioForm.name" placeholder="请输入场景名称" />
        </el-form-item>
        <el-form-item label="所属项目">
          <el-select v-model="scenarioForm.project_id" placeholder="选择所属项目">
            <el-option v-for="proj in projects" :key="proj.id" :label="proj.name" :value="proj.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="scenarioForm.description" type="textarea" :rows="3" placeholder="请输入场景描述" />
        </el-form-item>
        <el-form-item label="状态">
          <el-radio-group v-model="scenarioForm.status">
            <el-radio label="已启用" />
            <el-radio label="已禁用" />
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="scenarioDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSaveScenario">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="debugDialogVisible" title="场景调试" width="800px">
      <div class="debug-container">
        <div class="debug-header">
          <span>{{ selectedScenario?.name }}</span>
          <el-select v-model="debugEnvId" placeholder="选择环境">
            <el-option v-for="env in environments" :key="env.id" :label="env.name" :value="env.id" />
          </el-select>
        </div>
        
        <div class="debug-progress" v-if="isDebugging">
          <el-progress :percentage="debugProgress" :format="(val) => `执行中 ${val}%`" />
        </div>
        
        <div v-if="debugResult" class="debug-result">
          <div class="result-summary">
            <el-tag :type="debugResult.all_passed ? 'success' : 'danger'" size="large">
              {{ debugResult.all_passed ? '执行成功' : '执行失败' }}
            </el-tag>
            <span class="summary-item">总步骤: {{ debugResult.total_steps }}</span>
            <span class="summary-item">通过: {{ debugResult.passed_steps }}</span>
            <span class="summary-item">失败: {{ debugResult.failed_steps }}</span>
            <span class="summary-item">总耗时: {{ debugResult.total_time }}ms</span>
          </div>
          
          <div class="result-steps">
            <div v-for="(step, index) in debugResult.steps" :key="index" class="result-step">
              <div class="step-header" @click="toggleStepDetail(index)">
                <span class="step-num">{{ index + 1 }}</span>
                <span class="step-name">{{ step.step.name }}</span>
                <el-tag :type="step.skipped ? 'info' : (step.passed ? 'success' : 'danger')" size="small">
                  {{ step.skipped ? '跳过' : (step.passed ? '通过' : '失败') }}
                </el-tag>
                <span class="step-time">{{ step.time }}ms</span>
                <el-icon class="expand-icon" :class="{ expanded: expandedSteps[index] }">
                  <component :is="icons.ArrowDown" />
                </el-icon>
              </div>
              
              <div v-if="expandedSteps[index]" class="step-detail-content">
                <div v-if="step.response" class="response-section">
                  <div class="response-status">
                    <span class="label">状态码:</span>
                    <el-tag :type="step.response.status_code < 400 ? 'success' : 'danger'" size="small">
                      {{ step.response.status_code }}
                    </el-tag>
                  </div>
                  
                  <div class="response-tabs">
                    <el-tabs v-model="stepTabs[index]">
                      <el-tab-pane label="响应体" name="body">
                        <pre class="response-body">{{ formatResponse(step.response.body) }}</pre>
                      </el-tab-pane>
                      <el-tab-pane label="响应头" name="headers">
                        <div class="response-headers">
                          <div v-for="(value, key) in step.response.headers" :key="key" class="header-item">
                            <span class="header-key">{{ key }}:</span>
                            <span class="header-value">{{ value }}</span>
                          </div>
                        </div>
                      </el-tab-pane>
                      <el-tab-pane label="请求信息" name="request">
                        <div class="request-info">
                          <div class="info-row">
                            <span class="label">请求方法:</span>
                            <el-tag size="small" :type="getMethodType(step.step.method)">{{ step.step.method }}</el-tag>
                          </div>
                          <div class="info-row">
                            <span class="label">请求URL:</span>
                            <code class="url-code">{{ step.step.url }}</code>
                          </div>
                          <div v-if="step.request_body" class="info-row">
                            <span class="label">请求参数:</span>
                            <pre class="request-body-preview">{{ formatResponse(step.request_body) }}</pre>
                          </div>
                          <div v-if="step.extracted_vars && Object.keys(step.extracted_vars).length > 0" class="extracted-vars">
                            <span class="label">已提取变量:</span>
                            <div v-for="(value, key) in step.extracted_vars" :key="key" class="var-item">
                              <code>{{ key }}</code> = <code>{{ typeof value === 'object' ? JSON.stringify(value) : value }}</code>
                            </div>
                          </div>
                          <div v-else-if="step.step.extract_params && step.step.extract_params.length > 0" class="extracted-vars">
                            <span class="label">提取变量配置:</span>
                            <div v-for="(ext, extIdx) in step.step.extract_params" :key="extIdx" class="var-item">
                              <code>{{ ext.key }}</code> ← <code>{{ ext.path }}</code>
                            </div>
                          </div>
                        </div>
                      </el-tab-pane>
                    </el-tabs>
                  </div>
                </div>
                
                <div v-if="step.assertions && step.assertions.length > 0" class="assertions-section">
                  <div class="section-title">断言结果</div>
                  <el-table :data="step.assertions" size="small" border>
                    <el-table-column prop="assertion.type" label="类型" width="100" />
                    <el-table-column prop="assertion.field" label="字段" min-width="120" />
                    <el-table-column prop="assertion.operator" label="操作" width="60" />
                    <el-table-column prop="assertion.expected" label="期望值" width="100" />
                    <el-table-column prop="actual" label="实际值" width="100">
                      <template #default="scope">
                        <span v-if="scope.row.actual !== null && scope.row.actual !== undefined">{{ scope.row.actual }}</span>
                        <span v-else class="text-gray">-</span>
                      </template>
                    </el-table-column>
                    <el-table-column label="结果" width="70">
                      <template #default="scope">
                        <el-tag :type="scope.row.passed ? 'success' : 'danger'" size="small">
                          {{ scope.row.passed ? '✓' : '✗' }}
                        </el-tag>
                      </template>
                    </el-table-column>
                  </el-table>
                </div>
                
                <div v-if="step.error" class="step-error">
                  <el-icon><component :is="icons.Warning" /></el-icon>
                  <span>{{ step.error }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <div v-if="!isDebugging && !debugResult" class="debug-empty">
          <el-icon :size="32"><component :is="icons.Warning" /></el-icon>
          <span>选择环境后点击执行按钮进行调试</span>
        </div>
      </div>
      
      <template #footer>
        <el-button @click="debugDialogVisible = false">关闭</el-button>
        <el-button type="primary" @click="handleStartDebug" :disabled="isDebugging || !debugEnvId">
          <el-icon><component :is="icons.VideoPlay" /></el-icon>
          执行调试
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, nextTick, onMounted, watch } from 'vue'
import * as icons from '@element-plus/icons-vue'
import { useProjects } from '../composables/useProjects'

const { projects, currentProjectId, loadProjects } = useProjects()

const apiLibrary = ref([])
const scenarios = ref([])
const selectedScenario = ref(null)
const editingScenarioId = ref(null)
const apiSearch = ref('')
const environments = ref([])

const steps = ref([])
const selectedStep = ref(null)
const draggedApi = ref(null)

const scenarioDialogVisible = ref(false)
const isEditScenario = ref(false)
const scenarioForm = reactive({
  name: '',
  project_id: '',
  description: '',
  status: '已启用'
})

const debugDialogVisible = ref(false)
const isDebugging = ref(false)
const debugProgress = ref(0)
const debugEnvId = ref('')
const debugResult = ref(null)
const expandedSteps = reactive({})
const stepTabs = reactive({})

const filteredApiLibrary = computed(() => {
  if (!apiSearch.value) return apiLibrary.value
  const keyword = apiSearch.value.toLowerCase()
  return apiLibrary.value.filter(api => api.name.toLowerCase().includes(keyword))
})

const loadApiLibrary = async () => {
  try {
    const params = new URLSearchParams()
    if (currentProjectId.value) {
      params.append('project_id', currentProjectId.value)
    }
    const response = await fetch(`/api/v1/api_cases${params.toString() ? '?' + params.toString() : ''}`)
    const data = await response.json()
    apiLibrary.value = data.cases || []
  } catch (error) {
    console.error('加载接口用例库失败:', error)
  }
}

const loadScenarios = async () => {
  try {
    const params = new URLSearchParams()
    if (currentProjectId.value) {
      params.append('project_id', currentProjectId.value)
    }
    const response = await fetch(`/api/v1/scenarios${params.toString() ? '?' + params.toString() : ''}`)
    const data = await response.json()
    scenarios.value = data.scenarios || []
    if (scenarios.value.length > 0) {
      handleSelectScenario(scenarios.value[0])
    }
  } catch (error) {
    console.error('加载场景列表失败:', error)
  }
}

const handleProjectChange = () => {
  loadApiLibrary()
  loadScenarios()
}

watch(currentProjectId, () => {
  loadApiLibrary()
  loadScenarios()
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

const handleDragStart = (api) => {
  draggedApi.value = api
}

const handleDrop = () => {
  if (draggedApi.value) {
    const newStep = {
      id: Date.now().toString(),
      api_case_id: draggedApi.value.id,
      name: draggedApi.value.name,
      method: draggedApi.value.method,
      url: draggedApi.value.url,
      waitTime: 0,
      retryCount: 0,
      skip: false,
      request_body: '',
      extract_params: []
    }
    steps.value.push(newStep)
    selectedStep.value = newStep
    draggedApi.value = null
  }
}

const handleAddStep = () => {
  const newStep = {
    id: Date.now().toString(),
    api_case_id: '',
    name: `步骤 ${steps.value.length + 1}`,
    method: 'GET',
    url: '/api/example',
    waitTime: 0,
    retryCount: 0,
    skip: false,
    request_body: '',
    extract_params: []
  }
  steps.value.push(newStep)
  selectedStep.value = newStep
}

const handleRemoveStep = (id) => {
  steps.value = steps.value.filter(step => step.id !== id)
  if (steps.value.length > 0) {
    selectedStep.value = steps.value[0]
  } else {
    selectedStep.value = null
  }
}

const handleClear = () => {
  steps.value = []
  selectedStep.value = null
}

const handleMoveUp = () => {
  if (!selectedStep.value) return
  const index = steps.value.indexOf(selectedStep.value)
  if (index > 0) {
    const temp = steps.value[index]
    steps.value[index] = steps.value[index - 1]
    steps.value[index - 1] = temp
  }
}

const handleMoveDown = () => {
  if (!selectedStep.value) return
  const index = steps.value.indexOf(selectedStep.value)
  if (index < steps.value.length - 1) {
    const temp = steps.value[index]
    steps.value[index] = steps.value[index + 1]
    steps.value[index + 1] = temp
  }
}

const handleSelectScenario = (scenario) => {
  selectedScenario.value = scenario
  editingScenarioId.value = scenario.id
  steps.value = scenario.steps ? JSON.parse(JSON.stringify(scenario.steps)) : []
  if (steps.value.length > 0) {
    selectedStep.value = steps.value[0]
  } else {
    selectedStep.value = null
  }
}

const handleAddScenario = () => {
  isEditScenario.value = false
  editingScenarioId.value = null
  scenarioForm.name = ''
  scenarioForm.project_id = currentProjectId.value || ''
  scenarioForm.description = ''
  scenarioForm.status = '已启用'
  scenarioDialogVisible.value = true
}

const handleEditScenario = (row) => {
  isEditScenario.value = true
  editingScenarioId.value = row.id
  scenarioForm.name = row.name
  scenarioForm.project_id = row.project_id || currentProjectId.value || ''
  scenarioForm.description = row.description || ''
  scenarioForm.status = row.status || '已启用'
  scenarioDialogVisible.value = true
}

const handleSaveScenario = async () => {
  if (!scenarioForm.name) {
    alert('场景名称不能为空')
    return
  }
  
  try {
    const url = isEditScenario.value ? `/api/v1/scenarios/${editingScenarioId.value}` : '/api/v1/scenarios'
    const method = isEditScenario.value ? 'PUT' : 'POST'
    
    const response = await fetch(url, {
      method: method,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(scenarioForm)
    })
    
    const data = await response.json()
    if (data.success) {
      alert(data.message)
      scenarioDialogVisible.value = false
      loadScenarios()
    }
  } catch (error) {
    console.error('保存场景失败:', error)
    alert('保存场景失败')
  }
}

const handleDeleteScenario = async () => {
  if (!selectedScenario.value) return
  if (!confirm(`确定要删除场景「${selectedScenario.value.name}」吗？`)) return
  
  try {
    const response = await fetch(`/api/v1/scenarios/${selectedScenario.value.id}`, {
      method: 'DELETE'
    })
    
    const data = await response.json()
    if (data.success) {
      alert(data.message)
      selectedScenario.value = null
      steps.value = []
      selectedStep.value = null
      loadScenarios()
    }
  } catch (error) {
    console.error('删除场景失败:', error)
    alert('删除失败')
  }
}

const handleDebug = () => {
  debugEnvId.value = environments.value.find(e => e.status === '启用')?.id || (environments.value[0]?.id || '')
  debugResult.value = null
  debugProgress.value = 0
  debugDialogVisible.value = true
  
  Object.keys(expandedSteps).forEach(key => delete expandedSteps[key])
  Object.keys(stepTabs).forEach(key => delete stepTabs[key])
}

const toggleStepDetail = (index) => {
  expandedSteps[index] = !expandedSteps[index]
  if (expandedSteps[index] && !stepTabs[index]) {
    stepTabs[index] = 'body'
  }
}

const formatResponse = (body) => {
  if (typeof body === 'object') {
    return JSON.stringify(body, null, 2)
  }
  return String(body)
}

const getExtractedValue = (steps, currentIndex, varKey) => {
  for (let i = currentIndex; i >= 0; i--) {
    const step = steps[i]
    if (step.step && step.step.extract_params) {
      const extract = step.step.extract_params.find(e => e.key === varKey)
      if (extract && step.response && step.response.body) {
        try {
          let value = step.response.body
          for (const p of extract.path.split('.')) {
            if (typeof value === 'object' && value !== null && p in value) {
              value = value[p]
            } else {
              break
            }
          }
          if (value !== undefined && value !== null) {
            return typeof value === 'object' ? JSON.stringify(value) : String(value)
          }
        } catch {}
      }
    }
  }
  return '(未提取)'
}

const handleStartDebug = async () => {
  if (!selectedScenario.value || !debugEnvId.value) return
  
  isDebugging.value = true
  debugProgress.value = 0
  debugResult.value = null
  
  try {
    const response = await fetch(`/api/v1/scenarios/${selectedScenario.value.id}/execute`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ environment_id: debugEnvId.value })
    })
    
    const data = await response.json()
    if (data.success) {
      debugResult.value = data.report
      debugProgress.value = 100
      
      if (data.report && data.report.steps) {
        data.report.steps.forEach((_, idx) => {
          stepTabs[idx] = 'body'
        })
      }
    } else {
      alert(data.message)
    }
  } catch (error) {
    console.error('调试场景失败:', error)
    alert('调试失败')
  } finally {
    isDebugging.value = false
  }
}

const handleSave = async () => {
  if (!selectedScenario.value) {
    alert('请先选择或创建一个场景')
    return
  }
  
  try {
    const response = await fetch(`/api/v1/scenarios/${selectedScenario.value.id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        name: selectedScenario.value.name,
        description: selectedScenario.value.description,
        status: selectedScenario.value.status,
        steps: steps.value
      })
    })
    
    const data = await response.json()
    if (data.success) {
      alert(data.message)
      loadScenarios()
    }
  } catch (error) {
    console.error('保存场景步骤失败:', error)
    alert('保存失败')
  }
}

const handleExecute = async () => {
  if (!selectedScenario.value) {
    alert('请先选择一个场景')
    return
  }
  
  const envId = environments.value.find(e => e.status === '启用')?.id || (environments.value[0]?.id || '')
  if (!envId) {
    alert('请先配置测试环境')
    return
  }
  
  try {
    const response = await fetch(`/api/v1/scenarios/${selectedScenario.value.id}/execute`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ environment_id: envId })
    })
    
    const data = await response.json()
    if (data.success) {
      const goToReport = confirm('场景执行完成，已生成执行报告，是否查看报告？')
      if (goToReport) {
        window.location.href = '/#/interface-reports'
      }
    } else {
      alert(data.message)
    }
  } catch (error) {
    console.error('执行场景失败:', error)
    alert('执行失败')
  }
}

const handleSchedule = () => {
  window.location.href = '/#/interface-tasks'
}

const getMethodType = (method) => {
  const types = { 'GET': 'success', 'POST': 'primary', 'PUT': 'warning', 'DELETE': 'danger', 'PATCH': 'info' }
  return types[method] || 'info'
}

onMounted(async () => {
  await loadProjects(true)
  loadApiLibrary()
  loadScenarios()
  loadEnvironments()
})
</script>

<style scoped>
.api-scenarios { padding: 20px; }

.page-header { 
  margin-bottom: 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 16px;
}

.header-left { flex: 1; }
.header-right { display: flex; align-items: center; gap: 12px; }
.filter-label { font-size: 14px; color: #6b7280; }
.project-select { width: 200px; }
.page-header h2 { font-size: 24px; font-weight: 600; color: #1f2937; margin-bottom: 4px; }
.page-desc { font-size: 14px; color: #6b7280; }

.scenario-container { display: grid; grid-template-columns: 250px 1fr 320px; gap: 16px; }

.left-panel { height: fit-content; }

.api-library-card, .scenario-list-card { position: sticky; top: 20px; margin-bottom: 16px; }

.card-title { font-size: 16px; font-weight: 600; }

.api-search { width: 120px; }
.scenario-actions { display: flex; gap: 8px; }

.api-list, .scenario-list { max-height: 300px; overflow-y: auto; }

.api-item {
  display: flex; align-items: center; gap: 8px;
  padding: 10px 12px; background-color: #f9fafb; border-radius: 8px; margin-bottom: 8px;
  cursor: grab; transition: all 0.2s;
}
.api-item:hover { background-color: #f3f4f6; border: 1px solid #6366f1; }

.scenario-item {
  display: flex; align-items: center; justify-content: space-between;
  padding: 10px 12px; background-color: #f9fafb; border-radius: 8px; margin-bottom: 8px;
  cursor: pointer; transition: all 0.2s;
}
.scenario-item:hover, .scenario-item.active { background-color: #e0e7ff; border: 1px solid #6366f1; }

.edit-icon {
  margin-left: 8px;
  color: #9ca3af;
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  transition: all 0.2s;
}
.edit-icon:hover { color: #6366f1; background-color: #e0e7ff; }

.center-panel { display: flex; flex-direction: column; gap: 16px; }

.card-header { display: flex; align-items: center; justify-content: space-between; }
.canvas-actions { display: flex; gap: 8px; }

.canvas { min-height: 400px; border: 2px dashed #d1d5db; border-radius: 12px; padding: 20px; }

.empty-canvas {
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  height: 350px; color: #9ca3af; gap: 12px;
}

.empty-icon { color: #c0c4cc; }

.steps-container { display: flex; flex-direction: column; gap: 4px; }

.step-item {
  background-color: #f9fafb; border-radius: 8px; padding: 12px;
  cursor: pointer; border: 2px solid transparent; transition: all 0.2s;
}
.step-item:hover, .step-item.active { border-color: #6366f1; }

.step-header { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
.step-number {
  width: 24px; height: 24px; border-radius: 50%; background-color: #6366f1;
  color: white; font-size: 12px; display: flex; align-items: center; justify-content: center;
}
.step-name { flex: 1; font-weight: 500; }
.step-badges { display: flex; gap: 4px; }
.step-actions { opacity: 0; cursor: pointer; }
.step-item:hover .step-actions { opacity: 1; }

.step-config { display: flex; align-items: center; gap: 8px; margin-top: 8px; font-size: 13px; color: #6b7280; }
.step-url { font-family: monospace; }

.step-extract {
  display: flex; align-items: center; gap: 4px; margin-top: 6px;
  font-size: 12px; color: #6366f1; background-color: #e0e7ff; padding: 4px 8px; border-radius: 4px;
}

.step-arrow { display: flex; justify-content: center; padding: 8px 0; color: #9ca3af; }

.bottom-actions {
  display: flex; gap: 12px; padding: 16px; background-color: #fff;
  border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.right-panel { height: fit-content; }

.config-card, .basic-info-card { position: sticky; top: 20px; margin-bottom: 16px; }

.no-selection {
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  padding: 40px; color: #9ca3af; gap: 8px;
}

.extract-container { max-height: 150px; overflow-y: auto; }
.extract-row { display: flex; gap: 8px; margin-bottom: 8px; }
.extract-input { width: 100px; }
.extract-hint {
  display: flex; align-items: center; gap: 4px; margin-top: 8px;
  font-size: 12px; color: #6b7280; padding: 8px; background-color: #f9fafb; border-radius: 4px;
}

.form-text { color: #6b7280; font-size: 14px; }

.request-body-hint {
  display: flex; align-items: center; gap: 4px; margin-top: 8px;
  font-size: 12px; color: #6b7280; padding: 8px; background-color: #f0f9ff; border-radius: 4px;
}

.debug-container { padding: 8px; }
.debug-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.debug-header span { font-weight: 600; }

.debug-progress { margin-bottom: 16px; }

.debug-result { margin-top: 16px; }
.result-summary { display: flex; align-items: center; gap: 16px; margin-bottom: 16px; flex-wrap: wrap; }
.summary-item { font-size: 13px; color: #6b7280; background-color: #f3f4f6; padding: 4px 8px; border-radius: 4px; }

.result-steps { max-height: 500px; overflow-y: auto; }
.result-step { margin-bottom: 12px; border: 1px solid #e5e7eb; border-radius: 8px; overflow: hidden; }
.result-step .step-header { 
  display: flex; align-items: center; gap: 8px; padding: 12px; 
  background-color: #f9fafb; cursor: pointer; transition: background-color 0.2s;
}
.result-step .step-header:hover { background-color: #f3f4f6; }
.step-num { width: 24px; height: 24px; border-radius: 50%; background-color: #6366f1; color: white; font-size: 12px; display: flex; align-items: center; justify-content: center; }
.step-time { font-size: 12px; color: #6b7280; font-family: monospace; margin-left: auto; }
.expand-icon { transition: transform 0.2s; color: #9ca3af; }
.expand-icon.expanded { transform: rotate(180deg); }

.step-detail-content { padding: 16px; background-color: #fff; border-top: 1px solid #e5e7eb; }

.response-section { margin-bottom: 16px; }
.response-status { display: flex; align-items: center; gap: 8px; margin-bottom: 12px; }
.response-status .label { font-size: 13px; color: #6b7280; }

.response-tabs { margin-top: 12px; }
.response-body {
  background-color: #1f2937; color: #e5e7eb; padding: 12px; border-radius: 4px;
  font-family: monospace; font-size: 12px; max-height: 300px; overflow-y: auto;
  white-space: pre-wrap; word-break: break-all;
}
.response-headers { max-height: 200px; overflow-y: auto; }
.header-item { display: flex; gap: 8px; padding: 6px 0; font-size: 13px; border-bottom: 1px solid #f3f4f6; }
.header-key { color: #6366f1; font-weight: 500; min-width: 150px; }
.header-value { color: #374151; word-break: break-all; }

.request-info { padding: 12px; background-color: #f9fafb; border-radius: 4px; }
.request-info .info-row { display: flex; align-items: flex-start; gap: 8px; margin-bottom: 8px; flex-direction: column; }
.request-info .label { font-size: 13px; color: #6b7280; min-width: 80px; }
.url-code { background-color: #e5e7eb; padding: 4px 8px; border-radius: 4px; font-size: 12px; display: inline-block; }
.request-body-preview {
  background-color: #1f2937; color: #e5e7eb; padding: 12px; border-radius: 4px;
  font-family: monospace; font-size: 12px; max-height: 200px; overflow-y: auto;
  white-space: pre-wrap; word-break: break-all; margin-top: 8px;
}
.extracted-vars { margin-top: 12px; padding-top: 12px; border-top: 1px solid #e5e7eb; }
.var-item { margin-top: 4px; font-size: 12px; }
.var-item code { background-color: #e0e7ff; padding: 2px 6px; border-radius: 4px; color: #4338ca; }

.assertions-section { margin-top: 16px; }
.section-title { font-size: 14px; font-weight: 600; margin-bottom: 12px; color: #374151; }

.text-gray { color: #9ca3af; }

.step-error { display: flex; align-items: center; gap: 8px; padding: 12px; background-color: #fef2f2; border-radius: 4px; color: #ef4444; font-size: 13px; }

.debug-empty { display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 40px; color: #9ca3af; gap: 12px; }
</style>