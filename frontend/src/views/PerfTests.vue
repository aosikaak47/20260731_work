<template>
  <div class="perf-tests">
    <div class="page-header">
      <div class="header-left">
        <h2>性能测试管理</h2>
        <p class="page-desc">管理性能测试场景、配置和执行</p>
      </div>
      <div class="header-right">
        <el-button type="primary" @click="handleAdd">
          <el-icon><component :is="icons.Plus" /></el-icon>
          新建测试
        </el-button>
        <el-button @click="showEnvDialog = true">
          <el-icon><component :is="icons.Setting" /></el-icon>
          环境管理
        </el-button>
      </div>
    </div>

    <div class="stats-cards">
      <el-card
        v-for="stat in statsCards"
        :key="stat.key"
        class="stat-card"
        shadow="hover"
        :style="{ borderLeftColor: stat.color }"
      >
        <div class="stat-content">
          <div class="stat-icon" :style="{ backgroundColor: stat.color + '22', color: stat.color }">
            <el-icon :size="24"><component :is="stat.icon" /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stat.value }}</div>
            <div class="stat-title">{{ stat.title }}</div>
          </div>
        </div>
      </el-card>
    </div>

    <el-card class="main-card">
      <template #header>
        <div class="card-header">
          <span class="card-title">测试列表</span>
          <div class="chart-wrap">
            <div ref="statusChartRef" class="status-chart"></div>
          </div>
        </div>
      </template>

      <div class="filter-bar">
        <el-select v-model="filters.project_id" placeholder="选择项目" clearable class="filter-item">
          <el-option v-for="p in projects" :key="p.id" :label="p.name" :value="p.id" />
        </el-select>
        <el-select v-model="filters.status" placeholder="状态" clearable class="filter-item">
          <el-option label="草稿" value="draft" />
          <el-option label="运行中" value="running" />
          <el-option label="已完成" value="completed" />
          <el-option label="待执行" value="pending" />
        </el-select>
        <el-input v-model="filters.keyword" placeholder="搜索测试名称 / URL" clearable class="search-input" @keyup.enter="loadTests">
          <template #prefix>
            <el-icon><component :is="icons.Search" /></el-icon>
          </template>
        </el-input>
        <el-button type="primary" @click="loadTests">
          <el-icon><component :is="icons.Search" /></el-icon>
          搜索
        </el-button>
        <el-button @click="resetFilters">
          <el-icon><component :is="icons.Refresh" /></el-icon>
          重置
        </el-button>
      </div>

      <el-table v-loading="loading" :data="filteredTests" stripe border class="perf-table" empty-text="暂无性能测试数据">
        <el-table-column type="index" label="#" width="55" align="center" />
        <el-table-column prop="name" label="名称" min-width="150" show-overflow-tooltip />
        <el-table-column label="类型" width="90" align="center">
          <template #default="scope">
            <el-tag v-if="scope.row.steps && scope.row.steps.length > 0" type="warning" size="small" effect="plain">场景</el-tag>
            <el-tag v-else type="info" size="small" effect="plain">单接口</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="target_url" label="目标URL" min-width="180" show-overflow-tooltip>
          <template #default="scope">
            <span class="url-text">{{ scope.row.protocol }}://{{ scope.row.target_url }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="method" label="方法" width="90" align="center">
          <template #default="scope">
            <el-tag :type="methodTagType(scope.row.method)" size="small" effect="dark">{{ scope.row.method }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="环境" width="110" align="center">
          <template #default="scope">
            <el-tag v-if="scope.row.environment_id" size="small" type="success">{{ getEnvName(scope.row.environment_id) }}</el-tag>
            <span v-else class="text-muted">-</span>
          </template>
        </el-table-column>
        <el-table-column prop="concurrency" label="并发" width="70" align="center" />
        <el-table-column prop="status" label="状态" width="90" align="center">
          <template #default="scope">
            <el-tag :type="statusTagType(scope.row.status)" size="small">{{ statusLabel(scope.row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="last_run" label="上次执行" width="150">
          <template #default="scope">
            <span v-if="scope.row.last_run">{{ scope.row.last_run }}</span>
            <span v-else class="text-muted">未执行</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="240" fixed="right" class-name="action-cell">
          <template #default="scope">
            <div class="action-btns">
              <el-button size="small" type="primary" :loading="executingId === scope.row.id" @click="handleExecute(scope.row)">执行</el-button>
              <el-button size="small" @click="handleEdit(scope.row)">
                <el-icon><component :is="icons.Edit" /></el-icon>
                编辑
              </el-button>
              <el-button size="small" type="danger" @click="handleDelete(scope.row)">
                <el-icon><component :is="icons.Delete" /></el-icon>
              </el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 编辑对话框 -->
    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑测试' : '新建测试'" width="960px" :close-on-click-modal="false" top="3vh">
      <el-tabs v-model="activeTab" class="editor-tabs">
        <!-- 基本信息 -->
        <el-tab-pane label="基本信息" name="basic">
          <el-form :model="form" label-width="110px" class="perf-form">
            <el-row :gutter="16">
              <el-col :span="12">
                <el-form-item label="测试名称" required>
                  <el-input v-model="form.name" placeholder="请输入测试名称" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="所属项目" required>
                  <el-select v-model="form.project_id" placeholder="选择项目" style="width: 100%">
                    <el-option v-for="p in projects" :key="p.id" :label="p.name" :value="p.id" />
                  </el-select>
                </el-form-item>
              </el-col>
            </el-row>
            <el-row :gutter="16">
              <el-col :span="6">
                <el-form-item label="协议">
                  <el-select v-model="form.protocol" style="width: 100%">
                    <el-option label="HTTP" value="HTTP" />
                    <el-option label="HTTPS" value="HTTPS" />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="6">
                <el-form-item label="请求方法">
                  <el-select v-model="form.method" style="width: 100%">
                    <el-option label="GET" value="GET" />
                    <el-option label="POST" value="POST" />
                    <el-option label="PUT" value="PUT" />
                    <el-option label="DELETE" value="DELETE" />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="6">
                <el-form-item label="优先级">
                  <el-select v-model="form.priority" style="width: 100%">
                    <el-option label="高" value="high" />
                    <el-option label="中" value="medium" />
                    <el-option label="低" value="low" />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="6">
                <el-form-item label="测试类型">
                  <el-select v-model="form.test_type" style="width: 100%" @change="handleTestTypeChange">
                    <el-option label="单接口" value="single" />
                    <el-option label="场景编排" value="scenario" />
                  </el-select>
                </el-form-item>
              </el-col>
            </el-row>
            <el-form-item label="目标URL" required>
              <el-input v-model="form.target_url" placeholder="如：api.example.com/v1/login" />
            </el-form-item>
            <el-row :gutter="16">
              <el-col :span="6">
                <el-form-item label="并发数">
                  <el-input-number v-model="form.concurrency" :min="1" :max="10000" controls-position="right" style="width: 100%" />
                </el-form-item>
              </el-col>
              <el-col :span="6">
                <el-form-item label="爬升时间">
                  <el-input-number v-model="form.ramp_up" :min="0" :max="3600" controls-position="right" style="width: 100%" />
                </el-form-item>
              </el-col>
              <el-col :span="6">
                <el-form-item label="持续时长">
                  <el-input-number v-model="form.duration" :min="1" :max="86400" controls-position="right" style="width: 100%" />
                </el-form-item>
              </el-col>
              <el-col :span="6">
                <el-form-item label="最大虚拟用户">
                  <el-input-number v-model="form.max_vusers" :min="1" :max="100000" controls-position="right" style="width: 100%" />
                </el-form-item>
              </el-col>
            </el-row>
            <el-row :gutter="16">
              <el-col :span="12">
                <el-form-item label="思考时间">
                  <el-input-number v-model="form.think_time" :min="0" :max="60" controls-position="right" style="width: 100%" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="标签">
                  <el-input v-model="form.tags" placeholder="多个标签用逗号分隔" />
                </el-form-item>
              </el-col>
            </el-row>
            <el-form-item label="请求头">
              <el-input v-model="form.headers" type="textarea" :rows="3" placeholder='{"Content-Type":"application/json","Authorization":"Bearer xxx"}' />
            </el-form-item>
            <el-form-item label="请求体" v-if="['POST', 'PUT', 'PATCH'].includes(form.method)">
              <el-input v-model="form.body" type="textarea" :rows="4" placeholder='{"username":"admin","password":"***"}' />
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <!-- 场景编排 -->
        <el-tab-pane label="场景编排" name="steps" :disabled="form.test_type !== 'scenario'">
          <div class="steps-toolbar">
            <span class="steps-tip">场景编排：按顺序执行多个接口步骤，适用于复杂业务流程压测</span>
            <div class="steps-actions">
              <el-button size="small" @click="addStep('request')">
                <el-icon><component :is="icons.Link" /></el-icon>
                请求步骤
              </el-button>
              <el-button size="small" @click="addStep('assert')">
                <el-icon><component :is="icons.CircleCheck" /></el-icon>
                断言步骤
              </el-button>
              <el-button size="small" @click="addStep('wait')">
                <el-icon><component :is="icons.Clock" /></el-icon>
                等待步骤
              </el-button>
            </div>
          </div>
          <div class="steps-list">
            <div v-if="form.steps.length === 0" class="empty-steps">
              <el-icon :size="48" color="#c0c4cc"><component :is="icons.Document" /></el-icon>
              <p>暂无步骤，点击上方按钮添加</p>
            </div>
            <div v-else v-for="(step, index) in form.steps" :key="step.id" class="step-item">
              <div class="step-header">
                <span class="step-index">{{ index + 1 }}</span>
                <el-select v-model="step.type" size="small" class="step-type">
                  <el-option label="请求" value="request" />
                  <el-option label="断言" value="assert" />
                  <el-option label="等待" value="wait" />
                </el-select>
                <el-input v-model="step.name" size="small" class="step-name" :placeholder="'步骤名称'" />
                <div class="step-actions">
                  <el-button size="small" text :disabled="index === 0" @click="moveStep(index, -1)">
                    <el-icon><component :is="icons.ArrowUp" /></el-icon>
                  </el-button>
                  <el-button size="small" text :disabled="index === form.steps.length - 1" @click="moveStep(index, 1)">
                    <el-icon><component :is="icons.ArrowDown" /></el-icon>
                  </el-button>
                  <el-button size="small" text type="danger" @click="removeStep(step.id)">
                    <el-icon><component :is="icons.Delete" /></el-icon>
                  </el-button>
                </div>
              </div>
              <div class="step-body">
                <template v-if="step.type === 'request'">
                  <el-row :gutter="12">
                    <el-col :span="4">
                      <el-select v-model="step.method" size="small" style="width: 100%">
                        <el-option label="GET" value="GET" />
                        <el-option label="POST" value="POST" />
                        <el-option label="PUT" value="PUT" />
                        <el-option label="DELETE" value="DELETE" />
                      </el-select>
                    </el-col>
                    <el-col :span="20">
                      <el-input v-model="step.url" size="small" placeholder="请求URL" />
                    </el-col>
                  </el-row>
                  <el-input v-model="step.headers" type="textarea" :rows="2" class="step-field" placeholder='请求头 (JSON)' />
                  <el-input v-model="step.body" type="textarea" :rows="3" class="step-field" placeholder='请求体 (JSON)' />
                </template>
                <template v-else-if="step.type === 'assert'">
                  <el-row :gutter="12">
                    <el-col :span="8">
                      <el-select v-model="step.assert_type" size="small" style="width: 100%">
                        <el-option label="状态码" value="status_code" />
                        <el-option label="响应时间" value="response_time" />
                        <el-option label="响应体包含" value="body_contains" />
                      </el-select>
                    </el-col>
                    <el-col :span="16">
                      <el-input v-model="step.assert_value" size="small" placeholder="断言值，如 200、100、success" />
                    </el-col>
                  </el-row>
                </template>
                <template v-else-if="step.type === 'wait'">
                  <el-row :gutter="12">
                    <el-col :span="8">
                      <el-input-number v-model="step.wait_time" :min="1" :max="300" controls-position="right" size="small" style="width: 100%" />
                    </el-col>
                    <el-col :span="16">
                      <span class="step-hint">等待该步骤完成后再执行下一步（秒）</span>
                    </el-col>
                  </el-row>
                </template>
                <el-row :gutter="12" class="step-meta">
                  <el-col :span="8">
                    <span class="meta-label">延时:</span>
                    <el-input-number v-model="step.delay" :min="0" :max="60" :step="0.5" controls-position="right" size="small" style="width: 110px" />
                  </el-col>
                  <el-col :span="8">
                    <span class="meta-label">重试:</span>
                    <el-input-number v-model="step.retry" :min="0" :max="5" controls-position="right" size="small" style="width: 110px" />
                  </el-col>
                  <el-col :span="8">
                    <span class="meta-label">超时:</span>
                    <el-input-number v-model="step.timeout" :min="1" :max="300" controls-position="right" size="small" style="width: 110px" />
                  </el-col>
                </el-row>
              </div>
            </div>
          </div>
        </el-tab-pane>

        <!-- 环境配置 -->
        <el-tab-pane label="环境配置" name="environment">
          <el-form :model="form" label-width="110px" class="perf-form">
            <el-form-item label="选择环境">
              <el-select v-model="form.environment_id" placeholder="选择目标环境" clearable style="width: 100%" @change="handleEnvChange">
                <el-option label="不使用环境" value="" />
                <el-option v-for="env in environments" :key="env.id" :label="env.name" :value="env.id" />
              </el-select>
            </el-form-item>
            <el-alert v-if="currentEnv" :title="`当前环境: ${currentEnv.name}`" type="info" :closable="false" show-icon class="env-alert">
              <div class="env-info">
                <p><strong>Base URL:</strong> {{ currentEnv.base_url }}</p>
                <p v-if="currentEnv.description"><strong>描述:</strong> {{ currentEnv.description }}</p>
                <p v-if="currentEnv.headers"><strong>Headers:</strong> {{ JSON.stringify(currentEnv.headers) }}</p>
              </div>
            </el-alert>
            <el-alert v-else-if="form.environment_id" title="环境不存在或已被删除" type="warning" :closable="false" show-icon />
            <el-alert v-else title="不使用环境配置，将直接使用URL" type="info" :closable="false" show-icon />
          </el-form>
        </el-tab-pane>

        <!-- 在线调试 -->
        <el-tab-pane label="在线调试" name="debug">
          <div class="debug-section">
            <div class="debug-request">
              <h4>请求配置</h4>
              <div class="debug-request-line">
                <el-select v-model="debugForm.method" class="debug-method">
                  <el-option label="GET" value="GET" />
                  <el-option label="POST" value="POST" />
                  <el-option label="PUT" value="PUT" />
                  <el-option label="DELETE" value="DELETE" />
                </el-select>
                <el-select v-model="debugForm.protocol" class="debug-protocol">
                  <el-option label="HTTP" value="HTTP" />
                  <el-option label="HTTPS" value="HTTPS" />
                </el-select>
                <el-input v-model="debugForm.target_url" placeholder="目标URL" class="debug-url" />
                <el-button type="primary" @click="runDebug" :loading="debugLoading">
                  <el-icon><component :is="icons.Promotion" /></el-icon>
                  发送
                </el-button>
              </div>
              <div v-if="form.environment_id" class="debug-env-hint">
                <el-icon><component :is="icons.Setting" /></el-icon>
                <span>使用环境: {{ getEnvName(form.environment_id) }}</span>
              </div>
              <el-input v-model="debugForm.headers" type="textarea" :rows="3" class="debug-textarea" placeholder='请求头 (JSON格式)' />
              <el-input v-model="debugForm.body" type="textarea" :rows="4" class="debug-textarea" placeholder='请求体 (JSON格式)' v-if="['POST', 'PUT', 'PATCH'].includes(debugForm.method)" />
            </div>
            <el-divider />
            <div class="debug-response">
              <h4>响应结果</h4>
              <div v-if="debugResult" class="response-display">
                <div class="response-header-bar">
                  <el-tag :type="debugResult.status_code >= 200 && debugResult.status_code < 300 ? 'success' : 'danger'" size="large">
                    {{ debugResult.status_code }} {{ debugResult.status_text }}
                  </el-tag>
                  <span class="response-meta">耗时: {{ debugResult.time }}ms | 大小: {{ formatSize(debugResult.size) }}</span>
                </div>
                <el-collapse>
                  <el-collapse-item title="响应头">
                    <el-table :data="debugHeaders" size="small" border>
                      <el-table-column prop="key" label="Header" width="200" />
                      <el-table-column prop="value" label="Value" show-overflow-tooltip />
                    </el-table>
                  </el-collapse-item>
                  <el-collapse-item title="响应体">
                    <pre class="code-block">{{ formatResponse(debugResult.body, debugResult.body_type) }}</pre>
                  </el-collapse-item>
                </el-collapse>
              </div>
              <div v-else-if="debugError" class="debug-error-state">
                <el-icon :size="48" color="#F56C6C"><component :is="icons.Warning" /></el-icon>
                <p class="error-title">请求失败</p>
                <p class="error-message">{{ debugError }}</p>
              </div>
              <div v-else class="debug-empty">
                <el-icon :size="48" color="#909399"><component :is="icons.Document" /></el-icon>
                <p>配置请求参数后点击"发送"查看结果</p>
              </div>
            </div>
          </div>
        </el-tab-pane>
      </el-tabs>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" :loading="saving" @click="handleSave">
            {{ isEdit ? '保存修改' : '创建测试' }}
          </el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 环境管理对话框 -->
    <el-dialog v-model="showEnvDialog" title="环境管理" width="700px">
      <div class="env-toolbar">
        <el-button type="primary" @click="handleAddEnv">
          <el-icon><component :is="icons.Plus" /></el-icon>
          新增环境
        </el-button>
      </div>
      <el-table :data="environments" border stripe>
        <el-table-column prop="name" label="环境名称" width="150" />
        <el-table-column prop="base_url" label="Base URL" min-width="200" />
        <el-table-column prop="description" label="描述" min-width="150" show-overflow-tooltip />
        <el-table-column label="操作" width="150">
          <template #default="scope">
            <el-button size="small" @click="handleEditEnv(scope.row)">编辑</el-button>
            <el-button size="small" type="danger" @click="handleDeleteEnv(scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <template #footer>
        <el-button @click="showEnvDialog = false">关闭</el-button>
      </template>
    </el-dialog>

    <!-- 新增/编辑环境对话框 -->
    <el-dialog v-model="envDialogVisible" :title="isEditEnv ? '编辑环境' : '新增环境'" width="500px" append-to-body>
      <el-form :model="envForm" label-width="100px">
        <el-form-item label="环境名称">
          <el-input v-model="envForm.name" placeholder="如：开发环境" />
        </el-form-item>
        <el-form-item label="Base URL">
          <el-input v-model="envForm.base_url" placeholder="如：http://dev.example.com" />
        </el-form-item>
        <el-form-item label="Headers">
          <el-input v-model="envForm.headers_text" type="textarea" :rows="4" placeholder='{"Content-Type":"application/json"}' />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="envForm.description" type="textarea" :rows="2" placeholder="环境描述" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="envDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveEnv">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import * as echarts from 'echarts'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useProjects } from '../composables/useProjects'
import {
  Plus, Search, Refresh, Delete, Edit, VideoPlay,
  DataLine, Lightning, Odometer, Document,
  Connection, Promotion, Warning, Setting,
  Link, CircleCheck, Clock, ArrowUp, ArrowDown
} from '@element-plus/icons-vue'

const icons = {
  Plus, Search, Refresh, Delete, Edit, VideoPlay,
  DataLine, Lightning, Odometer, Document,
  Connection, Promotion, Warning, Setting,
  Link, CircleCheck, Clock, ArrowUp, ArrowDown
}

const { projects, loadProjects } = useProjects()

const tests = ref([])
const environments = ref([])
const loading = ref(false)
const saving = ref(false)
const executingId = ref(null)
const stats = ref({ total: 0, running: 0, completed: 0, draft: 0 })

const filters = reactive({ project_id: '', status: '', keyword: '' })

const dialogVisible = ref(false)
const isEdit = ref(false)
const editingId = ref(null)
const activeTab = ref('basic')

const showEnvDialog = ref(false)
const envDialogVisible = ref(false)
const isEditEnv = ref(false)
const envForm = reactive({ id: '', name: '', base_url: '', headers_text: '{}', description: '' })

const currentEnv = computed(() => {
  if (!form.environment_id) return null
  return environments.value.find(e => e.id === form.environment_id)
})

const statusChartRef = ref(null)
let statusChartInstance = null

const defaultForm = () => ({
  name: '',
  project_id: '',
  target_url: '',
  method: 'GET',
  protocol: 'HTTPS',
  concurrency: 50,
  ramp_up: 10,
  duration: 60,
  max_vusers: 200,
  think_time: 0,
  priority: 'medium',
  test_type: 'single',
  environment_id: '',
  tags: '',
  headers: '',
  body: '',
  steps: []
})

const form = reactive(defaultForm())

const debugForm = reactive({
  method: 'GET',
  protocol: 'HTTPS',
  target_url: '',
  headers: '',
  body: ''
})
const debugLoading = ref(false)
const debugResult = ref(null)
const debugError = ref('')

const debugHeaders = computed(() => {
  if (!debugResult.value?.headers) return []
  return Object.entries(debugResult.value.headers).map(([key, value]) => ({ key, value: String(value) }))
})

const statsCards = computed(() => [
  { key: 'total', title: '测试总数', value: stats.value.total, icon: icons.DataLine, color: '#6366f1' },
  { key: 'running', title: '运行中', value: stats.value.running, icon: icons.Lightning, color: '#ef4444' },
  { key: 'completed', title: '已完成', value: stats.value.completed, icon: icons.Odometer, color: '#10b981' },
  { key: 'draft', title: '草稿', value: stats.value.draft, icon: icons.Document, color: '#6b7280' }
])

const filteredTests = computed(() => {
  let list = tests.value
  if (filters.status) list = list.filter(t => t.status === filters.status)
  if (filters.project_id) list = list.filter(t => String(t.project_id) === String(filters.project_id))
  if (filters.keyword) {
    const kw = filters.keyword.toLowerCase()
    list = list.filter(t => (t.name && t.name.toLowerCase().includes(kw)) || (t.target_url && t.target_url.toLowerCase().includes(kw)))
  }
  return list
})

const statusLabel = s => ({ draft: '草稿', running: '运行中', completed: '已完成', pending: '待执行' }[s] || s || '-')
const statusTagType = s => ({ draft: 'info', pending: 'warning', running: 'danger', completed: 'success' }[s] || 'info')
const methodTagType = m => ({ GET: 'success', POST: 'primary', PUT: 'warning', DELETE: 'danger' }[m] || 'info')

const getEnvName = envId => {
  const env = environments.value.find(e => e.id === envId)
  return env ? env.name : envId
}

const loadTests = async () => {
  loading.value = true
  try {
    const res = await fetch('/api/v1/perf/tests')
    const json = await res.json()
    const data = json.data || json
    tests.value = data.tests || []
  } catch (e) {
    ElMessage.error('加载测试列表失败')
  } finally {
    loading.value = false
  }
}

const loadEnvironments = async () => {
  try {
    const res = await fetch('/api/v1/perf/environments')
    const json = await res.json()
    environments.value = json.environments || []
  } catch (e) {
    console.error('加载环境列表失败:', e)
  }
}

const loadDashboard = async () => {
  try {
    const res = await fetch('/api/v1/perf/dashboard')
    const json = await res.json()
    const data = json.data || json
    const s = data.stats || data
    stats.value = { total: Number(s.total ?? 0), running: Number(s.running ?? 0), completed: Number(s.completed ?? 0), draft: Number(s.draft ?? 0) }
    nextTick(updateStatusChart)
  } catch (e) {
    console.error('加载性能仪表盘失败:', e)
  }
}

const updateStatusChart = () => {
  if (!statusChartInstance) return
  statusChartInstance.setOption({
    tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
    legend: { bottom: 0, textStyle: { color: '#6b7280', fontSize: 11 }, icon: 'circle', itemWidth: 8, itemHeight: 8 },
    series: [{
      name: '测试状态', type: 'pie', radius: ['42%', '68%'], center: ['50%', '42%'],
      avoidLabelOverlap: false, itemStyle: { borderRadius: 6, borderColor: '#fff', borderWidth: 2 },
      label: { show: false }, emphasis: { label: { show: true, fontSize: 13, fontWeight: 'bold' } },
      data: [
        { value: stats.value.total, name: '总数', itemStyle: { color: '#6366f1' } },
        { value: stats.value.running, name: '运行中', itemStyle: { color: '#ef4444' } },
        { value: stats.value.completed, name: '已完成', itemStyle: { color: '#10b981' } },
        { value: stats.value.draft, name: '草稿', itemStyle: { color: '#9ca3af' } }
      ]
    }]
  })
}

const initStatusChart = () => {
  if (!statusChartRef.value) return
  statusChartInstance = echarts.init(statusChartRef.value)
  updateStatusChart()
}

const handleResize = () => statusChartInstance?.resize()

const resetFilters = () => { filters.project_id = ''; filters.status = ''; filters.keyword = ''; loadTests() }
const resetForm = () => { Object.assign(form, defaultForm()) }

const handleTestTypeChange = () => {
  if (form.test_type !== 'scenario') {
    form.steps = []
  }
}

const handleAdd = () => {
  isEdit.value = false
  editingId.value = null
  resetForm()
  if (projects.value.length && !form.project_id) form.project_id = projects.value[0].id
  activeTab.value = 'basic'
  resetDebugForm()
  dialogVisible.value = true
}

const handleEdit = row => {
  isEdit.value = true
  editingId.value = row.id
  Object.assign(form, defaultForm(), row)
  if (Array.isArray(row.tags)) form.tags = row.tags.join(',')
  if (!form.test_type) form.test_type = form.steps && form.steps.length > 0 ? 'scenario' : 'single'
  activeTab.value = 'basic'
  Object.assign(debugForm, { method: form.method, protocol: form.protocol, target_url: form.target_url, headers: form.headers, body: form.body })
  debugResult.value = null
  debugError.value = ''
  dialogVisible.value = true
}

const handleSave = async () => {
  if (!form.name || !form.target_url || !form.project_id) {
    ElMessage.warning('请填写测试名称、所属项目和目标URL')
    return
  }
  saving.value = true
  try {
    const payload = { ...form }
    if (payload.tags && typeof payload.tags === 'string') payload.tags = payload.tags.split(',').map(s => s.trim()).filter(Boolean)
    const url = isEdit.value ? `/api/v1/perf/tests/${editingId.value}` : '/api/v1/perf/tests'
    const method = isEdit.value ? 'PUT' : 'POST'
    const res = await fetch(url, { method, headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) })
    const json = await res.json()
    const data = json.data || json
    if (json.success !== false && data.success !== false) {
      ElMessage.success(isEdit.value ? '测试更新成功' : '测试创建成功')
      dialogVisible.value = false
      await loadTests()
      await loadDashboard()
    } else {
      ElMessage.error(data.message || json.message || '保存失败')
    }
  } catch (e) {
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

const handleExecute = async row => {
  try {
    await ElMessageBox.confirm(`确定要执行性能测试「${row.name}」吗？`, '确认执行', { confirmButtonText: '执行', cancelButtonText: '取消', type: 'info' })
  } catch { return }
  executingId.value = row.id
  try {
    const res = await fetch(`/api/v1/perf/tests/${row.id}/execute`, { method: 'POST', headers: { 'Content-Type': 'application/json' } })
    const json = await res.json()
    const data = json.data || json
    if (json.success !== false && data.success !== false) {
      const reportId = data.report_id || data.reportId || data.id || '-'
      ElMessage.success(`测试已触发执行，报告ID：${reportId}`)
      await loadTests()
      await loadDashboard()
    } else {
      ElMessage.error(data.message || json.message || '执行失败')
    }
  } catch (e) {
    ElMessage.error('执行失败')
  } finally {
    executingId.value = null
  }
}

const handleDelete = row => {
  ElMessageBox.confirm(`确定要删除性能测试「${row.name}」吗？此操作不可恢复。`, '确认删除', { confirmButtonText: '删除', cancelButtonText: '取消', type: 'warning' })
    .then(async () => {
      try {
        const res = await fetch(`/api/v1/perf/tests/${row.id}`, { method: 'DELETE' })
        const json = await res.json()
        const data = json.data || json
        if (json.success !== false && data.success !== false) {
          ElMessage.success('删除成功')
          await loadTests()
          await loadDashboard()
        } else {
          ElMessage.error(data.message || json.message || '删除失败')
        }
      } catch (e) { ElMessage.error('删除失败') }
    }).catch(() => {})
}

// Step management
const addStep = type => {
  const stepTypes = {
    request: { method: 'GET', url: '', headers: '{}', body: '' },
    assert: { assert_type: 'status_code', assert_value: '200' },
    wait: { wait_time: 5 }
  }
  const newStep = {
    id: Date.now() + Math.random(),
    type,
    name: `${type === 'request' ? '请求' : type === 'assert' ? '断言' : '等待'}步骤 ${form.steps.length + 1}`,
    delay: 0, retry: 0, timeout: 30,
    ...(stepTypes[type] || {})
  }
  form.steps.push(newStep)
}

const removeStep = id => { form.steps = form.steps.filter(s => s.id !== id) }
const moveStep = (index, direction) => {
  const newIndex = index + direction
  if (newIndex < 0 || newIndex >= form.steps.length) return
  const temp = form.steps[index]
  form.steps.splice(index, 1)
  form.steps.splice(newIndex, 0, temp)
}

// Debug
const resetDebugForm = () => {
  Object.assign(debugForm, { method: form.method || 'GET', protocol: form.protocol || 'HTTPS', target_url: form.target_url || '', headers: form.headers || '{}', body: form.body || '' })
  debugResult.value = null
  debugError.value = ''
}

const handleEnvChange = () => {
  const env = currentEnv.value
  if (env && env.base_url) {
    if (!debugForm.target_url || debugForm.target_url.startsWith('http')) {
      // Keep the URL as-is if it already starts with http
    }
  }
}

const runDebug = async () => {
  if (!debugForm.target_url) {
    ElMessage.warning('请输入目标URL')
    return
  }
  debugLoading.value = true
  debugResult.value = null
  debugError.value = ''
  try {
    const payload = { method: debugForm.method, protocol: debugForm.protocol, target_url: debugForm.target_url, headers: debugForm.headers, body: debugForm.body }
    if (form.environment_id) payload.environment_id = form.environment_id
    const res = await fetch(`/api/v1/perf/tests/${editingId.value || 'pt_001'}/debug`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) })
    const json = await res.json()
    if (json.success) {
      debugResult.value = json.response
      ElMessage.success(`请求成功，状态码: ${json.response.status_code}`)
    } else {
      debugError.value = json.error || '请求失败'
    }
  } catch (e) {
    debugError.value = '网络错误或请求超时'
  } finally {
    debugLoading.value = false
  }
}

const formatResponse = (body, bodyType) => {
  if (!body) return '(空)'
  try {
    if (typeof body === 'object') return JSON.stringify(body, null, 2)
    const parsed = JSON.parse(body)
    return JSON.stringify(parsed, null, 2)
  } catch { return String(body) }
}

const formatSize = bytes => {
  if (!bytes) return '0 B'
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(2)} KB`
  return `${(bytes / 1024 / 1024).toFixed(2)} MB`
}

// Environment CRUD
const handleAddEnv = () => {
  isEditEnv.value = false
  Object.assign(envForm, { id: '', name: '', base_url: '', headers_text: '{}', description: '' })
  envDialogVisible.value = true
}

const handleEditEnv = row => {
  isEditEnv.value = true
  const headers = row.headers || {}
  Object.assign(envForm, { id: row.id, name: row.name, base_url: row.base_url, headers_text: JSON.stringify(headers, null, 2), description: row.description || '' })
  envDialogVisible.value = true
}

const handleDeleteEnv = row => {
  ElMessageBox.confirm(`确定删除环境「${row.name}」吗？`, '删除确认', { type: 'warning' })
    .then(async () => {
      try {
        await fetch(`/api/v1/perf/environments/${row.id}`, { method: 'DELETE' })
        ElMessage.success('删除成功')
        await loadEnvironments()
      } catch { ElMessage.error('删除失败') }
    }).catch(() => {})
}

const saveEnv = async () => {
  if (!envForm.name || !envForm.base_url) {
    ElMessage.warning('请填写环境名称和Base URL')
    return
  }
  try {
    const headers = JSON.parse(envForm.headers_text || '{}')
    const payload = { name: envForm.name, base_url: envForm.base_url, headers, description: envForm.description }
    if (isEditEnv.value) {
      payload.id = envForm.id
      await fetch(`/api/v1/perf/environments/${envForm.id}`, { method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) })
      ElMessage.success('更新成功')
    } else {
      await fetch('/api/v1/perf/environments', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) })
      ElMessage.success('创建成功')
    }
    envDialogVisible.value = false
    await loadEnvironments()
  } catch (e) {
    ElMessage.error('保存失败，请检查Headers格式')
  }
}

watch(dialogVisible, val => { if (val && !statusChartInstance) nextTick(initStatusChart) })

onMounted(async () => {
  await Promise.all([loadProjects(), loadEnvironments()])
  initStatusChart()
  await Promise.all([loadTests(), loadDashboard()])
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  statusChartInstance?.dispose()
})
</script>

<style scoped>
.perf-tests { padding: 20px; }
.page-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 24px; flex-wrap: wrap; gap: 16px; }
.page-header h2 { font-size: 24px; font-weight: 600; color: #1f2937; margin-bottom: 4px; }
.page-desc { font-size: 14px; color: #6b7280; }
.header-right { display: flex; align-items: center; gap: 12px; }
.stats-cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 16px; margin-bottom: 24px; }
.stat-card { border: 1px solid #e5e7eb; border-left: 4px solid #6366f1; background: linear-gradient(135deg, #fff 0%, #f5f7ff 100%); transition: transform 0.2s, box-shadow 0.2s; }
.stat-card:hover { transform: translateY(-2px); box-shadow: 0 8px 24px rgba(99, 102, 241, 0.15); }
.stat-content { display: flex; align-items: center; gap: 16px; }
.stat-icon { width: 52px; height: 52px; border-radius: 12px; display: flex; align-items: center; justify-content: center; }
.stat-value { font-size: 26px; font-weight: 700; color: #1f2937; line-height: 1.2; }
.stat-title { font-size: 13px; color: #6b7280; margin-top: 4px; }
.main-card { border: 1px solid #e5e7eb; }
.card-header { display: flex; align-items: center; justify-content: space-between; }
.card-title { font-size: 16px; font-weight: 600; color: #1f2937; }
.chart-wrap { width: 220px; height: 96px; }
.status-chart { width: 100%; height: 100%; }
.filter-bar { display: flex; gap: 12px; margin-bottom: 16px; flex-wrap: wrap; align-items: center; }
.filter-item { width: 180px; }
.search-input { width: 260px; }
.url-text { color: #4b5563; font-family: 'Menlo', 'Consolas', monospace; font-size: 12.5px; }
.text-muted { color: #9ca3af; }
.perf-table :deep(.el-table__row:hover) > td { background-color: rgba(99, 102, 241, 0.06) !important; }
.action-btns { display: flex; gap: 4px; }
.dialog-footer { display: flex; justify-content: flex-end; gap: 8px; }

.editor-tabs :deep(.el-tabs__content) { max-height: 55vh; overflow-y: auto; }
.perf-form { padding: 0 10px; }
.perf-form :deep(.el-input-number) { width: 100%; }

.steps-toolbar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; padding: 10px; background: #f9fafb; border-radius: 8px; }
.steps-tip { font-size: 13px; color: #6b7280; }
.steps-actions { display: flex; gap: 8px; }

.steps-list { display: flex; flex-direction: column; gap: 12px; }
.empty-steps { display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 40px; color: #9ca3af; gap: 12px; }

.step-item { border: 1px solid #e5e7eb; border-radius: 8px; overflow: hidden; }
.step-header { display: flex; align-items: center; gap: 8px; padding: 10px 12px; background: #f9fafb; border-bottom: 1px solid #e5e7eb; }
.step-index { width: 24px; height: 24px; border-radius: 50%; background: #6366f1; color: white; font-size: 12px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.step-type { width: 100px; }
.step-name { flex: 1; }
.step-actions { display: flex; gap: 2px; }
.step-body { padding: 12px; display: flex; flex-direction: column; gap: 8px; }
.step-field { margin-top: 8px; }
.step-meta { display: flex; gap: 16px; padding-top: 8px; border-top: 1px dashed #e5e7eb; }
.meta-label { font-size: 12px; color: #6b7280; margin-right: 4px; }
.step-hint { font-size: 12px; color: #6b7280; }

.env-alert { margin-top: 12px; }
.env-info { font-size: 13px; }
.env-info p { margin: 4px 0; }

.debug-section { display: flex; flex-direction: column; gap: 16px; }
.debug-request h4, .debug-response h4 { margin: 0 0 10px 0; font-size: 14px; font-weight: 600; color: #374151; }
.debug-request-line { display: flex; gap: 8px; align-items: center; }
.debug-method { width: 100px; }
.debug-protocol { width: 100px; }
.debug-url { flex: 1; }
.debug-textarea { margin-top: 10px; }
.debug-env-hint { display: flex; align-items: center; gap: 6px; padding: 8px 12px; background: #ecfdf5; border-radius: 6px; font-size: 13px; color: #059669; margin: 10px 0; }

.response-display { border: 1px solid #e5e7eb; border-radius: 8px; overflow: hidden; }
.response-header-bar { display: flex; align-items: center; gap: 16px; padding: 10px 14px; background: #f9fafb; border-bottom: 1px solid #e5e7eb; }
.response-meta { color: #6b7280; font-size: 13px; }
.code-block { background: #1f2937; color: #e5e7eb; padding: 12px 16px; border-radius: 0; font-family: 'Menlo', 'Consolas', monospace; font-size: 12.5px; line-height: 1.6; max-height: 350px; overflow: auto; white-space: pre-wrap; word-break: break-all; margin: 0; }
.debug-error-state, .debug-empty { display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 40px 20px; color: #9ca3af; }
.error-title { color: #ef4444; font-weight: 600; margin: 12px 0 4px; }
.error-message { color: #6b7280; font-size: 13px; }

.env-toolbar { margin-bottom: 12px; }

@media (max-width: 768px) {
  .filter-bar { flex-direction: column; align-items: stretch; }
  .filter-item, .search-input { width: 100%; }
  .chart-wrap { display: none; }
}
</style>
