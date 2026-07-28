<template>
  <div class="ai-scenario">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-content">
        <div class="logo-section">
          <el-icon :size="36" class="logo-icon"><component :is="icons.MagicStick" /></el-icon>
          <div class="title-block">
            <h1>智能场景生成</h1>
            <p class="subtitle">基于AI模型自动生成性能测试场景</p>
          </div>
        </div>
        <div class="header-stats">
          <div class="header-stat">
            <span class="stat-num">{{ scenarios.length }}</span>
            <span class="stat-label">已生成</span>
          </div>
          <div class="header-stat">
            <span class="stat-num high">{{ highPriorityCount }}</span>
            <span class="stat-label">高优先级</span>
          </div>
          <div class="header-stat">
            <span class="stat-num">{{ avgConfidence }}%</span>
            <span class="stat-label">平均置信度</span>
          </div>
        </div>
      </div>
    </div>

    <div class="main-container">
      <!-- 配置面板 -->
      <div class="config-panel">
        <el-card class="config-card" shadow="never">
          <div class="card-header">
            <el-icon class="header-icon"><component :is="icons.SetUp" /></el-icon>
            <span class="card-title">场景生成配置</span>
          </div>
          <div class="config-row">
            <div class="config-item">
              <span class="control-label">
                <el-icon><component :is="icons.Folder" /></el-icon>
                选择项目
              </span>
              <el-select
                v-model="form.project_id"
                placeholder="请选择项目"
                class="config-select"
                filterable
                clearable
              >
                <el-option
                  v-for="project in projects"
                  :key="project.id"
                  :label="project.name"
                  :value="project.id"
                />
              </el-select>
            </div>

            <div class="config-item">
              <span class="control-label">
                <el-icon><component :is="icons.Aim" /></el-icon>
                目标类型
              </span>
              <el-select v-model="form.target_type" placeholder="请选择目标类型" class="config-select">
                <el-option label="API测试" value="API测试" />
                <el-option label="业务流程" value="业务流程" />
                <el-option label="混合场景" value="混合场景" />
              </el-select>
            </div>

            <div class="config-item">
              <span class="control-label">
                <el-icon><component :is="icons.Lightning" /></el-icon>
                压测强度
              </span>
              <el-select v-model="form.intensity" placeholder="请选择压测强度" class="config-select">
                <el-option
                  v-for="opt in intensityOptions"
                  :key="opt.value"
                  :label="opt.label"
                  :value="opt.value"
                >
                  <span style="float: left">{{ opt.label }}</span>
                  <span class="intensity-desc">{{ opt.desc }}</span>
                </el-option>
              </el-select>
            </div>

            <el-button
              type="primary"
              class="generate-btn"
              :loading="generating"
              :disabled="!canGenerate || generating"
              @click="handleGenerate"
            >
              <el-icon v-if="!generating"><component :is="icons.MagicStick" /></el-icon>
              {{ generating ? 'AI生成中...' : '生成场景' }}
            </el-button>
          </div>
          <div v-if="!canGenerate" class="config-hint">
            <el-icon><component :is="icons.InfoFilled" /></el-icon>
            <span>请选择项目、目标类型和压测强度后再生成场景</span>
          </div>
        </el-card>
      </div>

      <!-- 空状态占位 -->
      <div v-if="!generating && scenarios.length === 0" class="empty-state">
        <el-icon :size="80" class="empty-icon"><component :is="icons.DataAnalysis" /></el-icon>
        <h2 class="empty-title">等待AI生成场景</h2>
        <p class="empty-desc">请完成上方配置后，点击「生成场景」按钮</p>
        <p class="empty-subdesc">AI引擎将根据项目特征自动生成多组性能测试场景方案</p>
      </div>

      <!-- 加载状态 -->
      <div v-if="generating" class="loading-state">
        <div class="loading-card">
          <div class="loading-spinner">
            <el-icon :size="56" class="is-loading"><component :is="icons.Loading" /></el-icon>
          </div>
          <h3 class="loading-title">AI引擎正在生成测试场景</h3>
          <p class="loading-desc">正在分析项目特征、计算场景参数、生成测试方案...</p>
          <el-progress
            :percentage="100"
            status="success"
            :indeterminate="true"
            :duration="2"
            :show-text="false"
            class="loading-progress"
          />
        </div>
      </div>

      <!-- 生成结果 -->
      <div v-if="!generating && scenarios.length > 0" class="result-section">
        <!-- 统计概览 + 模型信息 -->
        <div class="overview-section">
          <!-- 统计概览 -->
          <el-card class="info-card stats-card" shadow="never">
            <div class="card-header">
              <el-icon class="header-icon"><component :is="icons.DataLine" /></el-icon>
              <span class="card-title">生成统计</span>
            </div>
            <div class="stats-grid">
              <div class="stat-box">
                <div class="stat-box-num">{{ scenarios.length }}</div>
                <div class="stat-box-label">场景总数</div>
              </div>
              <div class="stat-box high">
                <div class="stat-box-num">{{ highPriorityCount }}</div>
                <div class="stat-box-label">高优先级</div>
              </div>
              <div class="stat-box">
                <div class="stat-box-num">{{ avgConfidence }}%</div>
                <div class="stat-box-label">平均置信度</div>
              </div>
            </div>
          </el-card>

          <!-- 可视化图表 -->
          <el-card class="info-card chart-card" shadow="never">
            <div class="card-header">
              <el-icon class="header-icon"><component :is="icons.PieChart" /></el-icon>
              <span class="card-title">场景分布</span>
            </div>
            <div ref="chartRef" class="chart-container"></div>
          </el-card>

          <!-- 模型信息 -->
          <el-card class="info-card model-card" shadow="never">
            <div class="card-header">
              <el-icon class="header-icon"><component :is="icons.Cpu" /></el-icon>
              <span class="card-title">模型信息</span>
            </div>
            <div class="model-info">
              <div class="info-row">
                <span class="info-label">使用模型</span>
                <span class="info-value model-name">
                  <el-icon><component :is="icons.Connection" /></el-icon>
                  {{ modelInfo.model_used || 'AI-Engine-v1.0' }}
                </span>
              </div>
              <div class="info-row">
                <span class="info-label">生成时间</span>
                <span class="info-value">
                  <el-icon><component :is="icons.Timer" /></el-icon>
                  {{ formatTime(modelInfo.generated_at) }}
                </span>
              </div>
              <div class="info-row">
                <span class="info-label">场景数量</span>
                <span class="info-value">
                  <el-icon><component :is="icons.Files" /></el-icon>
                  {{ modelInfo.total || scenarios.length }} 个
                </span>
              </div>
            </div>
          </el-card>
        </div>

        <!-- 场景列表标题 -->
        <div class="section-title-bar">
          <el-icon><component :is="icons.List" /></el-icon>
          <h2 class="section-title">生成场景列表</h2>
          <el-tag effect="dark" size="small">共 {{ scenarios.length }} 个</el-tag>
        </div>

        <!-- 场景卡片网格 -->
        <div class="scenarios-grid">
          <div
            v-for="(scenario, index) in scenarios"
            :key="index"
            class="scenario-card"
            :class="priorityClass(scenario.priority)"
          >
            <div class="scenario-top-bar"></div>

            <!-- 卡片头部 -->
            <div class="scenario-header">
              <div class="scenario-name-block">
                <el-icon class="scenario-icon"><component :is="icons.Document" /></el-icon>
                <div class="name-text">
                  <span class="scenario-name">{{ scenario.name || `场景 ${index + 1}` }}</span>
                  <span class="scenario-type">{{ scenario.type || form.target_type }}</span>
                </div>
              </div>
              <div class="scenario-tags">
                <el-tag
                  :type="intensityTagType(scenario.intensity)"
                  effect="dark"
                  size="small"
                >
                  {{ scenario.intensity || form.intensity }}
                </el-tag>
                <el-tag
                  :type="priorityTagType(scenario.priority)"
                  effect="dark"
                  size="small"
                >
                  {{ priorityLabel(scenario.priority) }}
                </el-tag>
              </div>
            </div>

            <!-- 参数指标 -->
            <div class="scenario-metrics">
              <div class="metric-item">
                <span class="metric-label">并发</span>
                <span class="metric-value">{{ scenario.concurrency ?? '-' }}</span>
              </div>
              <div class="metric-item">
                <span class="metric-label">爬坡(s)</span>
                <span class="metric-value">{{ scenario.ramp_up ?? '-' }}</span>
              </div>
              <div class="metric-item">
                <span class="metric-label">时长(s)</span>
                <span class="metric-value">{{ scenario.duration ?? '-' }}</span>
              </div>
              <div class="metric-item">
                <span class="metric-label">思考(ms)</span>
                <span class="metric-value">{{ scenario.think_time ?? '-' }}</span>
              </div>
            </div>

            <!-- 目标接口 -->
            <div class="scenario-target">
              <div class="target-label">
                <el-icon><component :is="icons.Link" /></el-icon>
                <span>目标接口</span>
              </div>
              <div class="target-content">
                <el-tag
                  :type="methodTagType(scenario.method)"
                  effect="dark"
                  size="small"
                  class="method-tag"
                >
                  {{ (scenario.method || 'GET').toUpperCase() }}
                </el-tag>
                <span class="target-url" :title="scenario.target_url">{{ scenario.target_url || '-' }}</span>
              </div>
            </div>

            <!-- AI推理 -->
            <div v-if="scenario.reasoning || scenario.ai_reasoning" class="scenario-reasoning">
              <div class="reasoning-header">
                <el-icon class="reasoning-icon"><component :is="icons.MagicStick" /></el-icon>
                <span class="reasoning-label">AI推理</span>
              </div>
              <p class="reasoning-text">{{ scenario.reasoning || scenario.ai_reasoning }}</p>
            </div>

            <!-- 置信度 -->
            <div class="scenario-confidence">
              <div class="confidence-header">
                <span class="confidence-label">置信度</span>
                <span class="confidence-value" :style="{ color: confidenceColor(scenario.confidence) }">
                  {{ confidencePercent(scenario.confidence) }}%
                </span>
              </div>
              <el-progress
                :percentage="confidencePercent(scenario.confidence)"
                :color="confidenceColor(scenario.confidence)"
                :stroke-width="10"
                :show-text="false"
                class="confidence-bar"
              />
            </div>

            <!-- 操作按钮 -->
            <div class="scenario-footer">
              <el-button
                type="primary"
                class="import-btn"
                :loading="importingId === getScenarioKey(scenario, index)"
                :disabled="importedKeys.includes(getScenarioKey(scenario, index))"
                @click="handleImport(scenario, index)"
              >
                <el-icon v-if="importedKeys.includes(getScenarioKey(scenario, index))">
                  <component :is="icons.Check" />
                </el-icon>
                <el-icon v-else><component :is="icons.Download" /></el-icon>
                {{ importedKeys.includes(getScenarioKey(scenario, index)) ? '已导入' : '导入为测试' }}
              </el-button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, nextTick } from 'vue'
import * as echarts from 'echarts'
import { ElMessage } from 'element-plus'
import * as icons from '@element-plus/icons-vue'
import { useProjects } from '../composables/useProjects'

const { projects, loadProjects } = useProjects()

const form = ref({
  project_id: '',
  target_type: 'API测试',
  intensity: '中强度'
})

const intensityOptions = [
  { value: '低强度', label: '低强度', desc: '并发 ~20' },
  { value: '中强度', label: '中强度', desc: '并发 ~100' },
  { value: '高强度', label: '高强度', desc: '并发 ~300' },
  { value: '极限', label: '极限', desc: '并发 ~500' }
]

const generating = ref(false)
const scenarios = ref([])
const modelInfo = ref({ model_used: '', generated_at: '', total: 0 })
const importingId = ref(null)
const importedKeys = ref([])

const chartRef = ref(null)
let chart = null

const canGenerate = computed(() => {
  return !!(form.value.project_id && form.value.target_type && form.value.intensity)
})

const highPriorityCount = computed(() => {
  return scenarios.value.filter(s => {
    const p = (s.priority || '').toLowerCase()
    return p === 'high' || p === '高' || p === 'critical'
  }).length
})

const avgConfidence = computed(() => {
  if (scenarios.value.length === 0) return 0
  const total = scenarios.value.reduce((sum, s) => sum + confidencePercent(s.confidence), 0)
  return Math.round(total / scenarios.value.length)
})

const confidencePercent = (val) => {
  if (val === undefined || val === null || val === '') return 0
  const num = typeof val === 'string' ? parseFloat(val) : Number(val)
  if (isNaN(num)) return 0
  return num > 1 ? Math.round(num) : Math.round(num * 100)
}

const confidenceColor = (val) => {
  const p = confidencePercent(val)
  if (p > 90) return '#52c41a'
  if (p > 80) return '#1890ff'
  if (p > 70) return '#fadb14'
  return '#f5222d'
}

const priorityLabel = (priority) => {
  const p = (priority || '').toLowerCase()
  const map = { high: '高优先级', critical: '高优先级', medium: '中优先级', low: '低优先级', 高: '高优先级', 中: '中优先级', 低: '低优先级' }
  return map[p] || '中优先级'
}

const priorityTagType = (priority) => {
  const p = (priority || '').toLowerCase()
  if (p === 'high' || p === 'critical' || p === '高') return 'danger'
  if (p === 'medium' || p === '中') return 'warning'
  return 'info'
}

const priorityClass = (priority) => {
  const p = (priority || '').toLowerCase()
  if (p === 'high' || p === 'critical' || p === '高') return 'priority-high'
  if (p === 'medium' || p === '中') return 'priority-medium'
  return 'priority-low'
}

const intensityTagType = (intensity) => {
  const i = (intensity || '').toLowerCase()
  if (i.includes('极限') || i.includes('extreme') || i.includes('高')) return 'danger'
  if (i.includes('中')) return 'warning'
  return 'success'
}

const methodTagType = (method) => {
  const m = (method || 'GET').toUpperCase()
  if (m === 'GET') return 'success'
  if (m === 'POST') return 'primary'
  if (m === 'PUT' || m === 'PATCH') return 'warning'
  if (m === 'DELETE') return 'danger'
  return 'info'
}

const formatTime = (time) => {
  if (!time) return '-'
  try {
    const d = new Date(time)
    if (isNaN(d.getTime())) return String(time)
    return d.toLocaleString('zh-CN')
  } catch (_) {
    return String(time)
  }
}

const getScenarioKey = (scenario, index) => {
  return scenario.id || `${index}-${scenario.name || ''}`
}

const handleGenerate = async () => {
  if (!canGenerate.value) {
    ElMessage.warning('请完成配置后再生成场景')
    return
  }
  generating.value = true
  scenarios.value = []
  modelInfo.value = { model_used: '', generated_at: '', total: 0 }
  try {
    const response = await fetch('/api/v1/perf/ai/generate-scenario', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        project_id: form.value.project_id,
        target_type: form.value.target_type,
        intensity: form.value.intensity
      })
    })
    if (!response.ok) {
      let errorDetail = `HTTP ${response.status}`
      try {
        const errorData = await response.json()
        errorDetail = errorData.detail || errorData.message || errorData.error || errorDetail
      } catch (_) {}
      throw new Error(errorDetail)
    }
    const data = await response.json()
    if (data.success) {
      scenarios.value = data.scenarios || []
      modelInfo.value = {
        model_used: data.model_used || 'AI-Engine-v1.0',
        generated_at: data.generated_at || '',
        total: data.total || scenarios.value.length
      }
      importedKeys.value = []
      if (scenarios.value.length === 0) {
        ElMessage.info('AI生成完成，但未生成任何场景')
      } else {
        ElMessage.success(`AI生成完成，共生成 ${scenarios.value.length} 个场景`)
      }
      nextTick(() => {
        initChart()
      })
    } else {
      ElMessage.error(data.message || data.error || 'AI生成场景失败')
    }
  } catch (error) {
    console.error('AI生成场景失败:', error)
    ElMessage.error({
      message: 'AI生成场景失败：' + (error.message || '请检查后端服务是否正常'),
      duration: 5000,
      showClose: true
    })
  } finally {
    generating.value = false
  }
}

const handleImport = async (scenario, index) => {
  const key = getScenarioKey(scenario, index)
  if (importedKeys.value.includes(key)) return
  importingId.value = key
  try {
    const payload = {
      name: scenario.name,
      project_id: form.value.project_id,
      target_url: scenario.target_url,
      method: scenario.method || 'GET',
      concurrency: scenario.concurrency,
      ramp_up: scenario.ramp_up,
      duration: scenario.duration,
      think_time: scenario.think_time,
      intensity: scenario.intensity || form.value.intensity,
      target_type: scenario.type || form.value.target_type,
      priority: scenario.priority
    }
    const response = await fetch('/api/v1/perf/tests', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })
    if (!response.ok) {
      let errorDetail = `HTTP ${response.status}`
      try {
        const errorData = await response.json()
        errorDetail = errorData.detail || errorData.message || errorData.error || errorDetail
      } catch (_) {}
      throw new Error(errorDetail)
    }
    const data = await response.json()
    if (data.success) {
      importedKeys.value.push(key)
      ElMessage.success(`场景「${scenario.name || '未命名'}」已成功导入为性能测试`)
    } else {
      ElMessage.error(data.message || data.error || '导入测试失败')
    }
  } catch (error) {
    console.error('导入测试失败:', error)
    ElMessage.error('导入测试失败：' + (error.message || '请检查后端服务是否正常'))
  } finally {
    importingId.value = null
  }
}

const initChart = () => {
  if (!chartRef.value) return
  if (chart) {
    chart.dispose()
  }
  chart = echarts.init(chartRef.value)

  // 按优先级统计
  const priorityCounts = { high: 0, medium: 0, low: 0 }
  scenarios.value.forEach(s => {
    const p = (s.priority || '').toLowerCase()
    if (p === 'high' || p === 'critical' || p === '高') priorityCounts.high++
    else if (p === 'medium' || p === '中') priorityCounts.medium++
    else priorityCounts.low++
  })

  // 按强度统计
  const intensityCounts = {}
  scenarios.value.forEach(s => {
    const key = s.intensity || form.value.intensity || '未知'
    intensityCounts[key] = (intensityCounts[key] || 0) + 1
  })

  const priorityData = [
    { name: '高优先级', value: priorityCounts.high, itemStyle: { color: '#f5222d' } },
    { name: '中优先级', value: priorityCounts.medium, itemStyle: { color: '#faad14' } },
    { name: '低优先级', value: priorityCounts.low, itemStyle: { color: '#1890ff' } }
  ].filter(item => item.value > 0)

  chart.setOption({
    backgroundColor: 'transparent',
    tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
    legend: {
      orient: 'vertical',
      right: '4%',
      top: 'center',
      textStyle: { color: '#a0aec0', fontSize: 11 }
    },
    series: [{
      name: '场景优先级分布',
      type: 'pie',
      radius: ['42%', '70%'],
      center: ['36%', '50%'],
      avoidLabelOverlap: false,
      itemStyle: { borderRadius: 6, borderColor: '#1e2a3a', borderWidth: 2 },
      label: {
        show: true,
        color: '#e2e8f0',
        fontSize: 11,
        formatter: '{b}\n{c}'
      },
      labelLine: { lineStyle: { color: '#4a5568' } },
      data: priorityData.length > 0 ? priorityData : [{ value: 0, name: '暂无数据', itemStyle: { color: '#4a5568' } }]
    }]
  })
}

const handleResize = () => {
  chart?.resize()
}

onMounted(async () => {
  await loadProjects()
  window.addEventListener('resize', handleResize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  chart?.dispose()
  chart = null
})
</script>

<style scoped>
.ai-scenario {
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
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background:
    radial-gradient(circle at 20% 50%, rgba(24, 144, 255, 0.15) 0%, transparent 50%),
    radial-gradient(circle at 80% 50%, rgba(82, 196, 26, 0.1) 0%, transparent 50%);
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

.header-stats {
  display: flex;
  gap: 16px;
}

.header-stat {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 8px 20px;
  background: rgba(64, 169, 255, 0.08);
  border: 1px solid rgba(64, 169, 255, 0.2);
  border-radius: 8px;
  min-width: 90px;
}

.stat-num {
  font-size: 24px;
  font-weight: 700;
  color: #40a9ff;
}

.stat-num.high {
  color: #f5222d;
}

.stat-label {
  font-size: 12px;
  color: #8bb8e8;
  margin-top: 2px;
}

/* 主容器 */
.main-container {
  padding: 24px;
  max-width: 1600px;
  margin: 0 auto;
}

/* 配置面板 */
.config-panel {
  margin-bottom: 24px;
}

.config-card {
  background: rgba(30, 42, 58, 0.7);
  border: 1px solid rgba(64, 169, 255, 0.15);
  border-radius: 12px;
  backdrop-filter: blur(10px);
}

.config-card :deep(.el-card__body) {
  padding: 20px 24px;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid rgba(64, 169, 255, 0.1);
}

.header-icon {
  font-size: 18px;
  color: #40a9ff;
}

.card-title {
  font-size: 15px;
  font-weight: 600;
  color: #e2e8f0;
}

.config-row {
  display: flex;
  align-items: flex-end;
  gap: 16px;
  flex-wrap: wrap;
}

.config-item {
  flex: 1;
  min-width: 220px;
}

.control-label {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: #a0aec0;
  margin-bottom: 8px;
}

.config-select {
  width: 100%;
}

.intensity-desc {
  float: right;
  color: #8bb8e8;
  font-size: 12px;
}

.generate-btn {
  height: 32px;
  padding: 0 24px;
  background: linear-gradient(135deg, #1890ff, #40a9ff);
  border: none;
  font-weight: 500;
}

.generate-btn:hover:not(:disabled) {
  background: linear-gradient(135deg, #40a9ff, #69b1ff);
}

.generate-btn:disabled {
  opacity: 0.5;
}

.config-hint {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 12px;
  font-size: 12px;
  color: #ffa940;
  padding: 8px 12px;
  background: rgba(250, 140, 22, 0.08);
  border-radius: 6px;
  border: 1px solid rgba(250, 140, 22, 0.2);
}

/* 空状态 */
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
  font-size: 22px;
  font-weight: 600;
  color: #e2e8f0;
  margin: 0 0 8px 0;
}

.empty-desc {
  font-size: 14px;
  color: #a0aec0;
  margin: 0 0 4px 0;
}

.empty-subdesc {
  font-size: 13px;
  color: #718096;
  margin: 0;
}

/* 加载状态 */
.loading-state {
  display: flex;
  justify-content: center;
  padding: 60px 20px;
}

.loading-card {
  background: rgba(30, 42, 58, 0.7);
  border: 1px solid rgba(64, 169, 255, 0.2);
  border-radius: 12px;
  padding: 48px 64px;
  text-align: center;
  min-width: 480px;
  backdrop-filter: blur(10px);
}

.loading-spinner {
  margin-bottom: 20px;
}

.loading-spinner .is-loading {
  color: #40a9ff;
  animation: spin 1.5s linear infinite;
  filter: drop-shadow(0 0 12px rgba(64, 169, 255, 0.5));
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.loading-title {
  font-size: 18px;
  font-weight: 600;
  color: #e2e8f0;
  margin: 0 0 8px 0;
}

.loading-desc {
  font-size: 13px;
  color: #a0aec0;
  margin: 0 0 20px 0;
}

.loading-progress {
  width: 100%;
}

/* 结果区域 */
.result-section {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

/* 概览区 */
.overview-section {
  display: grid;
  grid-template-columns: 1fr 1.2fr 1fr;
  gap: 20px;
}

.info-card {
  background: rgba(30, 42, 58, 0.7);
  border: 1px solid rgba(64, 169, 255, 0.15);
  border-radius: 12px;
  backdrop-filter: blur(10px);
}

.info-card :deep(.el-card__body) {
  padding: 20px;
}

/* 统计卡片 */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}

.stat-box {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 16px 8px;
  background: rgba(15, 23, 42, 0.5);
  border-radius: 8px;
  border: 1px solid rgba(64, 169, 255, 0.1);
}

.stat-box.high {
  border-color: rgba(245, 34, 45, 0.3);
  background: rgba(245, 34, 45, 0.06);
}

.stat-box-num {
  font-size: 26px;
  font-weight: 700;
  color: #40a9ff;
  line-height: 1.2;
}

.stat-box.high .stat-box-num {
  color: #f5222d;
}

.stat-box-label {
  font-size: 12px;
  color: #8bb8e8;
  margin-top: 6px;
}

/* 图表卡片 */
.chart-container {
  width: 100%;
  height: 220px;
}

/* 模型信息卡片 */
.model-info {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 13px;
  padding: 8px 0;
  border-bottom: 1px dashed rgba(64, 169, 255, 0.1);
}

.info-row:last-child {
  border-bottom: none;
}

.info-label {
  color: #8bb8e8;
}

.info-value {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #e2e8f0;
  font-weight: 500;
  max-width: 60%;
  overflow: hidden;
}

.model-name {
  color: #40a9ff;
}

/* 区块标题 */
.section-title-bar {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid rgba(64, 169, 255, 0.15);
}

.section-title {
  font-size: 17px;
  font-weight: 600;
  color: #e2e8f0;
  margin: 0;
  flex: 1;
}

.section-title-bar .el-icon {
  font-size: 20px;
  color: #40a9ff;
}

/* 场景卡片网格 */
.scenarios-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 16px;
}

.scenario-card {
  background: rgba(30, 42, 58, 0.7);
  border: 1px solid rgba(64, 169, 255, 0.15);
  border-radius: 12px;
  padding: 18px;
  position: relative;
  overflow: hidden;
  transition: all 0.3s;
  backdrop-filter: blur(10px);
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.scenario-card:hover {
  transform: translateY(-2px);
  border-color: rgba(64, 169, 255, 0.4);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
}

.scenario-top-bar {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
}

.priority-high .scenario-top-bar { background: linear-gradient(90deg, #f5222d, #ff4d4f); }
.priority-medium .scenario-top-bar { background: linear-gradient(90deg, #faad14, #ffc53d); }
.priority-low .scenario-top-bar { background: linear-gradient(90deg, #1890ff, #36cfc9); }

.priority-high { border-color: rgba(245, 34, 45, 0.3); }
.priority-medium { border-color: rgba(250, 173, 20, 0.3); }
.priority-low { border-color: rgba(24, 144, 255, 0.3); }

/* 卡片头部 */
.scenario-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
}

.scenario-name-block {
  display: flex;
  align-items: center;
  gap: 10px;
  flex: 1;
  min-width: 0;
}

.scenario-icon {
  font-size: 18px;
  color: #40a9ff;
  flex-shrink: 0;
}

.priority-high .scenario-icon { color: #f5222d; }
.priority-medium .scenario-icon { color: #faad14; }
.priority-low .scenario-icon { color: #1890ff; }

.name-text {
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
}

.scenario-name {
  font-size: 15px;
  font-weight: 600;
  color: #e2e8f0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.scenario-type {
  font-size: 12px;
  color: #8bb8e8;
}

.scenario-tags {
  display: flex;
  gap: 6px;
  flex-shrink: 0;
}

/* 参数指标 */
.scenario-metrics {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 8px;
  padding: 12px;
  background: rgba(15, 23, 42, 0.6);
  border-radius: 8px;
}

.metric-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.metric-label {
  font-size: 11px;
  color: #718096;
}

.metric-value {
  font-size: 16px;
  font-weight: 700;
  color: #40a9ff;
}

/* 目标接口 */
.scenario-target {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.target-label {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #8bb8e8;
}

.target-content {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 10px;
  background: rgba(15, 23, 42, 0.6);
  border-radius: 6px;
  overflow: hidden;
}

.method-tag {
  flex-shrink: 0;
}

.target-url {
  font-size: 12px;
  color: #e2e8f0;
  font-family: 'Consolas', 'Monaco', monospace;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  flex: 1;
  min-width: 0;
}

/* AI推理 */
.scenario-reasoning {
  padding: 12px;
  background: rgba(82, 196, 26, 0.06);
  border-radius: 8px;
  border: 1px solid rgba(82, 196, 26, 0.15);
}

.reasoning-header {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 6px;
}

.reasoning-icon {
  color: #52c41a;
  font-size: 14px;
}

.reasoning-label {
  font-size: 12px;
  color: #52c41a;
  font-weight: 600;
}

.reasoning-text {
  font-size: 12px;
  color: #e2e8f0;
  line-height: 1.6;
  margin: 0;
}

/* 置信度 */
.scenario-confidence {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.confidence-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.confidence-label {
  font-size: 12px;
  color: #8bb8e8;
}

.confidence-value {
  font-size: 16px;
  font-weight: 700;
}

.confidence-bar {
  width: 100%;
}

/* 卡片底部按钮 */
.scenario-footer {
  margin-top: auto;
  padding-top: 4px;
}

.import-btn {
  width: 100%;
  height: 34px;
  background: linear-gradient(135deg, #1890ff, #40a9ff);
  border: none;
  font-weight: 500;
}

.import-btn:hover:not(:disabled) {
  background: linear-gradient(135deg, #40a9ff, #69b1ff);
}

.import-btn.is-disabled {
  background: linear-gradient(135deg, #52c41a, #73d13d) !important;
  color: #0f172a !important;
  opacity: 0.85;
}

/* Element Plus 暗色主题覆盖 */
.config-card :deep(.el-select__wrapper),
.info-card :deep(.el-input__wrapper) {
  background-color: rgba(15, 23, 42, 0.6);
  box-shadow: 0 0 0 1px rgba(64, 169, 255, 0.2) inset;
}

.config-card :deep(.el-select__wrapper:hover),
.config-card :deep(.el-select__wrapper.is-focused) {
  box-shadow: 0 0 0 1px #40a9ff inset;
}

.config-card :deep(.el-select__placeholder),
.config-card :deep(.el-select__selected-item) {
  color: #e2e8f0;
}

.info-card :deep(.el-progress-bar__outer) {
  background-color: rgba(15, 23, 42, 0.6);
}

.scenario-card :deep(.el-progress-bar__outer) {
  background-color: rgba(15, 23, 42, 0.6);
}

/* 响应式 */
@media (max-width: 1200px) {
  .overview-section {
    grid-template-columns: 1fr;
  }

  .scenarios-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    align-items: flex-start;
  }

  .header-stats {
    width: 100%;
    justify-content: flex-start;
    flex-wrap: wrap;
  }

  .main-container {
    padding: 16px;
  }

  .config-row {
    flex-direction: column;
    align-items: stretch;
  }

  .config-item {
    min-width: auto;
  }

  .generate-btn {
    width: 100%;
  }

  .loading-card {
    min-width: auto;
    padding: 32px 24px;
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }

  .scenario-metrics {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
