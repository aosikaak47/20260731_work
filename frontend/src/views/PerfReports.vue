<template>
  <div class="perf-reports">
    <div class="page-header">
      <h2>性能报告</h2>
      <p class="page-desc">查看性能测试报告和分析结果</p>
    </div>

    <el-card>
      <template #header>
        <div class="card-header">
          <span class="card-title">报告列表</span>
          <div class="header-actions">
            <el-input
              v-model="filter.testName"
              placeholder="搜索测试名称..."
              size="small"
              class="search-input"
              clearable
              @keyup.enter="handleSearch"
            />
            <el-select
              v-model="filter.status"
              size="small"
              placeholder="状态"
              class="status-select"
              clearable
            >
              <el-option label="已完成" value="completed" />
              <el-option label="运行中" value="running" />
            </el-select>
            <el-button type="primary" size="small" :icon="icons.Search" @click="handleSearch">
              搜索
            </el-button>
          </div>
        </div>
      </template>

      <div v-loading="loading">
        <div v-if="reports.length === 0 && !loading" class="empty-state">
          <el-icon :size="48" class="empty-icon"><component :is="icons.Box" /></el-icon>
          <span>暂无性能报告</span>
        </div>

        <el-table v-else :data="reports" stripe border>
          <el-table-column prop="id" label="报告ID" width="80" />
          <el-table-column prop="test_name" label="测试名称" min-width="160" show-overflow-tooltip />
          <el-table-column prop="status" label="状态" width="100">
            <template #default="scope">
              <el-tag :type="statusTagType(scope.row.status)" size="small">
                {{ statusLabel(scope.row.status) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="start_time" label="开始时间" width="160" />
          <el-table-column prop="duration" label="耗时" width="100">
            <template #default="scope">{{ formatDuration(scope.row.duration) }}</template>
          </el-table-column>
          <el-table-column prop="concurrency" label="并发数" width="90" />
          <el-table-column prop="summary.total_requests" label="总请求" width="100">
            <template #default="scope">{{ scope.row.summary?.total_requests ?? '-' }}</template>
          </el-table-column>
          <el-table-column prop="summary.error_rate" label="错误率" width="100">
            <template #default="scope">
              <span :class="errorRateClass(scope.row.summary?.error_rate)">
                {{ formatPercent(scope.row.summary?.error_rate) }}
              </span>
            </template>
          </el-table-column>
          <el-table-column prop="summary.avg_response_time" label="平均RT(ms)" width="110">
            <template #default="scope">{{ scope.row.summary?.avg_response_time ?? '-' }}</template>
          </el-table-column>
          <el-table-column prop="summary.tps" label="TPS" width="90">
            <template #default="scope">{{ scope.row.summary?.tps ?? '-' }}</template>
          </el-table-column>
          <el-table-column label="操作" width="200" class-name="action-cell" fixed="right">
            <template #default="scope">
              <div class="action-btns">
                <el-button size="small" type="primary" link :icon="icons.View" @click="handleView(scope.row)">
                  详情
                </el-button>
                <el-button size="small" type="danger" link :icon="icons.Delete" @click="handleDelete(scope.row)">
                  删除
                </el-button>
              </div>
            </template>
          </el-table-column>
        </el-table>

        <el-pagination
          v-if="reports.length > 0"
          class="pagination"
          layout="total, prev, pager, next, jumper"
          :total="total"
          :page-size="pageSize"
          :current-page="currentPage"
          @current-change="handlePageChange"
        />
      </div>
    </el-card>

    <el-dialog
      v-model="detailDialogVisible"
      title="性能报告详情"
      width="90%"
      top="3vh"
      class="detail-dialog"
      @closed="handleDialogClosed"
    >
      <div v-loading="detailLoading" class="report-detail" v-if="currentReport">
        <!-- 报告概要 -->
        <div class="detail-header">
          <div class="header-left">
            <h3>{{ currentReport.test_name }}</h3>
            <span class="meta-tag">报告ID: {{ currentReport.id }}</span>
            <span class="meta-tag">并发: {{ currentReport.concurrency }}</span>
            <span class="meta-tag">耗时: {{ formatDuration(currentReport.duration) }}</span>
          </div>
          <div class="header-right">
            <el-tag :type="statusTagType(currentReport.status)" size="large">
              {{ statusLabel(currentReport.status) }}
            </el-tag>
          </div>
        </div>

        <div class="detail-info">
          <div class="info-row">
            <span class="info-label">开始时间:</span>
            <span>{{ currentReport.start_time }}</span>
          </div>
          <div class="info-row">
            <span class="info-label">结束时间:</span>
            <span>{{ currentReport.end_time }}</span>
          </div>
        </div>

        <!-- 关键指标卡片 -->
        <div class="section-title">关键指标</div>
        <div class="metrics-grid">
          <div class="metric-card" v-for="m in summaryMetrics" :key="m.label" :class="m.cls">
            <div class="metric-value">{{ m.value }}</div>
            <div class="metric-label">{{ m.label }}</div>
          </div>
        </div>

        <!-- 趋势图表 -->
        <div class="section-title">趋势图表</div>
        <div class="charts-grid">
          <el-card class="chart-card" shadow="never">
            <template #header><span class="chart-title">TPS 趋势</span></template>
            <div ref="tpsChartRef" class="chart-container"></div>
          </el-card>
          <el-card class="chart-card" shadow="never">
            <template #header><span class="chart-title">响应时间趋势</span></template>
            <div ref="rtChartRef" class="chart-container"></div>
          </el-card>
          <el-card class="chart-card" shadow="never">
            <template #header><span class="chart-title">CPU / 内存趋势</span></template>
            <div ref="resourceChartRef" class="chart-container"></div>
          </el-card>
          <el-card class="chart-card" shadow="never">
            <template #header><span class="chart-title">错误率趋势</span></template>
            <div ref="errorChartRef" class="chart-container"></div>
          </el-card>
        </div>

        <!-- 性能瓶颈 -->
        <div v-if="currentReport.bottlenecks && currentReport.bottlenecks.length > 0">
          <div class="section-title">性能瓶颈</div>
          <el-table :data="currentReport.bottlenecks" border size="small">
            <el-table-column type="index" label="#" width="50" />
            <el-table-column prop="type" label="瓶颈类型" width="140" />
            <el-table-column prop="description" label="描述" min-width="240" show-overflow-tooltip />
            <el-table-column prop="impact" label="影响" min-width="160" show-overflow-tooltip />
            <el-table-column prop="severity" label="严重程度" width="110">
              <template #default="scope">
                <el-tag :type="severityTagType(scope.row.severity)" size="small">
                  {{ scope.row.severity || '-' }}
                </el-tag>
              </template>
            </el-table-column>
          </el-table>
        </div>

        <!-- 异常事件 -->
        <div v-if="currentReport.anomalies && currentReport.anomalies.length > 0">
          <div class="section-title">异常事件</div>
          <el-table :data="currentReport.anomalies" border size="small">
            <el-table-column type="index" label="#" width="50" />
            <el-table-column prop="timestamp" label="时间点" width="160" />
            <el-table-column prop="type" label="异常类型" width="140" />
            <el-table-column prop="description" label="描述" min-width="260" show-overflow-tooltip />
            <el-table-column prop="severity" label="严重程度" width="110">
              <template #default="scope">
                <el-tag :type="severityTagType(scope.row.severity)" size="small">
                  {{ scope.row.severity || '-' }}
                </el-tag>
              </template>
            </el-table-column>
          </el-table>
        </div>

        <!-- AI 分析 -->
        <div v-if="currentReport.ai_analysis" class="ai-analysis-section">
          <div class="section-title">AI 分析</div>
          <el-card shadow="never" class="ai-card">
            <div class="ai-grid">
              <div class="ai-row">
                <span class="ai-label">瓶颈类型:</span>
                <span class="ai-value">{{ currentReport.ai_analysis.bottleneck_type || '-' }}</span>
              </div>
              <div class="ai-row">
                <span class="ai-label">置信度:</span>
                <el-progress
                  :percentage="aiConfidence"
                  :color="aiConfidenceColor"
                  class="ai-progress"
                />
              </div>
              <div class="ai-row">
                <span class="ai-label">根本原因:</span>
                <span class="ai-value">{{ currentReport.ai_analysis.root_cause || '-' }}</span>
              </div>
              <div class="ai-row">
                <span class="ai-label">趋势预测:</span>
                <span class="ai-value">{{ currentReport.ai_analysis.trend_prediction || '-' }}</span>
              </div>
            </div>
            <div class="ai-suggestions" v-if="aiSuggestions.length > 0">
              <div class="ai-label">优化建议:</div>
              <ol class="suggestions-list">
                <li v-for="(s, idx) in aiSuggestions" :key="idx">{{ s }}</li>
              </ol>
            </div>
          </el-card>
        </div>
      </div>

      <template #footer>
        <el-button @click="detailDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted, nextTick } from 'vue'
import * as icons from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import { ElMessage, ElMessageBox } from 'element-plus'

const loading = ref(false)
const detailLoading = ref(false)
const reports = ref([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(10)

const filter = reactive({
  testName: '',
  status: ''
})

const detailDialogVisible = ref(false)
const currentReport = ref(null)

const tpsChartRef = ref(null)
const rtChartRef = ref(null)
const resourceChartRef = ref(null)
const errorChartRef = ref(null)

let tpsChartInstance = null
let rtChartInstance = null
let resourceChartInstance = null
let errorChartInstance = null

const summaryMetrics = computed(() => {
  const s = currentReport.value?.summary || {}
  return [
    { label: '总请求数', value: s.total_requests ?? '-', cls: 'm-blue' },
    { label: '成功请求', value: s.success_requests ?? '-', cls: 'm-green' },
    { label: '失败请求', value: s.failed_requests ?? '-', cls: 'm-red' },
    { label: '错误率', value: formatPercent(s.error_rate), cls: errorRateClass(s.error_rate) },
    { label: '平均 RT (ms)', value: s.avg_response_time ?? '-', cls: 'm-blue' },
    { label: '最小 RT (ms)', value: s.min_response_time ?? '-', cls: 'm-green' },
    { label: '最大 RT (ms)', value: s.max_response_time ?? '-', cls: 'm-red' },
    { label: 'P90 (ms)', value: s.p90_response_time ?? '-', cls: 'm-orange' },
    { label: 'P95 (ms)', value: s.p95_response_time ?? '-', cls: 'm-orange' },
    { label: 'P99 (ms)', value: s.p99_response_time ?? '-', cls: 'm-red' },
    { label: 'TPS', value: s.tps ?? '-', cls: 'm-blue' },
    { label: 'QPS', value: s.qps ?? '-', cls: 'm-blue' },
    { label: '平均 CPU (%)', value: s.avg_cpu ?? '-', cls: 'm-purple' },
    { label: '峰值 CPU (%)', value: s.max_cpu ?? '-', cls: 'm-purple' },
    { label: '平均内存 (MB)', value: s.avg_memory ?? '-', cls: 'm-cyan' },
    { label: '峰值内存 (MB)', value: s.max_memory ?? '-', cls: 'm-cyan' }
  ]
})

const aiSuggestions = computed(() => {
  const sug = currentReport.value?.ai_analysis?.suggestions
  if (Array.isArray(sug)) return sug
  if (typeof sug === 'string' && sug.trim()) return [sug]
  return []
})

const aiConfidence = computed(() => {
  const c = currentReport.value?.ai_analysis?.confidence
  const num = Number(c)
  if (isNaN(num)) return 0
  if (num <= 1) return Math.round(num * 100)
  return Math.min(100, Math.max(0, Math.round(num)))
})

const aiConfidenceColor = computed(() => {
  const v = aiConfidence.value
  if (v >= 80) return '#10b981'
  if (v >= 50) return '#f59e0b'
  return '#ef4444'
})

function statusTagType(status) {
  if (status === 'completed') return 'success'
  if (status === 'running') return 'primary'
  return 'info'
}

function statusLabel(status) {
  if (status === 'completed') return '已完成'
  if (status === 'running') return '运行中'
  return status || '-'
}

function severityTagType(severity) {
  const s = String(severity || '').toLowerCase()
  if (s.includes('high') || s.includes('严重') || s === 'high') return 'danger'
  if (s.includes('medium') || s.includes('中') || s === 'medium') return 'warning'
  if (s.includes('low') || s.includes('低') || s === 'low') return 'success'
  return 'info'
}

function errorRateClass(rate) {
  const num = Number(rate)
  if (isNaN(num)) return ''
  if (num >= 5) return 'm-red'
  if (num >= 1) return 'm-orange'
  return 'm-green'
}

function formatPercent(rate) {
  const num = Number(rate)
  if (isNaN(num) || rate == null) return '-'
  if (num <= 1 && num > 0) return (num * 100).toFixed(2) + '%'
  return num.toFixed(2) + '%'
}

function formatDuration(duration) {
  if (duration == null) return '-'
  const num = Number(duration)
  if (isNaN(num)) return duration
  if (num < 1) return num + 's'
  const minutes = Math.floor(num / 60)
  const seconds = (num % 60).toFixed(0)
  if (minutes === 0) return seconds + 's'
  return minutes + 'm ' + seconds + 's'
}

async function loadReports() {
  loading.value = true
  try {
    const params = new URLSearchParams()
    params.set('page', currentPage.value)
    params.set('page_size', pageSize.value)
    if (filter.testName) params.set('test_name', filter.testName)
    if (filter.status) params.set('status', filter.status)

    const response = await fetch(`/api/v1/perf/reports?${params.toString()}`)
    const data = await response.json()
    if (data.success) {
      reports.value = data.reports || []
      total.value = data.total || 0
    } else {
      ElMessage.error(data.message || '加载报告失败')
    }
  } catch (error) {
    console.error('加载性能报告失败:', error)
    ElMessage.error('加载性能报告失败')
  } finally {
    loading.value = false
  }
}

function handleSearch() {
  currentPage.value = 1
  loadReports()
}

function handlePageChange(page) {
  currentPage.value = page
  loadReports()
}

async function handleView(report) {
  detailDialogVisible.value = true
  detailLoading.value = true
  currentReport.value = report
  try {
    const response = await fetch(`/api/v1/perf/reports/${report.id}`)
    const data = await response.json()
    if (data.success && data.report) {
      currentReport.value = data.report
    } else {
      ElMessage.warning('未能获取详细报告数据')
    }
  } catch (error) {
    console.error('加载报告详情失败:', error)
    ElMessage.error('加载报告详情失败')
  } finally {
    detailLoading.value = false
    await nextTick()
    initAllCharts()
  }
}

function handleDialogClosed() {
  disposeCharts()
  currentReport.value = null
}

async function handleDelete(report) {
  try {
    await ElMessageBox.confirm(
      `确定要删除报告「${report.test_name || report.id}」吗？`,
      '删除确认',
      { type: 'warning', confirmButtonText: '删除', cancelButtonText: '取消' }
    )
  } catch {
    return
  }

  try {
    const response = await fetch(`/api/v1/perf/reports/${report.id}`, { method: 'DELETE' })
    const data = await response.json()
    if (data.success) {
      ElMessage.success('删除成功')
      loadReports()
    } else {
      ElMessage.error(data.message || '删除失败')
    }
  } catch (error) {
    console.error('删除报告失败:', error)
    ElMessage.error('删除报告失败')
  }
}

function getTimeline() {
  const tl = currentReport.value?.timeline || []
  const timestamps = tl.map(p => p.timestamp || p.time || '')
  const toNum = (v) => {
    const n = Number(v)
    return isNaN(n) ? 0 : n
  }
  return {
    timestamps,
    tps: tl.map(p => toNum(p.tps)),
    avgRt: tl.map(p => toNum(p.avg_response_time ?? p.response_time)),
    maxRt: tl.map(p => toNum(p.max_response_time)),
    cpu: tl.map(p => toNum(p.cpu)),
    memory: tl.map(p => toNum(p.memory)),
    errorRate: tl.map(p => toNum(p.error_rate))
  }
}

function initAllCharts() {
  disposeCharts()
  if (tpsChartRef.value) {
    tpsChartInstance = echarts.init(tpsChartRef.value)
    renderTpsChart()
  }
  if (rtChartRef.value) {
    rtChartInstance = echarts.init(rtChartRef.value)
    renderRtChart()
  }
  if (resourceChartRef.value) {
    resourceChartInstance = echarts.init(resourceChartRef.value)
    renderResourceChart()
  }
  if (errorChartRef.value) {
    errorChartInstance = echarts.init(errorChartRef.value)
    renderErrorChart()
  }
}

function renderTpsChart() {
  if (!tpsChartInstance) return
  const tl = getTimeline()
  tpsChartInstance.setOption({
    tooltip: { trigger: 'axis' },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: tl.timestamps,
      axisLine: { lineStyle: { color: '#d1d5db' } },
      axisLabel: { color: '#6b7280', fontSize: 11 }
    },
    yAxis: {
      type: 'value',
      axisLine: { lineStyle: { color: '#d1d5db' } },
      axisLabel: { color: '#6b7280' },
      splitLine: { lineStyle: { color: '#f3f4f6' } }
    },
    series: [{
      name: 'TPS',
      type: 'line',
      smooth: true,
      showSymbol: false,
      data: tl.tps,
      itemStyle: { color: '#6366f1' },
      areaStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: 'rgba(99, 102, 241, 0.3)' },
          { offset: 1, color: 'rgba(99, 102, 241, 0.02)' }
        ])
      }
    }]
  })
}

function renderRtChart() {
  if (!rtChartInstance) return
  const tl = getTimeline()
  rtChartInstance.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['平均 RT', '最大 RT'], textStyle: { color: '#6b7280' }, top: 0 },
    grid: { left: '3%', right: '4%', bottom: '3%', top: 30, containLabel: true },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: tl.timestamps,
      axisLine: { lineStyle: { color: '#d1d5db' } },
      axisLabel: { color: '#6b7280', fontSize: 11 }
    },
    yAxis: {
      type: 'value',
      axisLine: { lineStyle: { color: '#d1d5db' } },
      axisLabel: { color: '#6b7280' },
      splitLine: { lineStyle: { color: '#f3f4f6' } }
    },
    series: [
      {
        name: '平均 RT',
        type: 'line',
        smooth: true,
        showSymbol: false,
        data: tl.avgRt,
        itemStyle: { color: '#f59e0b' }
      },
      {
        name: '最大 RT',
        type: 'line',
        smooth: true,
        showSymbol: false,
        data: tl.maxRt,
        itemStyle: { color: '#ef4444' }
      }
    ]
  })
}

function renderResourceChart() {
  if (!resourceChartInstance) return
  const tl = getTimeline()
  resourceChartInstance.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['CPU (%)', '内存 (MB)'], textStyle: { color: '#6b7280' }, top: 0 },
    grid: { left: '3%', right: '4%', bottom: '3%', top: 30, containLabel: true },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: tl.timestamps,
      axisLine: { lineStyle: { color: '#d1d5db' } },
      axisLabel: { color: '#6b7280', fontSize: 11 }
    },
    yAxis: [
      {
        type: 'value',
        name: 'CPU (%)',
        position: 'left',
        axisLine: { lineStyle: { color: '#d1d5db' } },
        axisLabel: { color: '#6b7280' },
        splitLine: { lineStyle: { color: '#f3f4f6' } }
      },
      {
        type: 'value',
        name: '内存 (MB)',
        position: 'right',
        axisLine: { lineStyle: { color: '#d1d5db' } },
        axisLabel: { color: '#6b7280' },
        splitLine: { show: false }
      }
    ],
    series: [
      {
        name: 'CPU (%)',
        type: 'line',
        smooth: true,
        showSymbol: false,
        data: tl.cpu,
        itemStyle: { color: '#8b5cf6' }
      },
      {
        name: '内存 (MB)',
        type: 'line',
        smooth: true,
        showSymbol: false,
        yAxisIndex: 1,
        data: tl.memory,
        itemStyle: { color: '#06b6d4' }
      }
    ]
  })
}

function renderErrorChart() {
  if (!errorChartInstance) return
  const tl = getTimeline()
  errorChartInstance.setOption({
    tooltip: {
      trigger: 'axis',
      valueFormatter: (v) => (v == null ? '-' : Number(v).toFixed(2) + '%')
    },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: tl.timestamps,
      axisLine: { lineStyle: { color: '#d1d5db' } },
      axisLabel: { color: '#6b7280', fontSize: 11 }
    },
    yAxis: {
      type: 'value',
      axisLine: { lineStyle: { color: '#d1d5db' } },
      axisLabel: { color: '#6b7280', formatter: '{value}%' },
      splitLine: { lineStyle: { color: '#f3f4f6' } }
    },
    series: [{
      name: '错误率',
      type: 'line',
      smooth: true,
      showSymbol: false,
      data: tl.errorRate,
      itemStyle: { color: '#ef4444' },
      areaStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: 'rgba(239, 68, 68, 0.3)' },
          { offset: 1, color: 'rgba(239, 68, 68, 0.02)' }
        ])
      }
    }]
  })
}

function disposeCharts() {
  tpsChartInstance?.dispose()
  rtChartInstance?.dispose()
  resourceChartInstance?.dispose()
  errorChartInstance?.dispose()
  tpsChartInstance = null
  rtChartInstance = null
  resourceChartInstance = null
  errorChartInstance = null
}

function handleResize() {
  tpsChartInstance?.resize()
  rtChartInstance?.resize()
  resourceChartInstance?.resize()
  errorChartInstance?.resize()
}

onMounted(() => {
  loadReports()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  disposeCharts()
})
</script>

<style scoped>
.perf-reports { padding: 20px; }

.page-header { margin-bottom: 24px; }
.page-header h2 { font-size: 24px; font-weight: 600; color: #1f2937; margin-bottom: 4px; }
.page-desc { font-size: 14px; color: #6b7280; }

.card-header { display: flex; align-items: center; justify-content: space-between; }
.card-title { font-size: 16px; font-weight: 600; }
.header-actions { display: flex; gap: 12px; align-items: center; }
.search-input { width: 220px; }
.status-select { width: 140px; }

.empty-state {
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  padding: 60px; color: #9ca3af; gap: 12px;
}
.empty-icon { color: #c0c4cc; }

.pagination { display: flex; justify-content: flex-end; margin-top: 16px; }

.detail-dialog :deep(.el-dialog__body) { padding: 16px 20px; }

.report-detail { padding: 4px; }

.detail-header {
  display: flex; justify-content: space-between; align-items: center;
  margin-bottom: 12px; flex-wrap: wrap; gap: 12px;
}
.header-left { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
.header-left h3 { font-size: 18px; font-weight: 600; color: #1f2937; margin: 0; }
.meta-tag {
  background-color: #e0e7ff; color: #4338ca; padding: 4px 10px;
  border-radius: 4px; font-size: 12px;
}

.detail-info {
  margin-bottom: 16px; padding: 12px 16px;
  background-color: #f9fafb; border-radius: 8px;
}
.info-row { display: flex; gap: 8px; margin-bottom: 4px; font-size: 13px; }
.info-row:last-child { margin-bottom: 0; }
.info-label { color: #6b7280; min-width: 70px; }

.section-title {
  font-size: 15px; font-weight: 600; color: #1f2937;
  margin: 20px 0 12px; padding-left: 8px;
  border-left: 3px solid #6366f1;
}

.metrics-grid {
  display: grid; grid-template-columns: repeat(auto-fill, minmax(170px, 1fr));
  gap: 12px;
}
.metric-card {
  padding: 16px; border-radius: 8px; background-color: #f9fafb;
  border: 1px solid #e5e7eb; border-left: 4px solid #6366f1;
  transition: transform 0.15s ease, box-shadow 0.15s ease;
}
.metric-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.06);
}
.metric-value { font-size: 22px; font-weight: 700; color: #1f2937; }
.metric-label { font-size: 12px; color: #6b7280; margin-top: 4px; }

.metric-card.m-blue { border-left-color: #6366f1; }
.metric-card.m-green { border-left-color: #10b981; }
.metric-card.m-green .metric-value { color: #10b981; }
.metric-card.m-red { border-left-color: #ef4444; }
.metric-card.m-red .metric-value { color: #ef4444; }
.metric-card.m-orange { border-left-color: #f59e0b; }
.metric-card.m-orange .metric-value { color: #f59e0b; }
.metric-card.m-purple { border-left-color: #8b5cf6; }
.metric-card.m-purple .metric-value { color: #8b5cf6; }
.metric-card.m-cyan { border-left-color: #06b6d4; }
.metric-card.m-cyan .metric-value { color: #06b6d4; }

.charts-grid {
  display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px;
}
.chart-card { border: 1px solid #e5e7eb; }
.chart-card :deep(.el-card__header) { padding: 10px 14px; background-color: #f9fafb; }
.chart-card :deep(.el-card__body) { padding: 8px; }
.chart-title { font-size: 13px; font-weight: 600; color: #374151; }
.chart-container { width: 100%; height: 260px; }

.ai-analysis-section { margin-top: 20px; }
.ai-card { border: 1px solid #e5e7eb; background-color: #fafafa; }
.ai-card :deep(.el-card__body) { padding: 16px; }
.ai-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px 24px; }
.ai-row { display: flex; align-items: center; gap: 8px; font-size: 13px; flex-wrap: wrap; }
.ai-label { color: #6b7280; min-width: 80px; font-weight: 500; }
.ai-value { color: #1f2937; }
.ai-progress { flex: 1; min-width: 120px; }
.ai-suggestions { margin-top: 16px; padding-top: 12px; border-top: 1px dashed #e5e7eb; }
.suggestions-list { margin: 8px 0 0; padding-left: 20px; color: #374151; font-size: 13px; line-height: 1.8; }

@media (max-width: 1200px) {
  .charts-grid { grid-template-columns: 1fr; }
}
@media (max-width: 768px) {
  .metrics-grid { grid-template-columns: repeat(2, 1fr); }
  .ai-grid { grid-template-columns: 1fr; }
}
</style>
