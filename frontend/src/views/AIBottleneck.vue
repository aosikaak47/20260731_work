<template>
  <div class="ai-bottleneck">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-content">
        <div class="logo-section">
          <el-icon :size="36" class="logo-icon"><component :is="icons.Cpu" /></el-icon>
          <div class="title-block">
            <h1>AI瓶颈分析</h1>
            <p class="subtitle">基于AI引擎的智能性能瓶颈分析与诊断</p>
          </div>
        </div>
        <div class="header-stats">
          <div class="header-stat">
            <span class="stat-num">{{ bottlenecks.length }}</span>
            <span class="stat-label">瓶颈数</span>
          </div>
          <div class="header-stat">
            <span class="stat-num">{{ criticalCount }}</span>
            <span class="stat-label">严重</span>
          </div>
        </div>
      </div>
    </div>

    <div class="main-container">
      <!-- 控制面板 -->
      <div class="control-panel">
        <el-card class="control-card" shadow="never">
          <div class="control-row">
            <div class="control-item">
              <span class="control-label">
                <el-icon><component :is="icons.Document" /></el-icon>
                选择性能报告
              </span>
              <el-select
                v-model="selectedReportId"
                placeholder="请选择性能报告"
                class="report-select"
                :loading="reportsLoading"
                filterable
                clearable
              >
                <el-option
                  v-for="report in reports"
                  :key="report.id || report.report_id"
                  :label="report.name || report.title || `报告 #${report.id || report.report_id}`"
                  :value="String(report.id || report.report_id)"
                />
              </el-select>
            </div>
            <el-button
              type="primary"
              class="analyze-btn"
              :loading="analyzing"
              :disabled="!selectedReportId || analyzing"
              @click="handleAnalyze"
            >
              <el-icon v-if="!analyzing"><component :is="icons.MagicStick" /></el-icon>
              {{ analyzing ? 'AI分析中...' : '开始AI分析' }}
            </el-button>
          </div>
          <div v-if="reports.length === 0 && !reportsLoading" class="report-hint">
            <el-icon><component :is="icons.InfoFilled" /></el-icon>
            <span>暂无可用的性能报告，请先在性能测试中生成报告</span>
          </div>
        </el-card>
      </div>

      <!-- 空状态占位 -->
      <div v-if="!selectedReportId && !analyzing && !analysis" class="empty-state">
        <el-icon :size="80" class="empty-icon"><component :is="icons.DataAnalysis" /></el-icon>
        <h2 class="empty-title">等待AI分析</h2>
        <p class="empty-desc">请先选择一个性能报告，然后点击「开始AI分析」按钮</p>
        <p class="empty-subdesc">AI引擎将自动诊断性能瓶颈，定位根因并给出优化建议</p>
      </div>

      <!-- 加载状态 -->
      <div v-if="analyzing" class="loading-state">
        <div class="loading-card">
          <div class="loading-spinner">
            <el-icon :size="56" class="is-loading"><component :is="icons.Loading" /></el-icon>
          </div>
          <h3 class="loading-title">AI引擎正在分析性能数据</h3>
          <p class="loading-desc">正在诊断瓶颈、计算置信度、生成优化建议...</p>
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

      <!-- 分析结果 -->
      <div v-if="analysis && !analyzing" class="analysis-result">
        <!-- 分析概览卡片组 -->
        <div class="overview-section">
          <!-- 模型信息卡片 -->
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
                  {{ analysis.model_used || 'AI-Engine-v1.0' }}
                </span>
              </div>
              <div class="info-row">
                <span class="info-label">分析耗时</span>
                <span class="info-value">
                  <el-icon><component :is="icons.Timer" /></el-icon>
                  {{ analysis.analysis_time || '-' }}
                </span>
              </div>
              <div class="info-row">
                <span class="info-label">瓶颈类型</span>
                <el-tag
                  :type="bottleneckTypeTag(analysis.bottleneck_type)"
                  effect="dark"
                  size="small"
                >
                  {{ analysis.bottleneck_type || '未知' }}
                </el-tag>
              </div>
            </div>
            <div class="confidence-section">
              <div class="confidence-header">
                <span class="confidence-label">置信度</span>
                <span class="confidence-value" :style="{ color: confidenceColor }">
                  {{ confidencePercent }}%
                </span>
              </div>
              <el-progress
                :percentage="confidencePercent"
                :color="confidenceColor"
                :stroke-width="14"
                :show-text="false"
                class="confidence-bar"
              />
              <div class="confidence-desc">{{ confidenceDesc }}</div>
            </div>
          </el-card>

          <!-- 根因分析卡片 -->
          <el-card class="info-card root-cause-card" shadow="never">
            <div class="card-header">
              <el-icon class="header-icon"><component :is="icons.Aim" /></el-icon>
              <span class="card-title">根因分析</span>
            </div>
            <div class="root-cause-content">
              <p class="root-cause-text">{{ analysis.root_cause || '暂无根因分析数据' }}</p>
              <div v-if="analysis.suggestions && analysis.suggestions.length > 0" class="suggestions-list">
                <div class="suggestions-title">
                  <el-icon><component :is="icons.List" /></el-icon>
                  <span>优化建议</span>
                </div>
                <div v-for="(suggestion, index) in analysis.suggestions" :key="index" class="suggestion-item">
                  <span class="suggestion-index">{{ index + 1 }}</span>
                  <span class="suggestion-text">{{ suggestion }}</span>
                </div>
              </div>
            </div>
          </el-card>

          <!-- 趋势预测卡片 -->
          <el-card class="info-card trend-card" shadow="never">
            <div class="card-header">
              <el-icon class="header-icon warning"><component :is="icons.WarningFilled" /></el-icon>
              <span class="card-title">趋势预测</span>
              <el-tag type="warning" effect="dark" size="small" class="trend-tag">预警</el-tag>
            </div>
            <div class="trend-content">
              <div class="trend-warning-banner">
                <el-icon :size="20"><component :is="icons.WarnTriangleFilled" /></el-icon>
                <span>性能趋势预警</span>
              </div>
              <p class="trend-text">{{ analysis.trend_prediction || '暂无趋势预测数据' }}</p>
            </div>
          </el-card>
        </div>

        <!-- 瓶颈列表 -->
        <div v-if="bottlenecks.length > 0" class="bottlenecks-section">
          <div class="section-title-bar">
            <el-icon><component :is="icons.Warning" /></el-icon>
            <h2 class="section-title">瓶颈列表</h2>
            <el-tag effect="dark" size="small">共 {{ bottlenecks.length }} 项</el-tag>
          </div>
          <div class="bottlenecks-grid">
            <div
              v-for="(bottleneck, index) in bottlenecks"
              :key="index"
              class="bottleneck-card"
              :class="severityClass(bottleneck.severity)"
            >
              <div class="bottleneck-top-bar"></div>
              <div class="bottleneck-header">
                <div class="bottleneck-type">
                  <el-icon class="type-icon"><component :is="severityIcon(bottleneck.severity)" /></el-icon>
                  <span class="type-name">{{ bottleneck.type || bottleneck.name || '未知瓶颈' }}</span>
                </div>
                <el-tag
                  :type="severityTagType(bottleneck.severity)"
                  effect="dark"
                  size="small"
                  class="severity-tag"
                >
                  {{ severityLabel(bottleneck.severity) }}
                </el-tag>
              </div>
              <p class="bottleneck-desc">{{ bottleneck.description || '暂无描述' }}</p>
              <div class="bottleneck-metrics">
                <div class="metric-item">
                  <span class="metric-label">指标值</span>
                  <span class="metric-value" :class="severityClass(bottleneck.severity)">
                    {{ formatMetric(bottleneck.metric_value) }}
                  </span>
                </div>
                <div class="metric-divider">
                  <el-icon><component :is="icons.ArrowRightBold" /></el-icon>
                </div>
                <div class="metric-item">
                  <span class="metric-label">阈值</span>
                  <span class="metric-value threshold">
                    {{ formatMetric(bottleneck.threshold) }}
                  </span>
                </div>
              </div>
              <div v-if="bottleneck.suggestion || bottleneck.suggestions" class="bottleneck-suggestion">
                <el-icon class="suggestion-icon"><component :is="icons.MagicStick" /></el-icon>
                <div class="suggestion-content">
                  <span class="suggestion-label">优化建议</span>
                  <span class="suggestion-text">{{ bottleneck.suggestion || (Array.isArray(bottleneck.suggestions) ? bottleneck.suggestions.join('；') : bottleneck.suggestions) }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 可视化图表 -->
        <div v-if="bottlenecks.length > 0" class="charts-section">
          <div class="section-title-bar">
            <el-icon><component :is="icons.PieChart" /></el-icon>
            <h2 class="section-title">可视化分析</h2>
          </div>
          <div class="charts-grid">
            <el-card class="chart-card" shadow="never">
              <template #header>
                <div class="chart-card-header">
                  <el-icon><component :is="icons.PieChart" /></el-icon>
                  <span>瓶颈严重度分布</span>
                </div>
              </template>
              <div ref="pieChartRef" class="chart-container"></div>
            </el-card>

            <el-card class="chart-card" shadow="never">
              <template #header>
                <div class="chart-card-header">
                  <el-icon><component :is="icons.Histogram" /></el-icon>
                  <span>指标值与阈值对比</span>
                </div>
              </template>
              <div ref="barChartRef" class="chart-container"></div>
            </el-card>

            <el-card class="chart-card chart-card-full" shadow="never">
              <template #header>
                <div class="chart-card-header">
                  <el-icon><component :is="icons.TrendCharts" /></el-icon>
                  <span>瓶颈发生时间线</span>
                </div>
              </template>
              <div ref="timelineChartRef" class="chart-container"></div>
            </el-card>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, nextTick, watch } from 'vue'
import * as echarts from 'echarts'
import { ElMessage } from 'element-plus'
import * as icons from '@element-plus/icons-vue'

const selectedReportId = ref('')
const reports = ref([])
const reportsLoading = ref(false)
const analyzing = ref(false)
const analysis = ref(null)
const bottlenecks = ref([])

const pieChartRef = ref(null)
const barChartRef = ref(null)
const timelineChartRef = ref(null)
let pieChart = null
let barChart = null
let timelineChart = null

const severityColors = {
  critical: '#f5222d',
  high: '#fa8c16',
  medium: '#fadb14',
  low: '#1890ff'
}

const severityLabels = {
  critical: '严重',
  high: '高',
  medium: '中',
  low: '低'
}

const criticalCount = computed(() => {
  return bottlenecks.value.filter(b => (b.severity || '').toLowerCase() === 'critical').length
})

const confidencePercent = computed(() => {
  const val = analysis.value?.confidence
  if (val === undefined || val === null) return 0
  const num = typeof val === 'string' ? parseFloat(val) : Number(val)
  if (isNaN(num)) return 0
  return num > 1 ? Math.round(num) : Math.round(num * 100)
})

const confidenceColor = computed(() => {
  const p = confidencePercent.value
  if (p > 90) return '#52c41a'
  if (p > 80) return '#1890ff'
  if (p > 70) return '#fadb14'
  return '#f5222d'
})

const confidenceDesc = computed(() => {
  const p = confidencePercent.value
  if (p > 90) return '极高置信度，分析结果可信'
  if (p > 80) return '较高置信度，结果具有参考价值'
  if (p > 70) return '中等置信度，建议结合实际验证'
  return '置信度较低，建议补充数据后重新分析'
})

const loadReports = async () => {
  reportsLoading.value = true
  try {
    const response = await fetch('/api/v1/perf/reports')
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`)
    }
    const data = await response.json()
    if (data.success) {
      reports.value = data.reports || []
    } else {
      reports.value = []
      ElMessage.warning(data.message || '获取性能报告列表失败')
    }
  } catch (error) {
    console.error('获取性能报告失败:', error)
    reports.value = []
    ElMessage.error('获取性能报告列表失败，请检查后端服务是否正常')
  } finally {
    reportsLoading.value = false
  }
}

const handleAnalyze = async () => {
  if (!selectedReportId.value) {
    ElMessage.warning('请先选择一个性能报告')
    return
  }
  analyzing.value = true
  analysis.value = null
  bottlenecks.value = []
  try {
    const response = await fetch(`/api/v1/perf/ai/bottleneck/${selectedReportId.value}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' }
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
      bottlenecks.value = data.bottlenecks || []
      analysis.value = data.analysis || null
      if (bottlenecks.value.length === 0) {
        ElMessage.info('AI分析完成，未检测到明显性能瓶颈')
      } else {
        ElMessage.success(`AI分析完成，共发现 ${bottlenecks.value.length} 个性能瓶颈`)
      }
      nextTick(() => {
        initAllCharts()
      })
    } else {
      ElMessage.error(data.message || data.error || 'AI分析失败')
    }
  } catch (error) {
    console.error('AI分析失败:', error)
    ElMessage.error({
      message: 'AI分析失败：' + (error.message || '请检查后端服务是否正常'),
      duration: 5000,
      showClose: true
    })
  } finally {
    analyzing.value = false
  }
}

const severityClass = (severity) => {
  const s = (severity || '').toLowerCase()
  return `severity-${s || 'medium'}`
}

const severityLabel = (severity) => {
  const s = (severity || '').toLowerCase()
  return severityLabels[s] || '中'
}

const severityTagType = (severity) => {
  const s = (severity || '').toLowerCase()
  const types = {
    critical: 'danger',
    high: 'warning',
    medium: 'warning',
    low: 'info'
  }
  return types[s] || 'info'
}

const severityIcon = (severity) => {
  const s = (severity || '').toLowerCase()
  const iconMap = {
    critical: icons.CircleCloseFilled,
    high: icons.WarnTriangleFilled,
    medium: icons.WarningFilled,
    low: icons.InfoFilled
  }
  return iconMap[s] || icons.WarningFilled
}

const bottleneckTypeTag = (type) => {
  if (!type) return 'info'
  const t = type.toLowerCase()
  if (t.includes('cpu') || t.includes('内存') || t.includes('memory')) return 'danger'
  if (t.includes('io') || t.includes('磁盘')) return 'warning'
  if (t.includes('网络') || t.includes('network')) return 'primary'
  return 'info'
}

const formatMetric = (value) => {
  if (value === undefined || value === null || value === '') return '-'
  const num = typeof value === 'string' ? parseFloat(value) : value
  if (isNaN(num)) return String(value)
  return num
}

const initAllCharts = () => {
  initPieChart()
  initBarChart()
  initTimelineChart()
}

const initPieChart = () => {
  if (!pieChartRef.value) return
  if (pieChart) {
    pieChart.dispose()
  }
  pieChart = echarts.init(pieChartRef.value)
  const counts = { critical: 0, high: 0, medium: 0, low: 0 }
  bottlenecks.value.forEach(b => {
    const s = (b.severity || '').toLowerCase() || 'medium'
    if (counts[s] !== undefined) counts[s]++
  })
  const data = [
    { name: '严重', value: counts.critical, itemStyle: { color: severityColors.critical } },
    { name: '高', value: counts.high, itemStyle: { color: severityColors.high } },
    { name: '中', value: counts.medium, itemStyle: { color: severityColors.medium } },
    { name: '低', value: counts.low, itemStyle: { color: severityColors.low } }
  ].filter(item => item.value > 0)

  pieChart.setOption({
    backgroundColor: 'transparent',
    tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
    legend: {
      orient: 'vertical',
      right: '5%',
      top: 'center',
      textStyle: { color: '#a0aec0' }
    },
    series: [{
      name: '严重度分布',
      type: 'pie',
      radius: ['40%', '70%'],
      center: ['38%', '50%'],
      avoidLabelOverlap: false,
      itemStyle: { borderRadius: 6, borderColor: '#1e2a3a', borderWidth: 2 },
      label: {
        show: true,
        color: '#e2e8f0',
        formatter: '{b}\n{c}'
      },
      labelLine: { lineStyle: { color: '#4a5568' } },
      data: data.length > 0 ? data : [{ value: 0, name: '暂无数据', itemStyle: { color: '#4a5568' } }]
    }]
  })
}

const initBarChart = () => {
  if (!barChartRef.value) return
  if (barChart) {
    barChart.dispose()
  }
  barChart = echarts.init(barChartRef.value)
  const list = bottlenecks.value
  const categories = list.map((b, i) => b.type || b.name || `瓶颈${i + 1}`)
  const metricValues = list.map(b => {
    const v = b.metric_value
    const num = typeof v === 'string' ? parseFloat(v) : v
    return isNaN(num) ? 0 : num
  })
  const thresholds = list.map(b => {
    const v = b.threshold
    const num = typeof v === 'string' ? parseFloat(v) : v
    return isNaN(num) ? 0 : num
  })

  barChart.setOption({
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' }
    },
    legend: {
      data: ['指标值', '阈值'],
      textStyle: { color: '#a0aec0' },
      top: '2%'
    },
    grid: { left: '3%', right: '4%', bottom: '10%', containLabel: true },
    xAxis: {
      type: 'category',
      data: categories,
      axisLabel: { color: '#a0aec0', rotate: categories.length > 4 ? 20 : 0, interval: 0 },
      axisLine: { lineStyle: { color: '#4a5568' } }
    },
    yAxis: {
      type: 'value',
      axisLabel: { color: '#a0aec0' },
      axisLine: { lineStyle: { color: '#4a5568' } },
      splitLine: { lineStyle: { color: '#2d3748' } }
    },
    series: [
      {
        name: '指标值',
        type: 'bar',
        data: metricValues,
        barWidth: '30%',
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#f5222d' },
            { offset: 1, color: '#fa541c' }
          ]),
          borderRadius: [4, 4, 0, 0]
        }
      },
      {
        name: '阈值',
        type: 'bar',
        data: thresholds,
        barWidth: '30%',
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#1890ff' },
            { offset: 1, color: '#36cfc9' }
          ]),
          borderRadius: [4, 4, 0, 0]
        }
      }
    ]
  })
}

const initTimelineChart = () => {
  if (!timelineChartRef.value) return
  if (timelineChart) {
    timelineChart.dispose()
  }
  timelineChart = echarts.init(timelineChartRef.value)
  const list = bottlenecks.value

  let timeData = []
  let hasValidTime = false
  list.forEach(b => {
    const time = b.timestamp || b.time || b.detected_at || b.created_at
    if (time) {
      hasValidTime = true
      timeData.push({
        name: b.type || b.name || '瓶颈',
        value: [time, severityScore(b.severity)],
        severity: b.severity,
        description: b.description || ''
      })
    } else {
      const now = new Date()
      const fakeTime = new Date(now.getTime() - Math.random() * 3600000).toISOString()
      timeData.push({
        name: b.type || b.name || '瓶颈',
        value: [fakeTime, severityScore(b.severity)],
        severity: b.severity,
        description: b.description || ''
      })
    }
  })

  timeData.sort((a, b) => new Date(a.value[0]) - new Date(b.value[0]))

  timelineChart.setOption({
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'item',
      formatter: (params) => {
        const d = params.data
        const time = Array.isArray(d.value) ? d.value[0] : d.value
        return `${d.name}<br/>时间: ${formatTime(time)}<br/>严重度: ${severityLabel(d.severity)}<br/>${d.description || ''}`
      }
    },
    grid: { left: '3%', right: '5%', bottom: '10%', containLabel: true },
    xAxis: {
      type: 'time',
      axisLabel: { color: '#a0aec0' },
      axisLine: { lineStyle: { color: '#4a5568' } },
      splitLine: { lineStyle: { color: '#2d3748' } }
    },
    yAxis: {
      type: 'value',
      name: '严重度',
      nameTextStyle: { color: '#a0aec0' },
      min: 0,
      max: 4,
      interval: 1,
      axisLabel: {
        color: '#a0aec0',
        formatter: (val) => {
          const labels = { 0: '低', 1: '中', 2: '高', 3: '严重', 4: '严重' }
          return labels[val] || ''
        }
      },
      axisLine: { lineStyle: { color: '#4a5568' } },
      splitLine: { lineStyle: { color: '#2d3748' } }
    },
    series: [{
      name: '瓶颈时间线',
      type: 'scatter',
      data: timeData.map(d => ({
        ...d,
        itemStyle: { color: severityColors[(d.severity || '').toLowerCase()] || severityColors.medium }
      })),
      symbolSize: (val, params) => {
        const s = (params.data.severity || '').toLowerCase()
        return s === 'critical' ? 22 : s === 'high' ? 18 : s === 'medium' ? 14 : 10
      },
      label: {
        show: true,
        position: 'top',
        color: '#e2e8f0',
        fontSize: 11,
        formatter: (params) => params.data.name
      }
    }]
  })
}

const severityScore = (severity) => {
  const s = (severity || '').toLowerCase()
  const scores = { critical: 3.5, high: 2.5, medium: 1.5, low: 0.5 }
  return scores[s] || 1.5
}

const formatTime = (time) => {
  try {
    const d = new Date(time)
    if (isNaN(d.getTime())) return String(time)
    return d.toLocaleString('zh-CN')
  } catch (_) {
    return String(time)
  }
}

const handleResize = () => {
  pieChart?.resize()
  barChart?.resize()
  timelineChart?.resize()
}

watch(selectedReportId, (newVal) => {
  if (!newVal) {
    analysis.value = null
    bottlenecks.value = []
  }
})

onMounted(async () => {
  await loadReports()
  window.addEventListener('resize', handleResize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  pieChart?.dispose()
  barChart?.dispose()
  timelineChart?.dispose()
  pieChart = null
  barChart = null
  timelineChart = null
})
</script>

<style scoped>
.ai-bottleneck {
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
    radial-gradient(circle at 80% 50%, rgba(245, 34, 45, 0.1) 0%, transparent 50%);
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
  gap: 32px;
}

.header-stat {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 8px 20px;
  background: rgba(64, 169, 255, 0.08);
  border: 1px solid rgba(64, 169, 255, 0.2);
  border-radius: 8px;
  min-width: 80px;
}

.stat-num {
  font-size: 24px;
  font-weight: 700;
  color: #40a9ff;
}

.header-stat:last-child .stat-num {
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

/* 控制面板 */
.control-panel {
  margin-bottom: 24px;
}

.control-card {
  background: rgba(30, 42, 58, 0.7);
  border: 1px solid rgba(64, 169, 255, 0.15);
  border-radius: 12px;
  backdrop-filter: blur(10px);
}

.control-card :deep(.el-card__body) {
  padding: 20px 24px;
}

.control-row {
  display: flex;
  align-items: flex-end;
  gap: 16px;
  flex-wrap: wrap;
}

.control-item {
  flex: 1;
  min-width: 280px;
}

.control-label {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: #a0aec0;
  margin-bottom: 8px;
}

.report-select {
  width: 100%;
}

.analyze-btn {
  height: 32px;
  padding: 0 24px;
  background: linear-gradient(135deg, #1890ff, #40a9ff);
  border: none;
  font-weight: 500;
}

.analyze-btn:hover {
  background: linear-gradient(135deg, #40a9ff, #69b1ff);
}

.report-hint {
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

/* 分析结果 */
.analysis-result {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.overview-section {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
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

.header-icon.warning {
  color: #faad14;
}

.card-title {
  font-size: 15px;
  font-weight: 600;
  color: #e2e8f0;
  flex: 1;
}

.trend-tag {
  margin-left: auto;
}

/* 模型信息卡片 */
.model-info {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 16px;
}

.info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 13px;
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
}

.model-name {
  color: #40a9ff;
}

.confidence-section {
  background: rgba(15, 23, 42, 0.5);
  border-radius: 8px;
  padding: 14px;
}

.confidence-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.confidence-label {
  font-size: 13px;
  color: #8bb8e8;
}

.confidence-value {
  font-size: 22px;
  font-weight: 700;
}

.confidence-bar {
  margin-bottom: 8px;
}

.confidence-desc {
  font-size: 12px;
  color: #a0aec0;
  text-align: center;
}

/* 根因分析卡片 */
.root-cause-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.root-cause-text {
  font-size: 13px;
  line-height: 1.7;
  color: #e2e8f0;
  margin: 0;
  padding: 12px;
  background: rgba(15, 23, 42, 0.5);
  border-radius: 8px;
  border-left: 3px solid #40a9ff;
}

.suggestions-title {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  font-weight: 600;
  color: #52c41a;
  margin-bottom: 8px;
}

.suggestion-item {
  display: flex;
  gap: 10px;
  padding: 10px 12px;
  background: rgba(82, 196, 26, 0.06);
  border-radius: 6px;
  margin-bottom: 6px;
  border: 1px solid rgba(82, 196, 26, 0.1);
}

.suggestion-index {
  flex-shrink: 0;
  width: 20px;
  height: 20px;
  background: linear-gradient(135deg, #52c41a, #73d13d);
  color: #0f172a;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  font-weight: 700;
}

.suggestion-text {
  font-size: 13px;
  color: #e2e8f0;
  line-height: 1.6;
}

/* 趋势预测卡片 */
.trend-card {
  border: 1px solid rgba(250, 173, 20, 0.25);
}

.trend-content {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.trend-warning-banner {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 14px;
  background: linear-gradient(135deg, rgba(250, 173, 20, 0.15), rgba(245, 34, 45, 0.1));
  border: 1px solid rgba(250, 173, 20, 0.3);
  border-radius: 8px;
  color: #faad14;
  font-size: 13px;
  font-weight: 600;
}

.trend-text {
  font-size: 13px;
  line-height: 1.7;
  color: #e2e8f0;
  margin: 0;
  padding: 12px;
  background: rgba(15, 23, 42, 0.5);
  border-radius: 8px;
  border-left: 3px solid #faad14;
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

/* 瓶颈列表 */
.bottlenecks-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
  gap: 16px;
}

.bottleneck-card {
  background: rgba(30, 42, 58, 0.7);
  border: 1px solid rgba(64, 169, 255, 0.15);
  border-radius: 12px;
  padding: 18px;
  position: relative;
  overflow: hidden;
  transition: all 0.3s;
  backdrop-filter: blur(10px);
}

.bottleneck-card:hover {
  transform: translateY(-2px);
  border-color: rgba(64, 169, 255, 0.4);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
}

.bottleneck-top-bar {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
}

.severity-critical .bottleneck-top-bar { background: linear-gradient(90deg, #f5222d, #ff4d4f); }
.severity-high .bottleneck-top-bar { background: linear-gradient(90deg, #fa8c16, #ffa940); }
.severity-medium .bottleneck-top-bar { background: linear-gradient(90deg, #fadb14, #ffec3d); }
.severity-low .bottleneck-top-bar { background: linear-gradient(90deg, #1890ff, #36cfc9); }

.severity-critical { border-color: rgba(245, 34, 45, 0.3); }
.severity-high { border-color: rgba(250, 140, 22, 0.3); }
.severity-medium { border-color: rgba(250, 219, 20, 0.3); }
.severity-low { border-color: rgba(24, 144, 255, 0.3); }

.bottleneck-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.bottleneck-type {
  display: flex;
  align-items: center;
  gap: 8px;
}

.type-icon {
  font-size: 18px;
}

.severity-critical .type-icon { color: #f5222d; }
.severity-high .type-icon { color: #fa8c16; }
.severity-medium .type-icon { color: #fadb14; }
.severity-low .type-icon { color: #1890ff; }

.type-name {
  font-size: 15px;
  font-weight: 600;
  color: #e2e8f0;
}

.severity-tag {
  flex-shrink: 0;
}

.bottleneck-desc {
  font-size: 13px;
  color: #a0aec0;
  line-height: 1.6;
  margin: 0 0 14px 0;
}

.bottleneck-metrics {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: rgba(15, 23, 42, 0.6);
  border-radius: 8px;
  margin-bottom: 12px;
}

.metric-item {
  flex: 1;
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
  font-size: 18px;
  font-weight: 700;
  color: #e2e8f0;
}

.metric-value.severity-critical { color: #f5222d; }
.metric-value.severity-high { color: #fa8c16; }
.metric-value.severity-medium { color: #fadb14; }
.metric-value.severity-low { color: #1890ff; }
.metric-value.threshold { color: #8bb8e8; }

.metric-divider {
  color: #4a5568;
  display: flex;
  align-items: center;
}

.bottleneck-suggestion {
  display: flex;
  gap: 10px;
  padding: 12px;
  background: rgba(82, 196, 26, 0.06);
  border-radius: 8px;
  border: 1px solid rgba(82, 196, 26, 0.15);
}

.suggestion-icon {
  color: #52c41a;
  font-size: 16px;
  flex-shrink: 0;
  margin-top: 2px;
}

.suggestion-content {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.bottleneck-suggestion .suggestion-label {
  font-size: 11px;
  color: #52c41a;
  font-weight: 600;
}

.bottleneck-suggestion .suggestion-text {
  font-size: 12px;
  color: #e2e8f0;
  line-height: 1.5;
}

/* 图表区域 */
.charts-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.chart-card {
  background: rgba(30, 42, 58, 0.7);
  border: 1px solid rgba(64, 169, 255, 0.15);
  border-radius: 12px;
  backdrop-filter: blur(10px);
}

.chart-card-full {
  grid-column: 1 / -1;
}

.chart-card :deep(.el-card__header) {
  padding: 14px 20px;
  border-bottom: 1px solid rgba(64, 169, 255, 0.1);
}

.chart-card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 600;
  color: #e2e8f0;
}

.chart-card-header .el-icon {
  color: #40a9ff;
}

.chart-container {
  width: 100%;
  height: 320px;
}

.chart-card-full .chart-container {
  height: 360px;
}

/* Element Plus 暗色主题覆盖 */
.control-card :deep(.el-select__wrapper),
.info-card :deep(.el-input__wrapper) {
  background-color: rgba(15, 23, 42, 0.6);
  box-shadow: 0 0 0 1px rgba(64, 169, 255, 0.2) inset;
}

.control-card :deep(.el-select__wrapper:hover),
.control-card :deep(.el-select__wrapper.is-focused) {
  box-shadow: 0 0 0 1px #40a9ff inset;
}

.control-card :deep(.el-select__placeholder),
.control-card :deep(.el-select__selected-item) {
  color: #e2e8f0;
}

.info-card :deep(.el-progress-bar__outer) {
  background-color: rgba(15, 23, 42, 0.6);
}

/* 响应式 */
@media (max-width: 1200px) {
  .overview-section {
    grid-template-columns: 1fr;
  }

  .charts-grid {
    grid-template-columns: 1fr;
  }

  .bottlenecks-grid {
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
  }

  .main-container {
    padding: 16px;
  }

  .control-row {
    flex-direction: column;
    align-items: stretch;
  }

  .analyze-btn {
    width: 100%;
  }

  .loading-card {
    min-width: auto;
    padding: 32px 24px;
  }
}
</style>
