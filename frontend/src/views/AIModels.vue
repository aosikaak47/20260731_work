<template>
  <div class="ai-models-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-content">
        <div class="logo-section">
          <el-icon :size="36" class="logo-icon"><Cpu /></el-icon>
          <div class="title-block">
            <h1>AI模型管理</h1>
            <p class="subtitle">管理AI分析模型、训练和配置</p>
          </div>
        </div>
        <div class="header-actions">
          <el-button :icon="Refresh" :loading="loading" @click="loadModels">刷新</el-button>
        </div>
      </div>
    </div>

    <div class="main-container">
      <!-- 统计卡片 -->
      <div class="stats-grid">
        <div class="stat-card stat-total">
          <div class="stat-icon"><el-icon :size="24"><DataBoard /></el-icon></div>
          <div class="stat-body">
            <div class="stat-value">{{ stats.total }}</div>
            <div class="stat-label">模型总数</div>
          </div>
        </div>
        <div class="stat-card stat-active">
          <div class="stat-icon"><el-icon :size="24"><CircleCheckFilled /></el-icon></div>
          <div class="stat-body">
            <div class="stat-value">{{ stats.active }}</div>
            <div class="stat-label">已启用模型</div>
          </div>
        </div>
        <div class="stat-card stat-training">
          <div class="stat-icon"><el-icon :size="24"><Loading /></el-icon></div>
          <div class="stat-body">
            <div class="stat-value">{{ stats.training }}</div>
            <div class="stat-label">训练中模型</div>
          </div>
        </div>
        <div class="stat-card stat-accuracy">
          <div class="stat-icon"><el-icon :size="24"><TrendCharts /></el-icon></div>
          <div class="stat-body">
            <div class="stat-value">{{ stats.avgAccuracy }}%</div>
            <div class="stat-label">平均准确率</div>
          </div>
        </div>
      </div>

      <!-- 准确率分布图 -->
      <el-card v-if="models.length > 0" class="chart-card" shadow="never">
        <template #header>
          <div class="card-header">
            <el-icon><PieChart /></el-icon>
            <span>模型准确率与训练数据分布</span>
          </div>
        </template>
        <div ref="chartRef" class="chart-container"></div>
      </el-card>

      <!-- 加载状态 -->
      <div v-if="loading" class="loading-state">
        <el-icon :size="40" class="is-loading"><Loading /></el-icon>
        <p class="loading-text">正在加载模型列表...</p>
      </div>

      <!-- 空状态 -->
      <div v-if="!loading && models.length === 0" class="empty-state">
        <el-icon :size="64" class="empty-icon"><DataLine /></el-icon>
        <p class="empty-title">暂无AI模型</p>
        <p class="empty-desc">请先在系统中创建AI分析模型</p>
      </div>

      <!-- 模型列表 -->
      <div v-if="!loading && models.length > 0" class="models-grid">
        <div
          v-for="model in models"
          :key="model.id"
          class="model-card"
          :class="[`status-${model.status}`, `type-${model.type}`]"
        >
          <!-- 顶部状态条 -->
          <div class="card-top-bar"></div>

          <!-- 卡片头部 -->
          <div class="model-header">
            <div class="model-title-row">
              <div class="model-type-icon" :style="{ background: typeMeta(model.type).color }">
                <el-icon :size="20"><component :is="typeMeta(model.type).icon" /></el-icon>
              </div>
              <div class="model-title-block">
                <div class="model-name">
                  {{ model.name || '未命名模型' }}
                  <span class="model-version">v{{ model.version || '1.0.0' }}</span>
                </div>
                <div class="model-type-label">{{ typeMeta(model.type).label }}</div>
              </div>
              <el-tag
                :type="statusTagType(model.status)"
                effect="dark"
                size="small"
                :class="{ 'status-pulse': model.status === 'training' }"
              >
                {{ statusLabel(model.status) }}
              </el-tag>
            </div>
          </div>

          <!-- 训练中遮罩 -->
          <div v-if="model.status === 'training'" class="training-overlay">
            <el-icon :size="28" class="is-loading"><Loading /></el-icon>
            <span>训练中...</span>
            <el-progress
              :percentage="model._trainProgress || 0"
              :indeterminate="!model._trainProgress"
              :show-text="false"
              :stroke-width="6"
              class="train-progress"
            />
          </div>

          <!-- 主体内容 -->
          <div class="model-body" :class="{ 'is-training': model.status === 'training' }">
            <!-- 算法 + 训练数据 -->
            <div class="info-row">
              <div class="info-item">
                <span class="info-label">
                  <el-icon><Connection /></el-icon> 算法
                </span>
                <span class="info-value">{{ model.algorithm || '-' }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">
                  <el-icon><Files /></el-icon> 训练数据
                </span>
                <span class="info-value">{{ formatDataSize(model.training_data_size) }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">
                  <el-icon><Clock /></el-icon> 最近训练
                </span>
                <span class="info-value">{{ formatTime(model.last_trained_at) }}</span>
              </div>
            </div>

            <!-- 准确率大数字 -->
            <div class="accuracy-block">
              <div class="accuracy-number" :style="{ color: accuracyColor(model.accuracy) }">
                {{ formatAccuracy(model.accuracy) }}<span class="accuracy-unit">%</span>
              </div>
              <div class="accuracy-label">模型准确率</div>
            </div>

            <!-- 评估指标 -->
            <div class="metrics-block">
              <div class="metric-item">
                <div class="metric-head">
                  <span class="metric-name">精确率</span>
                  <span class="metric-val">{{ formatPercent(model.metrics?.precision) }}</span>
                </div>
                <el-progress
                  :percentage="toPercent(model.metrics?.precision)"
                  :color="metricColor(model.metrics?.precision)"
                  :stroke-width="6"
                  :show-text="false"
                />
              </div>
              <div class="metric-item">
                <div class="metric-head">
                  <span class="metric-name">召回率</span>
                  <span class="metric-val">{{ formatPercent(model.metrics?.recall) }}</span>
                </div>
                <el-progress
                  :percentage="toPercent(model.metrics?.recall)"
                  :color="metricColor(model.metrics?.recall)"
                  :stroke-width="6"
                  :show-text="false"
                />
              </div>
              <div class="metric-item">
                <div class="metric-head">
                  <span class="metric-name">F1分数</span>
                  <span class="metric-val">{{ formatPercent(model.metrics?.f1_score) }}</span>
                </div>
                <el-progress
                  :percentage="toPercent(model.metrics?.f1_score)"
                  :color="metricColor(model.metrics?.f1_score)"
                  :stroke-width="6"
                  :show-text="false"
                />
              </div>
              <div class="metric-item">
                <div class="metric-head">
                  <span class="metric-name">误报率</span>
                  <span class="metric-val">{{ formatPercent(model.metrics?.false_positive_rate) }}</span>
                </div>
                <el-progress
                  :percentage="toPercent(model.metrics?.false_positive_rate)"
                  :color="fprColor(model.metrics?.false_positive_rate)"
                  :stroke-width="6"
                  :show-text="false"
                />
              </div>
            </div>

            <!-- 特征列表 -->
            <div class="features-block" v-if="model.features && model.features.length">
              <div class="block-title">
                <el-icon><Key /></el-icon>
                <span>特征列表</span>
              </div>
              <div class="features-tags">
                <el-tag
                  v-for="(feature, idx) in model.features"
                  :key="idx"
                  size="small"
                  type="info"
                  effect="plain"
                  class="feature-tag"
                >
                  {{ feature }}
                </el-tag>
              </div>
            </div>

            <!-- 配置可折叠区 -->
            <el-collapse class="config-collapse">
              <el-collapse-item name="config">
                <template #title>
                  <div class="block-title collapse-title">
                    <el-icon><Setting /></el-icon>
                    <span>模型配置</span>
                  </div>
                </template>
                <div class="config-grid">
                  <div class="config-item">
                    <span class="config-key">learning_rate</span>
                    <span class="config-val">{{ model.config?.learning_rate ?? '-' }}</span>
                  </div>
                  <div class="config-item">
                    <span class="config-key">batch_size</span>
                    <span class="config-val">{{ model.config?.batch_size ?? '-' }}</span>
                  </div>
                  <div class="config-item">
                    <span class="config-key">epochs</span>
                    <span class="config-val">{{ model.config?.epochs ?? '-' }}</span>
                  </div>
                  <div class="config-item">
                    <span class="config-key">hidden_layers</span>
                    <span class="config-val">{{ formatHiddenLayers(model.config?.hidden_layers) }}</span>
                  </div>
                  <div class="config-item">
                    <span class="config-key">dropout</span>
                    <span class="config-val">{{ model.config?.dropout ?? '-' }}</span>
                  </div>
                </div>
              </el-collapse-item>
            </el-collapse>

            <!-- 操作按钮 -->
            <div class="model-actions">
              <el-button
                type="primary"
                size="small"
                :icon="VideoPlay"
                :loading="model._training"
                :disabled="model.status === 'training'"
                @click="handleTrain(model)"
              >
                {{ model.status === 'training' ? '训练中' : '训练模型' }}
              </el-button>
              <el-button size="small" :icon="Edit" @click="openEditDialog(model)">编辑</el-button>
              <el-button
                size="small"
                :type="model.status === 'active' ? 'danger' : 'success'"
                :icon="model.status === 'active' ? CircleClose : CircleCheck"
                :loading="model._toggling"
                :disabled="model.status === 'training'"
                @click="handleToggleStatus(model)"
              >
                {{ model.status === 'active' ? '禁用' : '启用' }}
              </el-button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 编辑对话框 -->
    <el-dialog
      v-model="editDialogVisible"
      title="编辑模型配置"
      width="520px"
      :close-on-click-modal="false"
      class="edit-dialog"
    >
      <el-form :model="editForm" label-width="110px" class="edit-form">
        <el-form-item label="学习率">
          <el-input-number
            v-model="editForm.learning_rate"
            :min="0"
            :max="1"
            :step="0.001"
            :precision="4"
            class="full-width"
          />
        </el-form-item>
        <el-form-item label="Batch Size">
          <el-input-number
            v-model="editForm.batch_size"
            :min="1"
            :max="1024"
            :step="1"
            class="full-width"
          />
        </el-form-item>
        <el-form-item label="训练轮数">
          <el-input-number
            v-model="editForm.epochs"
            :min="1"
            :max="1000"
            :step="1"
            class="full-width"
          />
        </el-form-item>
        <el-form-item label="Dropout">
          <el-slider
            v-model="editForm.dropout"
            :min="0"
            :max="1"
            :step="0.05"
            show-input
          />
        </el-form-item>
        <el-form-item label="阈值">
          <el-slider
            v-model="editForm.threshold"
            :min="0"
            :max="1"
            :step="0.01"
            show-input
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="editSaving" @click="handleSaveEdit">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onBeforeUnmount, nextTick, watch } from 'vue'
import * as echarts from 'echarts'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Cpu, Refresh, DataBoard, CircleCheckFilled, Loading, TrendCharts,
  PieChart, DataLine, Connection, Files, Clock, Key, Setting,
  VideoPlay, Edit, CircleClose, CircleCheck,
  Aim, MagicStick, DataAnalysis, Histogram, WarnTriangleFilled
} from '@element-plus/icons-vue'

// 模型类型元数据：图标 + 颜色 + 中文标签
const TYPE_META = {
  bottleneck_analysis: { label: '瓶颈分析', icon: Histogram, color: 'linear-gradient(135deg, #f5222d, #ff7875)' },
  anomaly_detection: { label: '异常检测', icon: WarnTriangleFilled, color: 'linear-gradient(135deg, #fa8c16, #ffa940)' },
  scenario_generation: { label: '场景生成', icon: MagicStick, color: 'linear-gradient(135deg, #722ed1, #9254de)' },
  predictive_analysis: { label: '预测分析', icon: TrendCharts, color: 'linear-gradient(135deg, #1890ff, #36cfc9)' },
  root_cause_analysis: { label: '根因分析', icon: Aim, color: 'linear-gradient(135deg, #13c2c2, #5cdbd3)' }
}

const models = ref([])
const loading = ref(false)
const chartRef = ref(null)
let chartInstance = null

// 编辑对话框
const editDialogVisible = ref(false)
const editSaving = ref(false)
const editingModelId = ref(null)
const editForm = reactive({
  learning_rate: 0.001,
  batch_size: 32,
  epochs: 100,
  dropout: 0.3,
  threshold: 0.5
})

// 统计数据
const stats = computed(() => {
  const list = models.value
  const total = list.length
  const active = list.filter(m => m.status === 'active').length
  const training = list.filter(m => m.status === 'training').length
  const accuracies = list
    .map(m => typeof m.accuracy === 'number' ? m.accuracy : parseFloat(m.accuracy))
    .filter(v => !isNaN(v))
  const avgAccuracy = accuracies.length
    ? Math.round(accuracies.reduce((a, b) => a + b, 0) / accuracies.length * 100) / 100
    : 0
  return { total, active, training, avgAccuracy }
})

// 工具函数
const typeMeta = (type) => TYPE_META[type] || { label: type || '未知', icon: DataAnalysis, color: 'linear-gradient(135deg, #8c8c8c, #bfbfbf)' }

const statusTagType = (status) => {
  const map = { active: 'success', training: 'warning', inactive: 'info' }
  return map[status] || 'info'
}

const statusLabel = (status) => {
  const map = { active: '运行中', training: '训练中', inactive: '已停用' }
  return map[status] || '未知'
}

const accuracyColor = (acc) => {
  const v = toPercent(acc)
  if (v > 90) return '#52c41a'
  if (v > 80) return '#1890ff'
  if (v > 70) return '#faad14'
  return '#f5222d'
}

const metricColor = (val) => {
  const v = toPercent(val)
  if (v > 90) return '#52c41a'
  if (v > 80) return '#1890ff'
  if (v > 70) return '#faad14'
  return '#f5222d'
}

const fprColor = (val) => {
  const v = toPercent(val)
  if (v < 5) return '#52c41a'
  if (v < 10) return '#1890ff'
  if (v < 20) return '#faad14'
  return '#f5222d'
}

const toPercent = (val) => {
  if (val === undefined || val === null || val === '') return 0
  const num = typeof val === 'string' ? parseFloat(val) : val
  if (isNaN(num)) return 0
  return num > 1 ? Math.round(num) : Math.round(num * 100)
}

const formatPercent = (val) => {
  const v = toPercent(val)
  return v + '%'
}

const formatAccuracy = (acc) => {
  if (acc === undefined || acc === null || acc === '') return '0'
  const num = typeof acc === 'string' ? parseFloat(acc) : acc
  if (isNaN(num)) return '0'
  return num > 1 ? num.toFixed(2) : (num * 100).toFixed(2)
}

const formatDataSize = (size) => {
  if (size === undefined || size === null || size === '') return '-'
  const num = typeof size === 'string' ? parseInt(size, 10) : size
  if (isNaN(num)) return String(size)
  if (num >= 1000000) return (num / 1000000).toFixed(2) + 'M 条'
  if (num >= 1000) return (num / 1000).toFixed(2) + 'K 条'
  return num + ' 条'
}

const formatTime = (time) => {
  if (!time) return '从未训练'
  try {
    const d = new Date(time)
    if (isNaN(d.getTime())) return String(time)
    return d.toLocaleString('zh-CN', { hour12: false })
  } catch (_) {
    return String(time)
  }
}

const formatHiddenLayers = (layers) => {
  if (layers === undefined || layers === null) return '-'
  if (Array.isArray(layers)) return layers.join(' / ')
  return String(layers)
}

// API 调用：加载模型列表
const loadModels = async () => {
  loading.value = true
  try {
    const res = await fetch('/api/v1/ai/models')
    const json = await res.json()
    const data = json.data || json
    const list = data.models || data || []
    models.value = list.map(m => ({ ...m, _training: false, _toggling: false, _trainProgress: 0 }))
    nextTick(() => initChart())
  } catch (e) {
    console.error('加载AI模型失败:', e)
    ElMessage.error('加载AI模型列表失败，请检查后端服务是否正常')
  } finally {
    loading.value = false
  }
}

// 训练模型
const handleTrain = async (model) => {
  try {
    await ElMessageBox.confirm(
      `确定要开始训练模型「${model.name}」吗？训练过程可能需要一些时间。`,
      '训练确认',
      { confirmButtonText: '开始训练', cancelButtonText: '取消', type: 'info' }
    )
  } catch (_) {
    return
  }

  model._training = true
  model.status = 'training'
  model._trainProgress = 5

  // 模拟训练进度动画
  const progressTimer = setInterval(() => {
    if (model._trainProgress < 90) {
      model._trainProgress += Math.random() * 10
    }
  }, 800)

  try {
    const res = await fetch(`/api/v1/ai/models/${model.id}/train`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' }
    })
    const json = await res.json()
    const data = json.data || json
    clearInterval(progressTimer)
    model._trainProgress = 100

    // 更新模型数据
    if (data && data.model) {
      Object.assign(model, data.model)
    }
    if (data && data.status) {
      model.status = data.status
    } else {
      model.status = 'active'
    }
    model.last_trained_at = data?.last_trained_at || new Date().toISOString()
    if (data?.accuracy !== undefined) model.accuracy = data.accuracy
    if (data?.metrics) model.metrics = data.metrics

    ElMessage.success(`模型「${model.name}」训练完成`)
    nextTick(() => initChart())
  } catch (e) {
    console.error('训练模型失败:', e)
    ElMessage.error('训练模型失败：' + (e.message || '请检查后端服务'))
    model.status = 'inactive'
  } finally {
    clearInterval(progressTimer)
    model._training = false
    setTimeout(() => { model._trainProgress = 0 }, 600)
  }
}

// 启用/禁用切换
const handleToggleStatus = async (model) => {
  model._toggling = true
  const targetStatus = model.status === 'active' ? 'inactive' : 'active'
  try {
    const res = await fetch(`/api/v1/ai/models/${model.id}/toggle-status`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' }
    })
    const json = await res.json()
    const data = json.data || json
    model.status = data.status || targetStatus
    ElMessage.success(`模型「${model.name}」已${model.status === 'active' ? '启用' : '停用'}`)
  } catch (e) {
    console.error('切换状态失败:', e)
    ElMessage.error('切换状态失败：' + (e.message || '请检查后端服务'))
  } finally {
    model._toggling = false
  }
}

// 打开编辑对话框
const openEditDialog = (model) => {
  editingModelId.value = model.id
  const cfg = model.config || {}
  editForm.learning_rate = cfg.learning_rate ?? 0.001
  editForm.batch_size = cfg.batch_size ?? 32
  editForm.epochs = cfg.epochs ?? 100
  editForm.dropout = cfg.dropout ?? 0.3
  editForm.threshold = cfg.threshold ?? model.threshold ?? 0.5
  editDialogVisible.value = true
}

// 保存编辑
const handleSaveEdit = async () => {
  editSaving.value = true
  try {
    const payload = {
      config: {
        learning_rate: editForm.learning_rate,
        batch_size: editForm.batch_size,
        epochs: editForm.epochs,
        dropout: editForm.dropout,
        threshold: editForm.threshold
      }
    }
    const res = await fetch(`/api/v1/ai/models/${editingModelId.value}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })
    const json = await res.json()
    const data = json.data || json

    // 本地同步更新
    const model = models.value.find(m => m.id === editingModelId.value)
    if (model) {
      model.config = { ...(model.config || {}), ...payload.config }
      if (data?.config) model.config = data.config
      if (data?.threshold !== undefined) model.threshold = data.threshold
    }

    ElMessage.success('模型配置已保存')
    editDialogVisible.value = false
  } catch (e) {
    console.error('保存模型配置失败:', e)
    ElMessage.error('保存失败：' + (e.message || '请检查后端服务'))
  } finally {
    editSaving.value = false
  }
}

// 初始化图表
const initChart = () => {
  if (!chartRef.value) return
  if (chartInstance) {
    chartInstance.dispose()
  }
  chartInstance = echarts.init(chartRef.value)

  const list = models.value
  const names = list.map(m => m.name || '未命名')
  const accuracies = list.map(m => toPercent(m.accuracy))
  const dataSizes = list.map(m => {
    const v = m.training_data_size
    const num = typeof v === 'string' ? parseInt(v, 10) : v
    return isNaN(num) ? 0 : num
  })

  chartInstance.setOption({
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' }
    },
    legend: {
      data: ['准确率(%)', '训练数据量(条)'],
      textStyle: { color: '#a0aec0' },
      top: '2%'
    },
    grid: { left: '3%', right: '6%', bottom: '8%', containLabel: true },
    xAxis: {
      type: 'category',
      data: names,
      axisLabel: { color: '#a0aec0', rotate: names.length > 4 ? 20 : 0, interval: 0 },
      axisLine: { lineStyle: { color: '#4a5568' } }
    },
    yAxis: [
      {
        type: 'value',
        name: '准确率(%)',
        nameTextStyle: { color: '#a0aec0' },
        min: 0,
        max: 100,
        axisLabel: { color: '#a0aec0', formatter: '{value}%' },
        axisLine: { lineStyle: { color: '#4a5568' } },
        splitLine: { lineStyle: { color: '#2d3748' } }
      },
      {
        type: 'value',
        name: '数据量(条)',
        nameTextStyle: { color: '#a0aec0' },
        axisLabel: { color: '#a0aec0' },
        axisLine: { lineStyle: { color: '#4a5568' } },
        splitLine: { show: false }
      }
    ],
    series: [
      {
        name: '准确率(%)',
        type: 'bar',
        barWidth: '30%',
        data: accuracies,
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#1890ff' },
            { offset: 1, color: '#36cfc9' }
          ]),
          borderRadius: [4, 4, 0, 0]
        }
      },
      {
        name: '训练数据量(条)',
        type: 'line',
        yAxisIndex: 1,
        data: dataSizes,
        smooth: true,
        symbol: 'circle',
        symbolSize: 8,
        lineStyle: { color: '#faad14', width: 2 },
        itemStyle: { color: '#faad14' }
      }
    ]
  })
}

const handleResize = () => {
  chartInstance?.resize()
}

watch(models, () => {
  nextTick(() => initChart())
}, { deep: true })

onMounted(() => {
  loadModels()
  window.addEventListener('resize', handleResize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  chartInstance?.dispose()
  chartInstance = null
})
</script>

<style scoped>
.ai-models-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #0f172a 0%, #1a2332 50%, #0f172a 100%);
  color: #e2e8f0;
  font-family: 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif;
}

/* 页面头部 */
.page-header {
  background: linear-gradient(135deg, #1e3a5f 0%, #0f172a 100%);
  border-bottom: 1px solid rgba(64, 169, 255, 0.2);
  padding: 28px 32px;
  position: relative;
  overflow: hidden;
}

.page-header::before {
  content: '';
  position: absolute;
  inset: 0;
  background:
    radial-gradient(circle at 20% 50%, rgba(24, 144, 255, 0.15) 0%, transparent 50%),
    radial-gradient(circle at 80% 50%, rgba(114, 46, 209, 0.12) 0%, transparent 50%);
  pointer-events: none;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  position: relative;
  z-index: 1;
  flex-wrap: wrap;
  gap: 16px;
}

.logo-section {
  display: flex;
  align-items: center;
  gap: 16px;
}

.logo-icon {
  color: #40a9ff;
  filter: drop-shadow(0 0 8px rgba(64, 169, 255, 0.6));
}

.title-block h1 {
  font-size: 26px;
  font-weight: 700;
  margin: 0;
  background: linear-gradient(90deg, #40a9ff, #69b1ff);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.subtitle {
  font-size: 13px;
  color: #8bb8e8;
  margin: 4px 0 0 0;
  opacity: 0.9;
}

.header-actions {
  display: flex;
  gap: 12px;
}

/* 主容器 */
.main-container {
  padding: 24px;
  max-width: 1600px;
  margin: 0 auto;
}

/* 统计卡片 */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 20px;
}

.stat-card {
  background: rgba(30, 42, 58, 0.7);
  border: 1px solid rgba(64, 169, 255, 0.15);
  border-radius: 12px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  backdrop-filter: blur(10px);
  transition: all 0.3s;
}

.stat-card:hover {
  transform: translateY(-2px);
  border-color: rgba(64, 169, 255, 0.4);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  flex-shrink: 0;
}

.stat-total .stat-icon { background: linear-gradient(135deg, #1890ff, #40a9ff); }
.stat-active .stat-icon { background: linear-gradient(135deg, #52c41a, #73d13d); }
.stat-training .stat-icon { background: linear-gradient(135deg, #fa8c16, #ffa940); }
.stat-accuracy .stat-icon { background: linear-gradient(135deg, #722ed1, #9254de); }

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #e2e8f0;
  line-height: 1.2;
}

.stat-label {
  font-size: 13px;
  color: #8bb8e8;
  margin-top: 4px;
}

/* 图表卡片 */
.chart-card {
  background: rgba(30, 42, 58, 0.7);
  border: 1px solid rgba(64, 169, 255, 0.15);
  border-radius: 12px;
  margin-bottom: 20px;
  backdrop-filter: blur(10px);
}

.chart-card :deep(.el-card__header) {
  padding: 14px 20px;
  border-bottom: 1px solid rgba(64, 169, 255, 0.1);
}

.chart-card :deep(.el-card__body) {
  padding: 16px 20px;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 15px;
  font-weight: 600;
  color: #e2e8f0;
}

.card-header .el-icon {
  color: #40a9ff;
}

.chart-container {
  width: 100%;
  height: 280px;
}

/* 加载 / 空状态 */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
  text-align: center;
  background: rgba(30, 42, 58, 0.5);
  border: 1px dashed rgba(64, 169, 255, 0.3);
  border-radius: 12px;
}

.loading-state .is-loading {
  color: #40a9ff;
  animation: spin 1.5s linear infinite;
  filter: drop-shadow(0 0 12px rgba(64, 169, 255, 0.5));
  margin-bottom: 16px;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.loading-text {
  font-size: 14px;
  color: #a0aec0;
  margin: 0;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
  text-align: center;
  background: rgba(30, 42, 58, 0.5);
  border: 1px dashed rgba(64, 169, 255, 0.3);
  border-radius: 12px;
}

.empty-icon {
  color: #2d4a6b;
  margin-bottom: 20px;
  filter: drop-shadow(0 0 12px rgba(64, 169, 255, 0.2));
}

.empty-title {
  font-size: 20px;
  font-weight: 600;
  color: #e2e8f0;
  margin: 0 0 8px 0;
}

.empty-desc {
  font-size: 13px;
  color: #a0aec0;
  margin: 0;
}

/* 模型列表网格 */
.models-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(420px, 1fr));
  gap: 20px;
}

.model-card {
  background: rgba(30, 42, 58, 0.7);
  border: 1px solid rgba(64, 169, 255, 0.15);
  border-radius: 12px;
  overflow: hidden;
  position: relative;
  transition: all 0.3s;
  backdrop-filter: blur(10px);
  display: flex;
  flex-direction: column;
}

.model-card:hover {
  transform: translateY(-2px);
  border-color: rgba(64, 169, 255, 0.4);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
}

.card-top-bar {
  height: 3px;
  width: 100%;
  background: linear-gradient(90deg, #1890ff, #36cfc9);
}

.status-active .card-top-bar { background: linear-gradient(90deg, #52c41a, #73d13d); }
.status-training .card-top-bar { background: linear-gradient(90deg, #fa8c16, #ffa940); }
.status-inactive .card-top-bar { background: linear-gradient(90deg, #8c8c8c, #bfbfbf); }

/* 模型头部 */
.model-header {
  padding: 18px 18px 12px;
  border-bottom: 1px solid rgba(64, 169, 255, 0.1);
}

.model-title-row {
  display: flex;
  align-items: center;
  gap: 12px;
}

.model-type-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  flex-shrink: 0;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

.model-title-block {
  flex: 1;
  min-width: 0;
}

.model-name {
  font-size: 16px;
  font-weight: 600;
  color: #e2e8f0;
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.model-version {
  font-size: 11px;
  color: #8bb8e8;
  background: rgba(64, 169, 255, 0.1);
  padding: 2px 8px;
  border-radius: 4px;
  font-weight: 500;
}

.model-type-label {
  font-size: 12px;
  color: #a0aec0;
  margin-top: 2px;
}

/* 训练状态标签脉冲 */
.status-pulse {
  animation: pulse 1.5s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

/* 训练中遮罩 */
.training-overlay {
  position: absolute;
  top: 60px;
  left: 18px;
  right: 18px;
  background: rgba(15, 23, 42, 0.85);
  border: 1px solid rgba(250, 173, 20, 0.3);
  border-radius: 10px;
  padding: 16px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  z-index: 2;
  backdrop-filter: blur(4px);
}

.training-overlay .is-loading {
  color: #faad14;
  animation: spin 1.5s linear infinite;
}

.training-overlay span {
  font-size: 13px;
  color: #faad14;
  font-weight: 600;
}

.train-progress {
  width: 100%;
}

/* 模型主体 */
.model-body {
  padding: 16px 18px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  transition: opacity 0.3s;
}

.model-body.is-training {
  opacity: 0.3;
  pointer-events: none;
}

/* 信息行 */
.info-row {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 10px;
  background: rgba(15, 23, 42, 0.5);
  border-radius: 8px;
}

.info-label {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 11px;
  color: #8bb8e8;
}

.info-value {
  font-size: 13px;
  color: #e2e8f0;
  font-weight: 500;
  word-break: break-all;
}

/* 准确率大数字 */
.accuracy-block {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 18px;
  background: rgba(15, 23, 42, 0.6);
  border-radius: 10px;
  border: 1px solid rgba(64, 169, 255, 0.1);
}

.accuracy-number {
  font-size: 42px;
  font-weight: 700;
  line-height: 1;
  font-family: 'Segoe UI', 'SF Mono', monospace;
  text-shadow: 0 0 20px currentColor;
}

.accuracy-unit {
  font-size: 20px;
  font-weight: 600;
  margin-left: 2px;
}

.accuracy-label {
  font-size: 12px;
  color: #8bb8e8;
  margin-top: 8px;
}

/* 评估指标 */
.metrics-block {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.metric-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.metric-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.metric-name {
  font-size: 12px;
  color: #8bb8e8;
}

.metric-val {
  font-size: 13px;
  font-weight: 600;
  color: #e2e8f0;
}

/* 区块标题 */
.block-title {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  font-weight: 600;
  color: #a0aec0;
  margin-bottom: 8px;
}

.block-title .el-icon {
  color: #40a9ff;
}

/* 特征标签 */
.features-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.feature-tag {
  font-size: 11px;
}

/* 配置折叠 */
.config-collapse {
  border: none;
  background: transparent;
}

.config-collapse :deep(.el-collapse-item__header) {
  background: transparent;
  border-bottom: 1px solid rgba(64, 169, 255, 0.1);
  color: #a0aec0;
  height: 36px;
  line-height: 36px;
}

.config-collapse :deep(.el-collapse-item__wrap) {
  background: transparent;
  border-bottom: none;
}

.config-collapse :deep(.el-collapse-item__content) {
  padding: 12px 0 0;
  color: #e2e8f0;
}

.collapse-title {
  margin-bottom: 0;
}

.config-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 8px;
}

.config-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background: rgba(15, 23, 42, 0.5);
  border-radius: 6px;
  font-size: 12px;
}

.config-key {
  color: #8bb8e8;
  font-family: 'SF Mono', Consolas, monospace;
}

.config-val {
  color: #40a9ff;
  font-weight: 600;
  font-family: 'SF Mono', Consolas, monospace;
}

/* 操作按钮 */
.model-actions {
  display: flex;
  gap: 8px;
  padding-top: 12px;
  border-top: 1px solid rgba(64, 169, 255, 0.1);
}

.model-actions .el-button {
  flex: 1;
}

/* 编辑对话框 */
.edit-dialog :deep(.el-dialog) {
  background: #1e2a3a;
  border: 1px solid rgba(64, 169, 255, 0.2);
  border-radius: 12px;
}

.edit-dialog :deep(.el-dialog__header) {
  border-bottom: 1px solid rgba(64, 169, 255, 0.1);
}

.edit-dialog :deep(.el-dialog__title) {
  color: #e2e8f0;
}

.edit-dialog :deep(.el-dialog__body) {
  color: #e2e8f0;
}

.edit-form .full-width {
  width: 100%;
}

/* Element Plus 暗色主题覆盖 */
.ai-models-page :deep(.el-card) {
  background: rgba(30, 42, 58, 0.7);
  border-color: rgba(64, 169, 255, 0.15);
  color: #e2e8f0;
}

.ai-models-page :deep(.el-input__wrapper),
.ai-models-page :deep(.el-input-number),
.ai-models-page :deep(.el-select__wrapper) {
  background-color: rgba(15, 23, 42, 0.6);
  box-shadow: 0 0 0 1px rgba(64, 169, 255, 0.2) inset;
}

.ai-models-page :deep(.el-input__inner) {
  color: #e2e8f0;
}

.ai-models-page :deep(.el-progress-bar__outer) {
  background-color: rgba(15, 23, 42, 0.6);
}

.ai-models-page :deep(.el-button--default) {
  background: rgba(64, 169, 255, 0.08);
  border-color: rgba(64, 169, 255, 0.3);
  color: #e2e8f0;
}

.ai-models-page :deep(.el-button--default:hover) {
  background: rgba(64, 169, 255, 0.15);
  border-color: rgba(64, 169, 255, 0.5);
  color: #40a9ff;
}

/* 响应式 */
@media (max-width: 1200px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    align-items: flex-start;
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }

  .models-grid {
    grid-template-columns: 1fr;
  }

  .info-row {
    grid-template-columns: 1fr;
  }

  .main-container {
    padding: 16px;
  }

  .chart-container {
    height: 240px;
  }
}
</style>
