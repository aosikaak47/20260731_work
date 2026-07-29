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
        <el-select
          v-model="filters.project_id"
          placeholder="选择项目"
          clearable
          class="filter-item"
        >
          <el-option v-for="p in projects" :key="p.id" :label="p.name" :value="p.id" />
        </el-select>
        <el-select v-model="filters.status" placeholder="状态" clearable class="filter-item">
          <el-option label="草稿" value="draft" />
          <el-option label="运行中" value="running" />
          <el-option label="已完成" value="completed" />
          <el-option label="待执行" value="pending" />
        </el-select>
        <el-input
          v-model="filters.keyword"
          placeholder="搜索测试名称 / URL"
          clearable
          class="search-input"
          @keyup.enter="loadTests"
        >
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

      <el-table
        v-loading="loading"
        :data="filteredTests"
        stripe
        border
        class="perf-table"
        empty-text="暂无性能测试数据"
      >
        <el-table-column type="index" label="#" width="55" align="center" />
        <el-table-column prop="name" label="名称" min-width="160" show-overflow-tooltip />
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
        <el-table-column prop="concurrency" label="并发" width="80" align="center" />
        <el-table-column prop="duration" label="持续时长" width="100" align="center">
          <template #default="scope">{{ scope.row.duration }}s</template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="110" align="center">
          <template #default="scope">
            <el-tag
              :type="statusTagType(scope.row.status)"
              :class="{ 'status-running': scope.row.status === 'running' }"
              size="small"
            >
              {{ statusLabel(scope.row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="priority" label="优先级" width="90" align="center">
          <template #default="scope">
            <el-tag :type="priorityTagType(scope.row.priority)" size="small" effect="plain">
              {{ priorityLabel(scope.row.priority) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="last_run" label="上次执行" width="160">
          <template #default="scope">
            <span v-if="scope.row.last_run">{{ scope.row.last_run }}</span>
            <span v-else class="text-muted">未执行</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="320" class-name="action-cell" fixed="right">
          <template #default="scope">
            <div class="action-btns">
              <el-button
                size="small"
                type="primary"
                :loading="executingId === scope.row.id"
                @click="handleExecute(scope.row)"
              >
                <el-icon v-if="executingId !== scope.row.id"><component :is="icons.VideoPlay" /></el-icon>
                执行
              </el-button>
              <el-button size="small" type="warning" @click="handleDebug(scope.row)">
                <el-icon><component :is="icons.Connection" /></el-icon>
                调试
              </el-button>
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

    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑测试' : '新建测试'"
      width="740px"
      :close-on-click-modal="false"
    >
      <el-form :model="form" label-width="100px" class="perf-form">
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
          <el-col :span="8">
            <el-form-item label="协议">
              <el-select v-model="form.protocol" style="width: 100%">
                <el-option label="HTTP" value="HTTP" />
                <el-option label="HTTPS" value="HTTPS" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="请求方法">
              <el-select v-model="form.method" style="width: 100%">
                <el-option label="GET" value="GET" />
                <el-option label="POST" value="POST" />
                <el-option label="PUT" value="PUT" />
                <el-option label="DELETE" value="DELETE" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="优先级">
              <el-select v-model="form.priority" style="width: 100%">
                <el-option label="高" value="high" />
                <el-option label="中" value="medium" />
                <el-option label="低" value="low" />
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
          <el-input
            v-model="form.headers"
            type="textarea"
            :rows="3"
            placeholder='{"Content-Type":"application/json","Authorization":"Bearer xxx"}'
          />
        </el-form-item>
        <el-form-item label="请求体">
          <el-input
            v-model="form.body"
            type="textarea"
            :rows="4"
            placeholder='{"username":"admin","password":"***"}'
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="handleSave">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="debugVisible" title="接口调试" width="850px" :close-on-click-modal="false">
      <div class="debug-container">
        <el-tabs v-model="debugActiveTab">
          <el-tab-pane label="请求配置" name="request">
            <div class="debug-request-config">
              <div class="request-line">
                <el-select v-model="debugForm.method" class="debug-method">
                  <el-option label="GET" value="GET" />
                  <el-option label="POST" value="POST" />
                  <el-option label="PUT" value="PUT" />
                  <el-option label="DELETE" value="DELETE" />
                  <el-option label="PATCH" value="PATCH" />
                </el-select>
                <el-select v-model="debugForm.protocol" class="debug-protocol">
                  <el-option label="HTTP" value="HTTP" />
                  <el-option label="HTTPS" value="HTTPS" />
                </el-select>
                <el-input v-model="debugForm.target_url" placeholder="目标URL" class="debug-url" />
              </div>
              
              <el-divider />
              
              <div class="request-section">
                <h4>请求头 (JSON格式)</h4>
                <el-input
                  v-model="debugForm.headers"
                  type="textarea"
                  :rows="4"
                  placeholder='{"Content-Type": "application/json", "Authorization": "Bearer xxx"}'
                />
              </div>
              
              <div class="request-section" v-if="['POST', 'PUT', 'PATCH'].includes(debugForm.method)">
                <h4>请求体</h4>
                <el-input
                  v-model="debugForm.body"
                  type="textarea"
                  :rows="6"
                  placeholder='{"key": "value"}'
                />
              </div>
              
              <div class="debug-actions">
                <el-button type="primary" @click="runDebug" :loading="debugLoading">
                  <el-icon><component :is="icons.Promotion" /></el-icon>
                  发送请求
                </el-button>
                <el-button @click="resetDebugForm">重置</el-button>
              </div>
            </div>
          </el-tab-pane>
          
          <el-tab-pane label="响应结果" name="response">
            <div class="debug-response">
              <div v-if="debugResult" class="response-result">
                <div class="response-header">
                  <el-tag 
                    :type="debugResult.status_code >= 200 && debugResult.status_code < 300 ? 'success' : 'danger'"
                    size="large"
                  >
                    {{ debugResult.status_code }} {{ debugResult.status_text }}
                  </el-tag>
                  <span class="response-time">耗时: {{ debugResult.time }}ms</span>
                  <span class="response-size">大小: {{ formatSize(debugResult.size) }}</span>
                </div>
                
                <el-divider />
                
                <div class="response-section">
                  <h4>响应头</h4>
                  <el-table :data="debugHeaders" size="small" border stripe max-height="200">
                    <el-table-column prop="key" label="Header" width="200" />
                    <el-table-column prop="value" label="Value" show-overflow-tooltip />
                  </el-table>
                </div>
                
                <div class="response-section">
                  <h4>响应体</h4>
                  <pre class="code-block">{{ formatResponse(debugResult.body, debugResult.body_type) }}</pre>
                </div>
              </div>
              <div v-else-if="debugError" class="debug-error">
                <el-icon :size="48" color="#F56C6C"><component :is="icons.Warning" /></el-icon>
                <p class="error-title">请求失败</p>
                <p class="error-message">{{ debugError }}</p>
              </div>
              <div v-else class="empty-response">
                <el-icon :size="48" color="#909399"><component :is="icons.Document" /></el-icon>
                <p>点击"发送请求"查看响应结果</p>
              </div>
            </div>
          </el-tab-pane>
        </el-tabs>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted, nextTick } from 'vue'
import * as echarts from 'echarts'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useProjects } from '../composables/useProjects'
import {
  Plus, Search, Refresh, Delete, Edit, VideoPlay,
  DataLine, Lightning, Odometer, Document,
  Connection, Promotion, Warning
} from '@element-plus/icons-vue'

const icons = {
  Plus, Search, Refresh, Delete, Edit, VideoPlay,
  DataLine, Lightning, Odometer, Document,
  Connection, Promotion, Warning
}

const { projects, loadProjects } = useProjects()

const tests = ref([])
const loading = ref(false)
const saving = ref(false)
const executingId = ref(null)
const stats = ref({ total: 0, running: 0, completed: 0, draft: 0 })

const filters = reactive({
  project_id: '',
  status: '',
  keyword: ''
})

const dialogVisible = ref(false)
const isEdit = ref(false)
const editingId = ref(null)

const debugVisible = ref(false)
const debugActiveTab = ref('request')
const debugLoading = ref(false)
const debugResult = ref(null)
const debugError = ref('')
const debugTestId = ref(null)

const defaultDebugForm = () => ({
  method: 'GET',
  protocol: 'HTTPS',
  target_url: '',
  headers: '{\n  "Content-Type": "application/json"\n}',
  body: ''
})

const debugForm = reactive(defaultDebugForm())

const debugHeaders = computed(() => {
  if (!debugResult.value?.headers) return []
  return Object.entries(debugResult.value.headers).map(([key, value]) => ({
    key,
    value: String(value)
  }))
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
  tags: '',
  headers: '',
  body: ''
})

const form = reactive(defaultForm())

const statsCards = computed(() => [
  { key: 'total', title: '测试总数', value: stats.value.total, icon: icons.DataLine, color: '#6366f1' },
  { key: 'running', title: '运行中', value: stats.value.running, icon: icons.Lightning, color: '#ef4444' },
  { key: 'completed', title: '已完成', value: stats.value.completed, icon: icons.Odometer, color: '#10b981' },
  { key: 'draft', title: '草稿', value: stats.value.draft, icon: icons.Document, color: '#6b7280' }
])

const filteredTests = computed(() => {
  let list = tests.value
  if (filters.status) {
    list = list.filter(t => t.status === filters.status)
  }
  if (filters.project_id) {
    list = list.filter(t => String(t.project_id) === String(filters.project_id))
  }
  if (filters.keyword) {
    const kw = filters.keyword.toLowerCase()
    list = list.filter(t =>
      (t.name && t.name.toLowerCase().includes(kw)) ||
      (t.target_url && t.target_url.toLowerCase().includes(kw))
    )
  }
  return list
})

const statusLabel = (s) => ({
  draft: '草稿', running: '运行中', completed: '已完成', pending: '待执行'
}[s] || s || '-')

const statusTagType = (s) => ({
  draft: 'info', pending: 'warning', running: 'danger', completed: 'success'
}[s] || 'info')

const priorityLabel = (p) => ({ high: '高', medium: '中', low: '低' }[p] || p || '-')

const priorityTagType = (p) => ({
  high: 'danger', medium: 'warning', low: 'info'
}[p] || 'info')

const methodTagType = (m) => ({
  GET: 'success', POST: 'primary', PUT: 'warning', DELETE: 'danger'
}[m] || 'info')

const loadTests = async () => {
  loading.value = true
  try {
    const res = await fetch('/api/v1/perf/tests')
    const json = await res.json()
    const data = json.data || json
    tests.value = data.tests || []
  } catch (e) {
    console.error('加载性能测试列表失败:', e)
    ElMessage.error('加载测试列表失败')
  } finally {
    loading.value = false
  }
}

const loadDashboard = async () => {
  try {
    const res = await fetch('/api/v1/perf/dashboard')
    const json = await res.json()
    const data = json.data || json
    const s = data.stats || data
    stats.value = {
      total: Number(s.total ?? 0),
      running: Number(s.running ?? 0),
      completed: Number(s.completed ?? 0),
      draft: Number(s.draft ?? 0)
    }
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
      name: '测试状态',
      type: 'pie',
      radius: ['42%', '68%'],
      center: ['50%', '42%'],
      avoidLabelOverlap: false,
      itemStyle: { borderRadius: 6, borderColor: '#fff', borderWidth: 2 },
      label: { show: false },
      emphasis: { label: { show: true, fontSize: 13, fontWeight: 'bold' } },
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

const resetFilters = () => {
  filters.project_id = ''
  filters.status = ''
  filters.keyword = ''
  loadTests()
}

const resetForm = () => {
  Object.assign(form, defaultForm())
}

const handleAdd = () => {
  isEdit.value = false
  editingId.value = null
  resetForm()
  if (projects.value.length && !form.project_id) {
    form.project_id = projects.value[0].id
  }
  dialogVisible.value = true
}

const handleEdit = (row) => {
  isEdit.value = true
  editingId.value = row.id
  Object.assign(form, defaultForm(), row)
  if (Array.isArray(row.tags)) {
    form.tags = row.tags.join(',')
  }
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
    if (payload.tags && typeof payload.tags === 'string') {
      payload.tags = payload.tags.split(',').map(s => s.trim()).filter(Boolean)
    }
    const url = isEdit.value ? `/api/v1/perf/tests/${editingId.value}` : '/api/v1/perf/tests'
    const method = isEdit.value ? 'PUT' : 'POST'
    const res = await fetch(url, {
      method,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })
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
    console.error('保存性能测试失败:', e)
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

const handleExecute = async (row) => {
  try {
    await ElMessageBox.confirm(`确定要执行性能测试「${row.name}」吗？`, '确认执行', {
      confirmButtonText: '执行',
      cancelButtonText: '取消',
      type: 'info'
    })
  } catch {
    return
  }
  executingId.value = row.id
  try {
    const res = await fetch(`/api/v1/perf/tests/${row.id}/execute`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' }
    })
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
    console.error('执行性能测试失败:', e)
    ElMessage.error('执行失败')
  } finally {
    executingId.value = null
  }
}

const handleDelete = (row) => {
  ElMessageBox.confirm(`确定要删除性能测试「${row.name}」吗？此操作不可恢复。`, '确认删除', {
    confirmButtonText: '删除',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
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
    } catch (e) {
      console.error('删除性能测试失败:', e)
      ElMessage.error('删除失败')
    }
  }).catch(() => {})
}

const handleDebug = (row) => {
  debugTestId.value = row.id
  debugResult.value = null
  debugError.value = ''
  debugActiveTab.value = 'request'
  
  Object.assign(debugForm, {
    method: row.method || 'GET',
    protocol: row.protocol || 'HTTPS',
    target_url: row.target_url || '',
    headers: row.headers || '{\n  "Content-Type": "application/json"\n}',
    body: row.body || ''
  })
  
  debugVisible.value = true
}

const resetDebugForm = () => {
  Object.assign(debugForm, defaultDebugForm())
  debugResult.value = null
  debugError.value = ''
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
    const res = await fetch(`/api/v1/perf/tests/${debugTestId.value}/debug`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        method: debugForm.method,
        protocol: debugForm.protocol,
        target_url: debugForm.target_url,
        headers: debugForm.headers,
        body: debugForm.body
      })
    })
    
    const json = await res.json()
    
    if (json.success) {
      debugResult.value = json.response
      debugActiveTab.value = 'response'
      ElMessage.success(`请求成功，状态码: ${json.response.status_code}`)
    } else {
      debugError.value = json.error || '请求失败'
      debugActiveTab.value = 'response'
      ElMessage.error(debugError.value)
    }
  } catch (e) {
    console.error('调试请求失败:', e)
    debugError.value = '网络错误或请求超时'
    debugActiveTab.value = 'response'
  } finally {
    debugLoading.value = false
  }
}

const formatResponse = (body, bodyType) => {
  if (!body) return '(空)'
  if (bodyType === 'json' && typeof body === 'object') {
    try {
      return JSON.stringify(body, null, 2)
    } catch {
      return String(body)
    }
  }
  if (typeof body === 'object') {
    try {
      return JSON.stringify(body, null, 2)
    } catch {
      return String(body)
    }
  }
  return String(body)
}

const formatSize = (bytes) => {
  if (!bytes) return '0 B'
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(2)} KB`
  return `${(bytes / 1024 / 1024).toFixed(2)} MB`
}

onMounted(async () => {
  await loadProjects()
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
.perf-tests {
  padding: 20px;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
  flex-wrap: wrap;
  gap: 16px;
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

.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.stats-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.stat-card {
  border: 1px solid #e5e7eb;
  border-left: 4px solid #6366f1;
  background: linear-gradient(135deg, #ffffff 0%, #f5f7ff 100%);
  transition: transform 0.2s, box-shadow 0.2s;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(99, 102, 241, 0.15);
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-icon {
  width: 52px;
  height: 52px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.stat-value {
  font-size: 26px;
  font-weight: 700;
  color: #1f2937;
  line-height: 1.2;
}

.stat-title {
  font-size: 13px;
  color: #6b7280;
  margin-top: 4px;
}

.main-card {
  border: 1px solid #e5e7eb;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.card-title {
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
}

.chart-wrap {
  width: 220px;
  height: 96px;
}

.status-chart {
  width: 100%;
  height: 100%;
}

.filter-bar {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
  flex-wrap: wrap;
  align-items: center;
}

.filter-item {
  width: 180px;
}

.search-input {
  width: 260px;
}

.url-text {
  color: #4b5563;
  font-family: 'Menlo', 'Consolas', monospace;
  font-size: 12.5px;
}

.text-muted {
  color: #9ca3af;
}

.perf-table :deep(.el-table__row:hover) > td {
  background-color: rgba(99, 102, 241, 0.06) !important;
}

.status-running {
  animation: running-pulse 1.2s infinite;
}

@keyframes running-pulse {
  0% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.55); }
  70% { box-shadow: 0 0 0 6px rgba(239, 68, 68, 0); }
  100% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0); }
}

.perf-form :deep(.el-input-number) {
  width: 100%;
}

.debug-container {
  padding: 0;
}

.debug-request-config {
  padding: 10px 0;
}

.request-line {
  display: flex;
  gap: 8px;
  align-items: center;
}

.debug-method {
  width: 120px;
}

.debug-protocol {
  width: 110px;
}

.debug-url {
  flex: 1;
}

.request-section {
  margin-bottom: 16px;
}

.request-section h4 {
  margin: 0 0 8px 0;
  font-size: 13px;
  font-weight: 600;
  color: #374151;
}

.debug-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  margin-top: 16px;
}

.debug-response {
  min-height: 200px;
}

.response-result {
  width: 100%;
}

.response-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 8px;
}

.response-time,
.response-size {
  color: #6b7280;
  font-size: 13px;
}

.response-section {
  margin-bottom: 16px;
}

.response-section h4 {
  margin: 0 0 8px 0;
  font-size: 13px;
  font-weight: 600;
  color: #374151;
}

.code-block {
  background: #1f2937;
  color: #e5e7eb;
  padding: 12px 16px;
  border-radius: 8px;
  font-family: 'Menlo', 'Consolas', 'Monaco', monospace;
  font-size: 12.5px;
  line-height: 1.6;
  max-height: 350px;
  overflow: auto;
  white-space: pre-wrap;
  word-break: break-all;
  margin: 0;
}

.empty-response,
.debug-error {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  color: #9ca3af;
}

.error-title {
  color: #ef4444;
  font-weight: 600;
  margin: 12px 0 4px;
}

.error-message {
  color: #6b7280;
  font-size: 13px;
}

@media (max-width: 768px) {
  .filter-bar {
    flex-direction: column;
    align-items: stretch;
  }
  .filter-item,
  .search-input {
    width: 100%;
  }
  .chart-wrap {
    display: none;
  }
}
</style>
