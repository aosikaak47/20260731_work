<template>
  <div class="predictive-analysis">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <div class="logo-section">
          <el-icon :size="32" class="logo-icon"><component :is="icons.TrendCharts" /></el-icon>
          <div>
            <h1>预测性分析</h1>
            <p class="subtitle">基于AI模型进行性能趋势预测和容量规划</p>
          </div>
        </div>
      </div>
    </div>

    <div class="content-wrapper">
      <!-- 配置面板 -->
      <el-card class="control-card" shadow="never">
        <div class="control-bar">
          <div class="control-left">
            <div class="control-item">
              <span class="control-label">
                <el-icon><component :is="icons.Document" /></el-icon>
                选择性能测试：
              </span>
              <el-select
                v-model="selectedTestId"
                placeholder="请选择性能测试"
                class="test-select"
                :loading="testsLoading"
                filterable
                clearable
              >
                <el-option
                  v-for="test in tests"
                  :key="test.id"
                  :label="buildTestLabel(test)"
                  :value="test.id"
                />
              </el-select>
            </div>
            <div class="control-item">
              <span class="control-label">
                <el-icon><component :is="icons.Calendar" /></el-icon>
                预测天数：
              </span>
              <el-select v-model="predictDays" class="days-select">
                <el-option :value="7" label="7 天" />
                <el-option :value="14" label="14 天" />
                <el-option :value="30" label="30 天" />
              </el-select>
            </div>
          </div>
          <div class="control-right">
            <el-button
              type="primary"
              :icon="icons.VideoPlay"
              :loading="predicting"
              :disabled="!selectedTestId || predicting"
              @click="handlePredict"
            >
              {{ predicting ? '正在预测...' : '开始预测' }}
            </el-button>
            <el-button
              :icon="icons.Refresh"
              :disabled="predicting"
              @click="loadTests"
            >
              刷新测试
            </el-button>
          </div>
        </div>
        <div v-if="tests.length === 0 && !testsLoading" class="test-hint">
          <el-icon><component :is="icons.InfoFilled" /></el-icon>
          <span>暂无可用的性能测试，请先在性能测试中创建并执行测试</span>
        </div>
      </el-card>

      <!-- 空状态 -->
      <el-card v-if="!hasResult && !predicting" class="empty-card" shadow="never">
        <div class="empty-state">
          <el-icon :size="64" class="empty-icon"><component :is="icons.DataAnalysis" /></el-icon>
          <p class="empty-title">暂无预测结果</p>
          <p class="empty-desc">请选择一个性能测试，设置预测天数，然后点击「开始预测」</p>
          <p class="empty-subdesc">AI模型将基于历史数据预测未来性能趋势并给出容量规划建议</p>
        </div>
      </el-card>

      <!-- 预测中状态 -->
      <el-card v-if="predicting" class="loading-card" shadow="never">
        <div class="loading-state">
          <el-icon :size="48" class="loading-icon"><component :is="icons.Loading" /></el-icon>
          <p class="loading-text">AI 正在进行趋势建模与容量预测...</p>
          <el-progress
            :percentage="100"
            :indeterminate="true"
            :show-text="false"
            class="loading-progress"
          />
        </div>
      </el-card>

      <!-- 预测结果 -->
      <template v-if="hasResult">
        <!-- 概览汇总卡片 -->
        <div class="summary-cards">
          <el-card class="summary-card model" shadow="never">
            <div class="summary-icon"><el-icon :size="24"><component :is="icons.Cpu" /></el-icon></div>
            <div class="summary-info">
              <div class="summary-value text-value">{{ meta.modelUsed || '-' }}</div>
              <div class="summary-label">预测模型</div>
            </div>
          </el-card>
          <el-card class="summary-card days" shadow="never">
            <div class="summary-icon"><el-icon :size="24"><component :is="icons.Calendar" /></el-icon></div>
            <div class="summary-info">
              <div class="summary-value">{{ meta.days }}</div>
              <div class="summary-label">预测天数</div>
            </div>
          </el-card>
          <el-card class="summary-card points" shadow="never">
            <div class="summary-icon"><el-icon :size="24"><component :is="icons.DataLine" /></el-icon></div>
            <div class="summary-info">
              <div class="summary-value">{{ predictions.length }}</div>
              <div class="summary-label">预测点数</div>
            </div>
          </el-card>
          <el-card class="summary-card high-risk" shadow="never">
            <div class="summary-icon"><el-icon :size="24"><component :is="icons.WarningFilled" /></el-icon></div>
            <div class="summary-info">
              <div class="summary-value">{{ riskCounts.high }}</div>
              <div class="summary-label">高风险天数</div>
            </div>
          </el-card>
          <el-card class="summary-card avg-conf" shadow="never">
            <div class="summary-icon"><el-icon :size="24"><component :is="icons.CircleCheckFilled" /></el-icon></div>
            <div class="summary-info">
              <div class="summary-value">{{ avgConfidence }}%</div>
              <div class="summary-label">平均置信度</div>
            </div>
          </el-card>
        </div>

        <!-- 预测趋势图表 -->
        <el-card class="chart-card large-chart" shadow="never">
          <template #header>
            <div class="card-header">
              <span class="card-title">
                <el-icon><component :is="icons.TrendCharts" /></el-icon>
                TPS 预测趋势
              </span>
              <span class="header-hint">阴影区域为置信区间</span>
            </div>
          </template>
          <div ref="tpsChartRef" class="chart-container large"></div>
        </el-card>

        <div class="charts-row">
          <el-card class="chart-card" shadow="never">
            <template #header>
              <span class="card-title">
                <el-icon><component :is="icons.Timer" /></el-icon>
                响应时间预测
              </span>
            </template>
            <div ref="rtChartRef" class="chart-container"></div>
          </el-card>
          <el-card class="chart-card" shadow="never">
            <template #header>
              <span class="card-title">
                <el-icon><component :is="icons.CircleClose" /></el-icon>
                错误率预测
              </span>
            </template>
            <div ref="errorChartRef" class="chart-container"></div>
          </el-card>
        </div>

        <el-card class="chart-card" shadow="never">
          <template #header>
            <div class="card-header">
              <span class="card-title">
                <el-icon><component :is="icons.DataLine" /></el-icon>
                CPU / 内存预测
              </span>
              <div class="header-legend">
                <span class="legend-item">
                  <span class="legend-dot" style="background-color: #f59e0b"></span>CPU
                </span>
                <span class="legend-item">
                  <span class="legend-dot" style="background-color: #8b5cf6"></span>内存
                </span>
              </div>
            </div>
          </template>
          <div ref="resourceChartRef" class="chart-container"></div>
        </el-card>

        <!-- 容量规划卡片 + 风险分布 -->
        <div class="bottom-row">
          <el-card class="capacity-card" shadow="never">
            <template #header>
              <div class="card-header">
                <span class="card-title warning">
                  <el-icon><component :is="icons.WarnTriangleFilled" /></el-icon>
                  容量规划建议
                </span>
                <el-tag type="warning" effect="dark" size="small">预警</el-tag>
              </div>
            </template>
            <div class="capacity-content">
              <div class="capacity-banner">
                <el-icon :size="20"><component :is="icons.WarningFilled" /></el-icon>
                <span>基于预测结果的容量规划建议，请及时评估扩容需求</span>
              </div>
              <div class="capacity-grid">
                <div class="capacity-item">
                  <div class="capacity-label">当前容量</div>
                  <div class="capacity-value">{{ capacityPlan.current_capacity || '-' }}</div>
                </div>
                <div class="capacity-item">
                  <div class="capacity-label">预计增长</div>
                  <div class="capacity-value growth">{{ capacityPlan.projected_growth || '-' }}</div>
                </div>
                <div class="capacity-item highlight">
                  <div class="capacity-label">扩容建议</div>
                  <div class="capacity-value scaling">{{ capacityPlan.recommended_scaling || '-' }}</div>
                </div>
                <div class="capacity-item danger">
                  <div class="capacity-label">预估拐点</div>
                  <div class="capacity-value">{{ capacityPlan.estimated_breakpoint || '-' }}</div>
                </div>
                <div class="capacity-item danger">
                  <div class="capacity-label">距拐点时间</div>
                  <div class="capacity-value">{{ capacityPlan.time_to_breakpoint || '-' }}</div>
                </div>
              </div>
            </div>
          </el-card>

          <el-card class="chart-card risk-pie-card" shadow="never">
            <template #header>
              <span class="card-title">
                <el-icon><component :is="icons.PieChart" /></el-icon>
                风险等级分布
              </span>
            </template>
            <div ref="riskPieRef" class="chart-container"></div>
          </el-card>
        </div>

        <!-- 预测明细表 -->
        <el-card class="table-card" shadow="never">
          <template #header>
            <div class="card-header">
              <span class="card-title">
                <el-icon><component :is="icons.List" /></el-icon>
                预测明细
              </span>
              <el-tag effect="plain" size="small">共 {{ predictions.length }} 条</el-tag>
            </div>
          </template>

          <el-table :data="predictions" stripe border style="width: 100%">
            <el-table-column type="index" label="#" width="55" align="center" />
            <el-table-column prop="date" label="日期" width="130">
              <template #default="scope">
                {{ formatDate(scope.row.date) }}
              </template>
            </el-table-column>
            <el-table-column prop="predicted_tps" label="预测TPS" width="120" align="right">
              <template #default="scope">
                <span class="value-cell tps">{{ formatNumber(scope.row.predicted_tps) }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="predicted_rt" label="预测响应时间(ms)" width="150" align="right">
              <template #default="scope">
                <span class="value-cell rt">{{ formatNumber(scope.row.predicted_rt) }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="predicted_error_rate" label="错误率(%)" width="120" align="right">
              <template #default="scope">
                <span class="value-cell error">{{ formatNumber(scope.row.predicted_error_rate) }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="predicted_cpu" label="CPU(%)" width="110" align="right">
              <template #default="scope">
                <span class="value-cell cpu">{{ formatNumber(scope.row.predicted_cpu) }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="predicted_memory" label="内存(%)" width="110" align="right">
              <template #default="scope">
                <span class="value-cell memory">{{ formatNumber(scope.row.predicted_memory) }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="confidence" label="置信度" width="120" align="center">
              <template #default="scope">
                <el-progress
                  :percentage="confidencePercent(scope.row.confidence)"
                  :color="confidenceColor(scope.row.confidence)"
                  :stroke-width="10"
                  :text-inside="false"
                  :format="() => confidencePercent(scope.row.confidence) + '%'"
                  class="conf-progress"
                />
              </template>
            </el-table-column>
            <el-table-column prop="risk_level" label="风险等级" width="110" align="center">
              <template #default="scope">
                <el-tag :type="riskTagType(scope.row.risk_level)" effect="dark" size="small">
                  {{ riskLabel(scope.row.risk_level) }}
                </el-tag>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </template>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import * as icons from '@element-plus/icons-vue'
import * as echarts from 'echarts'

// ===== 静态配置 =====
const riskColors = {
  low: '#10b981',
  medium: '#f59e0b',
  high: '#ef4444'
}

const riskLabels = {
  low: '低风险',
  medium: '中风险',
  high: '高风险'
}

// ===== 状态 =====
const tests = ref([])
const selectedTestId = ref('')
const testsLoading = ref(false)
const predictDays = ref(7)
const predicting = ref(false)

const predictions = ref([])
const capacityPlan = ref({})
const meta = reactive({
  modelUsed: '',
  analyzedAt: '',
  days: 7
})

// ===== 图表引用 =====
const tpsChartRef = ref(null)
const rtChartRef = ref(null)
const errorChartRef = ref(null)
const resourceChartRef = ref(null)
const riskPieRef = ref(null)

let tpsChartInstance = null
let rtChartInstance = null
let errorChartInstance = null
let resourceChartInstance = null
let riskPieInstance = null

// ===== 计算属性 =====
const hasResult = computed(() => predictions.value.length > 0)

const riskCounts = computed(() => {
  const counts = { low: 0, medium: 0, high: 0 }
  predictions.value.forEach(p => {
    const level = (p.risk_level || 'medium').toLowerCase()
    if (counts[level] !== undefined) counts[level]++
  })
  return counts
})

const avgConfidence = computed(() => {
  if (predictions.value.length === 0) return 0
  const sum = predictions.value.reduce((acc, p) => acc + confidencePercent(p.confidence), 0)
  return Math.round(sum / predictions.value.length)
})

// ===== 工具方法 =====
const buildTestLabel = (test) => {
  const name = test.name || test.title || test.scenario_name || `测试 #${test.id}`
  const time = test.start_time || test.created_at || ''
  return time ? `${name} (${time})` : name
}

const formatDate = (date) => {
  if (!date) return '-'
  const str = String(date)
  if (/^\d{4}-\d{2}-\d{2}/.test(str)) return str.slice(0, 10)
  const d = new Date(str)
  if (!isNaN(d.getTime())) return d.toLocaleDateString('zh-CN')
  return str
}

const formatNumber = (val) => {
  if (val === null || val === undefined || val === '') return '-'
  const num = Number(val)
  if (isNaN(num)) return String(val)
  return Number.isInteger(num) ? String(num) : num.toFixed(2)
}

const confidencePercent = (val) => {
  if (val === null || val === undefined || val === '') return 0
  const num = typeof val === 'string' ? parseFloat(val) : Number(val)
  if (isNaN(num)) return 0
  return num > 1 ? Math.round(num) : Math.round(num * 100)
}

const confidenceColor = (val) => {
  const p = confidencePercent(val)
  if (p >= 85) return '#10b981'
  if (p >= 70) return '#1890ff'
  if (p >= 60) return '#f59e0b'
  return '#ef4444'
}

const riskTagType = (level) => {
  const l = (level || '').toLowerCase()
  if (l === 'high') return 'danger'
  if (l === 'medium') return 'warning'
  return 'success'
}

const riskLabel = (level) => {
  const l = (level || '').toLowerCase()
  return riskLabels[l] || '中风险'
}

// ===== API 调用 =====
const loadTests = async () => {
  testsLoading.value = true
  try {
    const response = await fetch('/api/v1/perf/tests')
    const data = await response.json()
    if (data.success !== false) {
      tests.value = data.tests || []
    } else {
      tests.value = []
      ElMessage.error(data.message || '加载测试列表失败')
    }
  } catch (error) {
    console.error('加载测试列表失败:', error)
    tests.value = []
    ElMessage.error('加载测试列表失败，请检查后端服务')
  } finally {
    testsLoading.value = false
  }
}

const handlePredict = async () => {
  if (!selectedTestId.value) {
    ElMessage.warning('请先选择一个性能测试')
    return
  }
  predicting.value = true
  // 重置结果
  predictions.value = []
  capacityPlan.value = {}
  meta.modelUsed = ''
  meta.analyzedAt = ''
  meta.days = predictDays.value

  try {
    const response = await fetch('/api/v1/perf/ai/predict', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        test_id: selectedTestId.value,
        days: predictDays.value
      })
    })

    if (!response.ok) {
      let errorDetail = `HTTP ${response.status}`
      try {
        const errorData = await response.json()
        errorDetail = errorData.detail || errorData.message || errorData.error || errorDetail
      } catch (_) {
        // ignore
      }
      throw new Error(errorDetail)
    }

    const data = await response.json()
    if (data.success) {
      predictions.value = normalizePredictions(data.predictions || [])
      capacityPlan.value = data.capacity_plan || {}
      meta.modelUsed = data.model_used || data.modelUsed || 'AI-Engine'
      meta.analyzedAt = data.analyzed_at || data.analyzedAt || ''
      meta.days = predictDays.value

      ElMessage.success(`预测完成，共生成 ${predictions.value.length} 个预测点`)
      await nextTick()
      initAllCharts()
      updateAllCharts()
    } else {
      ElMessage.error(data.message || data.error || '预测失败')
    }
  } catch (error) {
    console.error('预测失败:', error)
    ElMessage.error({
      message: '预测失败：' + (error.message || '请检查后端服务'),
      duration: 5000,
      showClose: true
    })
  } finally {
    predicting.value = false
  }
}

const normalizePredictions = (list) => {
  return list.map(item => ({
    ...item,
    risk_level: (item.risk_level || 'medium').toLowerCase()
  }))
}

// ===== 图表初始化与更新 =====
function initAllCharts() {
  if (tpsChartRef.value && !tpsChartInstance) {
    tpsChartInstance = echarts.init(tpsChartRef.value)
  }
  if (rtChartRef.value && !rtChartInstance) {
    rtChartInstance = echarts.init(rtChartRef.value)
  }
  if (errorChartRef.value && !errorChartInstance) {
    errorChartInstance = echarts.init(errorChartRef.value)
  }
  if (resourceChartRef.value && !resourceChartInstance) {
    resourceChartInstance = echarts.init(resourceChartRef.value)
  }
  if (riskPieRef.value && !riskPieInstance) {
    riskPieInstance = echarts.init(riskPieRef.value)
  }
}

function updateAllCharts() {
  updateTpsChart()
  updateRtChart()
  updateErrorChart()
  updateResourceChart()
  updateRiskPie()
}

// 计算置信区间上下界（基于置信度生成合理的置信带）
function buildConfidenceBand(values, confidences) {
  return values.map((v, i) => {
    const val = Number(v)
    if (isNaN(val)) return [null, null]
    const conf = confidencePercent(confidences[i]) / 100
    // 置信度越高，区间越窄
    const spread = 1 - conf
    const offset = val * spread * 0.15
    return [Number((val - offset).toFixed(2)), Number((val + offset).toFixed(2))]
  })
}

function updateTpsChart() {
  if (!tpsChartInstance) return
  const dates = predictions.value.map(p => formatDate(p.date))
  const tpsValues = predictions.value.map(p => Number(p.predicted_tps) || 0)
  const band = buildConfidenceBand(
    predictions.value.map(p => p.predicted_tps),
    predictions.value.map(p => p.confidence)
  )
  const lower = band.map(b => b[0])
  const upper = band.map(b => b[1])

  tpsChartInstance.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'cross' } },
    legend: { top: 0, textStyle: { color: '#6b7280' } },
    grid: { left: '3%', right: '4%', bottom: '8%', top: '15%', containLabel: true },
    xAxis: {
      type: 'category',
      data: dates,
      boundaryGap: false,
      axisLine: { lineStyle: { color: '#d1d5db' } },
      axisLabel: { color: '#6b7280', rotate: dates.length > 8 ? 30 : 0 }
    },
    yAxis: {
      type: 'value',
      name: 'TPS',
      axisLine: { lineStyle: { color: '#d1d5db' } },
      axisLabel: { color: '#6b7280' },
      splitLine: { lineStyle: { color: '#f3f4f6' } }
    },
    series: [
      {
        name: '置信下界',
        type: 'line',
        smooth: true,
        symbol: 'none',
        lineStyle: { opacity: 0 },
        stack: 'confidence',
        data: lower
      },
      {
        name: '置信区间',
        type: 'line',
        smooth: true,
        symbol: 'none',
        stack: 'confidence',
        areaStyle: { color: 'rgba(99, 102, 241, 0.18)' },
        lineStyle: { opacity: 0 },
        data: upper.map((u, i) => Number((u - (lower[i] || 0)).toFixed(2)))
      },
      {
        name: '预测TPS',
        type: 'line',
        smooth: true,
        symbol: 'circle',
        symbolSize: 6,
        lineStyle: { color: '#6366f1', width: 2.5 },
        itemStyle: { color: '#6366f1' },
        data: tpsValues
      }
    ]
  }, true)
}

function updateRtChart() {
  if (!rtChartInstance) return
  const dates = predictions.value.map(p => formatDate(p.date))
  const rtValues = predictions.value.map(p => Number(p.predicted_rt) || 0)

  rtChartInstance.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'cross' } },
    grid: { left: '3%', right: '4%', bottom: '8%', top: '12%', containLabel: true },
    xAxis: {
      type: 'category',
      data: dates,
      boundaryGap: false,
      axisLine: { lineStyle: { color: '#d1d5db' } },
      axisLabel: { color: '#6b7280', rotate: dates.length > 8 ? 30 : 0 }
    },
    yAxis: {
      type: 'value',
      name: '响应时间(ms)',
      axisLine: { lineStyle: { color: '#d1d5db' } },
      axisLabel: { color: '#6b7280' },
      splitLine: { lineStyle: { color: '#f3f4f6' } }
    },
    series: [{
      name: '预测响应时间',
      type: 'line',
      smooth: true,
      symbol: 'circle',
      symbolSize: 6,
      lineStyle: { color: '#06b6d4', width: 2.5 },
      itemStyle: { color: '#06b6d4' },
      areaStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: 'rgba(6, 182, 212, 0.25)' },
          { offset: 1, color: 'rgba(6, 182, 212, 0.02)' }
        ])
      },
      data: rtValues
    }]
  }, true)
}

function updateErrorChart() {
  if (!errorChartInstance) return
  const dates = predictions.value.map(p => formatDate(p.date))
  const errorValues = predictions.value.map(p => Number(p.predicted_error_rate) || 0)

  errorChartInstance.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'cross' } },
    grid: { left: '3%', right: '4%', bottom: '8%', top: '12%', containLabel: true },
    xAxis: {
      type: 'category',
      data: dates,
      boundaryGap: true,
      axisLine: { lineStyle: { color: '#d1d5db' } },
      axisLabel: { color: '#6b7280', rotate: dates.length > 8 ? 30 : 0 }
    },
    yAxis: {
      type: 'value',
      name: '错误率(%)',
      axisLine: { lineStyle: { color: '#d1d5db' } },
      axisLabel: { color: '#6b7280' },
      splitLine: { lineStyle: { color: '#f3f4f6' } }
    },
    series: [{
      name: '预测错误率',
      type: 'bar',
      barWidth: '50%',
      itemStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: '#ef4444' },
          { offset: 1, color: '#f87171' }
        ]),
        borderRadius: [4, 4, 0, 0]
      },
      data: errorValues
    }]
  }, true)
}

function updateResourceChart() {
  if (!resourceChartInstance) return
  const dates = predictions.value.map(p => formatDate(p.date))
  const cpuValues = predictions.value.map(p => Number(p.predicted_cpu) || 0)
  const memValues = predictions.value.map(p => Number(p.predicted_memory) || 0)

  resourceChartInstance.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'cross' } },
    legend: { top: 0, textStyle: { color: '#6b7280' } },
    grid: { left: '3%', right: '4%', bottom: '8%', top: '12%', containLabel: true },
    xAxis: {
      type: 'category',
      data: dates,
      boundaryGap: false,
      axisLine: { lineStyle: { color: '#d1d5db' } },
      axisLabel: { color: '#6b7280', rotate: dates.length > 8 ? 30 : 0 }
    },
    yAxis: {
      type: 'value',
      name: '使用率(%)',
      max: 100,
      axisLine: { lineStyle: { color: '#d1d5db' } },
      axisLabel: { color: '#6b7280' },
      splitLine: { lineStyle: { color: '#f3f4f6' } }
    },
    series: [
      {
        name: 'CPU',
        type: 'line',
        smooth: true,
        symbol: 'circle',
        symbolSize: 6,
        lineStyle: { color: '#f59e0b', width: 2.5 },
        itemStyle: { color: '#f59e0b' },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(245, 158, 11, 0.3)' },
            { offset: 1, color: 'rgba(245, 158, 11, 0.02)' }
          ])
        },
        data: cpuValues
      },
      {
        name: '内存',
        type: 'line',
        smooth: true,
        symbol: 'circle',
        symbolSize: 6,
        lineStyle: { color: '#8b5cf6', width: 2.5 },
        itemStyle: { color: '#8b5cf6' },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(139, 92, 246, 0.3)' },
            { offset: 1, color: 'rgba(139, 92, 246, 0.02)' }
          ])
        },
        data: memValues
      }
    ]
  }, true)
}

function updateRiskPie() {
  if (!riskPieInstance) return
  const counts = riskCounts.value
  const data = [
    { name: '低风险', value: counts.low, itemStyle: { color: riskColors.low } },
    { name: '中风险', value: counts.medium, itemStyle: { color: riskColors.medium } },
    { name: '高风险', value: counts.high, itemStyle: { color: riskColors.high } }
  ].filter(item => item.value > 0)

  riskPieInstance.setOption({
    tooltip: { trigger: 'item', formatter: '{b}: {c} 天 ({d}%)' },
    legend: {
      orient: 'vertical',
      right: '5%',
      top: 'center',
      textStyle: { color: '#6b7280' }
    },
    series: [{
      name: '风险分布',
      type: 'pie',
      radius: ['40%', '70%'],
      center: ['38%', '50%'],
      avoidLabelOverlap: false,
      itemStyle: { borderRadius: 8, borderColor: '#fff', borderWidth: 2 },
      label: { show: false },
      emphasis: { label: { show: true, fontSize: 16, fontWeight: 'bold' } },
      labelLine: { show: false },
      data: data.length > 0 ? data : [{ name: '暂无数据', value: 0, itemStyle: { color: '#c0c4cc' } }]
    }]
  }, true)
}

function handleResize() {
  tpsChartInstance?.resize()
  rtChartInstance?.resize()
  errorChartInstance?.resize()
  resourceChartInstance?.resize()
  riskPieInstance?.resize()
}

onMounted(() => {
  loadTests()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  tpsChartInstance?.dispose()
  rtChartInstance?.dispose()
  errorChartInstance?.dispose()
  resourceChartInstance?.dispose()
  riskPieInstance?.dispose()
})
</script>

<style scoped>
.predictive-analysis {
  min-height: 100vh;
  background-color: #f5f7fa;
}

/* 页面头部 */
.page-header {
  background: linear-gradient(135deg, #2563eb 0%, #7c3aed 100%);
  color: white;
  padding: 24px 32px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.header-left {
  display: flex;
  align-items: center;
}

.logo-section {
  display: flex;
  align-items: center;
  gap: 16px;
}

.logo-icon {
  color: #fde047;
}

.page-header h1 {
  font-size: 24px;
  font-weight: 600;
  margin: 0;
}

.subtitle {
  font-size: 14px;
  opacity: 0.9;
  margin: 4px 0 0 0;
}

.content-wrapper {
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  max-width: 1920px;
  margin: 0 auto;
}

/* 配置面板 */
.control-card {
  border-radius: 12px;
}

.control-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 16px;
}

.control-left {
  display: flex;
  align-items: center;
  gap: 24px;
  flex-wrap: wrap;
}

.control-item {
  display: flex;
  align-items: center;
  gap: 12px;
}

.control-label {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  font-weight: 500;
  color: #303133;
  white-space: nowrap;
}

.test-select {
  width: 300px;
}

.days-select {
  width: 140px;
}

.control-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.test-hint {
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

/* 空状态 / 加载 */
.empty-card,
.loading-card {
  border-radius: 12px;
}

.empty-state,
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 0;
  color: #9ca3af;
  gap: 12px;
}

.empty-icon {
  color: #c0c4cc;
}

.empty-title {
  font-size: 18px;
  font-weight: 500;
  color: #6b7280;
  margin: 0;
}

.empty-desc {
  font-size: 14px;
  color: #9ca3af;
  margin: 0;
}

.empty-subdesc {
  font-size: 13px;
  color: #c0c4cc;
  margin: 0;
}

.loading-icon {
  color: #2563eb;
  animation: rotate 1s linear infinite;
}

@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.loading-text {
  font-size: 15px;
  color: #6b7280;
  margin: 0;
}

.loading-progress {
  width: 320px;
  margin-top: 8px;
}

/* 汇总卡片 */
.summary-cards {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 16px;
}

.summary-card {
  border-radius: 12px;
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 8px 8px 8px 20px;
  border-left: 4px solid transparent;
}

.summary-card.model { border-left-color: #8b5cf6; }
.summary-card.days { border-left-color: #2563eb; }
.summary-card.points { border-left-color: #6366f1; }
.summary-card.high-risk { border-left-color: #ef4444; }
.summary-card.avg-conf { border-left-color: #10b981; }

.summary-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.summary-card.model .summary-icon { background: rgba(139, 92, 246, 0.12); color: #8b5cf6; }
.summary-card.days .summary-icon { background: rgba(37, 99, 235, 0.12); color: #2563eb; }
.summary-card.points .summary-icon { background: rgba(99, 102, 241, 0.12); color: #6366f1; }
.summary-card.high-risk .summary-icon { background: rgba(239, 68, 68, 0.12); color: #ef4444; }
.summary-card.avg-conf .summary-icon { background: rgba(16, 185, 129, 0.12); color: #10b981; }

.summary-info {
  min-width: 0;
}

.summary-value {
  font-size: 28px;
  font-weight: 700;
  color: #1f2937;
  line-height: 1.2;
}

.summary-value.text-value {
  font-size: 16px;
  word-break: break-all;
}

.summary-label {
  font-size: 13px;
  color: #6b7280;
  margin-top: 4px;
}

/* 图表卡片 */
.chart-card {
  border-radius: 12px;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 12px;
}

.card-title {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 15px;
  font-weight: 600;
  color: #303133;
}

.card-title.warning {
  color: #d97706;
}

.header-hint {
  font-size: 12px;
  color: #9ca3af;
}

.header-legend {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #6b7280;
}

.legend-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  display: inline-block;
}

.chart-container {
  width: 100%;
  height: 320px;
}

.chart-container.large {
  height: 380px;
}

.charts-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

/* 底部行：容量规划 + 风险饼图 */
.bottom-row {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 16px;
}

/* 容量规划卡片 */
.capacity-card {
  border-radius: 12px;
  border: 1px solid rgba(250, 173, 20, 0.4);
  background: linear-gradient(135deg, rgba(255, 251, 230, 0.6) 0%, rgba(255, 245, 230, 0.4) 100%);
}

.capacity-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.capacity-banner {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  background: linear-gradient(135deg, rgba(250, 173, 20, 0.18), rgba(245, 34, 45, 0.1));
  border: 1px solid rgba(250, 173, 20, 0.35);
  border-radius: 8px;
  color: #b45309;
  font-size: 13px;
  font-weight: 600;
}

.capacity-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 12px;
}

.capacity-item {
  padding: 16px;
  background: rgba(255, 255, 255, 0.7);
  border-radius: 8px;
  border: 1px solid rgba(250, 173, 20, 0.2);
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.capacity-item.highlight {
  background: rgba(250, 173, 20, 0.12);
  border-color: rgba(250, 173, 20, 0.5);
}

.capacity-item.danger {
  background: rgba(239, 68, 68, 0.08);
  border-color: rgba(239, 68, 68, 0.3);
}

.capacity-label {
  font-size: 12px;
  color: #6b7280;
  font-weight: 500;
}

.capacity-value {
  font-size: 18px;
  font-weight: 700;
  color: #1f2937;
  word-break: break-all;
}

.capacity-value.growth {
  color: #d97706;
}

.capacity-value.scaling {
  color: #b45309;
}

.risk-pie-card {
  height: 100%;
}

/* 表格 */
.table-card {
  border-radius: 12px;
}

.value-cell {
  font-weight: 600;
  font-family: 'Courier New', monospace;
}

.value-cell.tps { color: #6366f1; }
.value-cell.rt { color: #06b6d4; }
.value-cell.error { color: #ef4444; }
.value-cell.cpu { color: #f59e0b; }
.value-cell.memory { color: #8b5cf6; }

.conf-progress {
  width: 100%;
}

/* 响应式 */
@media (max-width: 1200px) {
  .summary-cards {
    grid-template-columns: repeat(2, 1fr);
  }

  .charts-row,
  .bottom-row {
    grid-template-columns: 1fr;
  }

  .capacity-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .test-select {
    width: 240px;
  }
}

@media (max-width: 768px) {
  .control-bar {
    flex-direction: column;
    align-items: stretch;
  }

  .control-left {
    flex-direction: column;
    align-items: stretch;
  }

  .control-item {
    width: 100%;
  }

  .test-select,
  .days-select {
    width: 100%;
  }

  .summary-cards {
    grid-template-columns: 1fr;
  }

  .capacity-grid {
    grid-template-columns: 1fr;
  }
}
</style>
