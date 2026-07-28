<template>
  <div class="iteration-analysis">
    <div class="page-header">
      <h2>迭代质量分析</h2>
      <p class="page-desc">分析迭代测试质量数据</p>
    </div>

    <div class="filter-row">
      <span class="filter-label">选择迭代：</span>
      <el-select v-model="selectedIteration" placeholder="请选择迭代" style="width: 240px" @change="handleIterationChange">
        <el-option v-for="iter in iterations" :key="iter.id" :label="iter.name" :value="iter.id">
          <span>{{ iter.name }}</span>
          <el-tag style="margin-left: 8px" :type="iter.status === '进行中' ? 'warning' : iter.status === '已完成' ? 'success' : 'info'">
            {{ iter.status }}
          </el-tag>
        </el-option>
      </el-select>
      <el-button type="success" @click="handleExport">
        <el-icon><component :is="icons.Download" /></el-icon>
        导出报表
      </el-button>
    </div>

    <div v-if="currentIteration" class="iteration-info">
      <el-card class="info-card">
        <div class="info-row">
          <div class="info-item">
            <span class="info-label">迭代周期：</span>
            <span class="info-value">{{ currentIteration.startDate }} ~ {{ currentIteration.endDate }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">负责人：</span>
            <span class="info-value">{{ currentIteration.owner }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">项目：</span>
            <span class="info-value">{{ currentIteration.project }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">迭代目标：</span>
            <span class="info-value">{{ currentIteration.goal }}</span>
          </div>
        </div>
      </el-card>
    </div>

    <div class="metrics-row">
      <el-card class="metric-card">
        <div class="metric-content">
          <div class="metric-icon" style="background-color: rgba(99, 102, 241, 0.12)">
            <el-icon :size="22" style="color: #6366f1"><component :is="icons.Document" /></el-icon>
          </div>
          <div class="metric-info">
            <div class="metric-value">{{ qualityMetrics.totalCases }}</div>
            <div class="metric-title">总用例数</div>
          </div>
        </div>
      </el-card>
      <el-card class="metric-card">
        <div class="metric-content">
          <div class="metric-icon" style="background-color: rgba(16, 185, 129, 0.12)">
            <el-icon :size="22" style="color: #10b981"><component :is="icons.Check" /></el-icon>
          </div>
          <div class="metric-info">
            <div class="metric-value metric-success">{{ qualityMetrics.passRate }}%</div>
            <div class="metric-title">通过率</div>
          </div>
        </div>
      </el-card>
      <el-card class="metric-card">
        <div class="metric-content">
          <div class="metric-icon" style="background-color: rgba(239, 68, 68, 0.12)">
            <el-icon :size="22" style="color: #ef4444"><component :is="icons.Bell" /></el-icon>
          </div>
          <div class="metric-info">
            <div class="metric-value metric-danger">{{ qualityMetrics.defectCount }}</div>
            <div class="metric-title">缺陷数</div>
          </div>
        </div>
      </el-card>
      <el-card class="metric-card">
        <div class="metric-content">
          <div class="metric-icon" style="background-color: rgba(6, 182, 212, 0.12)">
            <el-icon :size="22" style="color: #06b6d4"><component :is="icons.CircleCheck" /></el-icon>
          </div>
          <div class="metric-info">
            <div class="metric-value metric-info">{{ qualityMetrics.coverageRate }}%</div>
            <div class="metric-title">覆盖率</div>
          </div>
        </div>
      </el-card>
    </div>

    <div class="charts-row">
      <el-card class="chart-card">
        <template #header>
          <span class="card-title">多维度质量评估</span>
        </template>
        <div ref="radarChartRef" class="chart-container"></div>
      </el-card>

      <el-card class="chart-card">
        <template #header>
          <span class="card-title">缺陷分布</span>
        </template>
        <div ref="defectChartRef" class="chart-container"></div>
      </el-card>
    </div>

    <el-card class="chart-card-full">
      <template #header>
        <span class="card-title">迭代对比分析</span>
      </template>
      <div ref="compareChartRef" class="chart-container-large"></div>
    </el-card>

    <el-card style="margin-top: 24px">
      <template #header>
        <div class="card-header">
          <span class="card-title">迭代缺陷明细</span>
          <span class="card-total">共 {{ defectList.length }} 个缺陷</span>
        </div>
      </template>
      <el-table :data="defectList" stripe border>
        <el-table-column prop="id" label="缺陷编号" width="120" />
        <el-table-column prop="title" label="缺陷标题" min-width="220" show-overflow-tooltip />
        <el-table-column prop="module" label="模块" width="150" />
        <el-table-column prop="severity" label="严重程度" width="120">
          <template #default="scope">
            <el-tag :type="scope.row.severity === '致命' ? 'danger' : scope.row.severity === '严重' ? 'warning' : 'info'">
              {{ scope.row.severity }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="type" label="缺陷类型" width="120" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="scope">
            <el-tag :type="scope.row.status === '已修复' ? 'success' : scope.row.status === '待修复' ? 'warning' : 'info'">
              {{ scope.row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="foundDate" label="发现日期" width="120" />
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onBeforeUnmount, nextTick } from 'vue'
import * as echarts from 'echarts'
import * as XLSX from 'xlsx'
import { ElMessage } from 'element-plus'
import * as icons from '@element-plus/icons-vue'
import { useProjects } from '../composables/useProjects'

const { currentProject } = useProjects()

const loading = ref(false)

const iterations = ref([])
const selectedIteration = ref('')
const currentIteration = computed(() => iterations.value.find(i => i.id === selectedIteration.value))

const qualityMetrics = reactive({
  totalCases: 0,
  passRate: 0,
  defectCount: 0,
  coverageRate: 0
})

const defectList = ref([])

const radarChartRef = ref(null)
const defectChartRef = ref(null)
const compareChartRef = ref(null)
let radarChart = null
let defectChart = null
let compareChart = null

const FALLBACK_ITERATIONS = [
  { id: 'iter_2026_sprint12', name: 'Sprint 12 (07/15 - 07/28)', status: '已完成', startDate: '2026-07-15', endDate: '2026-07-28', owner: '张小明', project: '智能测试平台', goal: '完成AI用例生成模块测试' },
  { id: 'iter_2026_sprint11', name: 'Sprint 11 (07/01 - 07/14)', status: '已完成', startDate: '2026-07-01', endDate: '2026-07-14', owner: '李华', project: '智能测试平台', goal: '接口自动化覆盖率提升至80%' },
  { id: 'iter_2026_sprint10', name: 'Sprint 10 (06/17 - 06/30)', status: '已完成', startDate: '2026-06-17', endDate: '2026-06-30', owner: '王强', project: '党建系统', goal: '完成用例管理模块重构测试' },
  { id: 'iter_2026_sprint13', name: 'Sprint 13 (07/29 - 08/11)', status: '进行中', startDate: '2026-07-29', endDate: '2026-08-11', owner: '赵敏', project: '智能测试平台', goal: '性能优化与安全测试' },
  { id: 'iter_2026_sprint09', name: 'Sprint 9 (06/03 - 06/16)', status: '已完成', startDate: '2026-06-03', endDate: '2026-06-16', owner: '张伟', project: '电商平台', goal: 'UI自动化覆盖率达标' }
]

const FALLBACK_METRICS = {
  'iter_2026_sprint12': { totalCases: 320, passRate: 94.5, defectCount: 18, coverageRate: 86.2 },
  'iter_2026_sprint11': { totalCases: 310, passRate: 93.6, defectCount: 20, coverageRate: 82.5 },
  'iter_2026_sprint10': { totalCases: 300, passRate: 92.8, defectCount: 19, coverageRate: 80.1 },
  'iter_2026_sprint13': { totalCases: 290, passRate: 96.2, defectCount: 12, coverageRate: 88.7 },
  'iter_2026_sprint09': { totalCases: 280, passRate: 91.5, defectCount: 22, coverageRate: 76.3 }
}

const FALLBACK_DEFECTS = [
  { id: 'BUG-1001', title: 'AI用例生成结果排序逻辑异常', module: 'AI智能用例生成', severity: '严重', type: '功能缺陷', status: '已修复', foundDate: '2026-07-20' },
  { id: 'BUG-1002', title: '批量执行时部分用例超时未返回', module: '接口自动化', severity: '严重', type: '性能缺陷', status: '已修复', foundDate: '2026-07-21' },
  { id: 'BUG-1003', title: '用例详情页面数据展示错位', module: '用例管理', severity: '一般', type: 'UI缺陷', status: '待修复', foundDate: '2026-07-19' },
  { id: 'BUG-1004', title: '登录接口在高并发下响应缓慢', module: '接口自动化', severity: '严重', type: '性能缺陷', status: '已修复', foundDate: '2026-07-18' },
  { id: 'BUG-1005', title: '测试报告导出格式异常', module: '报告导出', severity: '一般', type: '功能缺陷', status: '已修复', foundDate: '2026-07-22' },
  { id: 'BUG-1006', title: 'UI自动化脚本在Chrome下执行失败', module: 'UI自动化', severity: '致命', type: '兼容性缺陷', status: '待修复', foundDate: '2026-07-23' },
  { id: 'BUG-1007', title: '用例标签筛选功能失效', module: '用例管理', severity: '一般', type: '功能缺陷', status: '已修复', foundDate: '2026-07-17' },
  { id: 'BUG-1008', title: '性能测试数据统计偏差', module: '性能测试', severity: '一般', type: '逻辑缺陷', status: '待修复', foundDate: '2026-07-24' }
]

const FALLBACK_RADAR = {
  current: [86, 94.5, 88, 78, 92, 90],
  previous: [78, 91, 82, 72, 85, 86]
}

const FALLBACK_DEFECT_DISTRIBUTION = [
  { value: 5, name: '功能缺陷', itemStyle: { color: '#ef4444' } },
  { value: 4, name: '性能缺陷', itemStyle: { color: '#f59e0b' } },
  { value: 3, name: 'UI缺陷', itemStyle: { color: '#3b82f6' } },
  { value: 3, name: '逻辑缺陷', itemStyle: { color: '#8b5cf6' } },
  { value: 2, name: '兼容性缺陷', itemStyle: { color: '#06b6d4' } },
  { value: 1, name: '其他', itemStyle: { color: '#6b7280' } }
]

const FALLBACK_COMPARE = {
  iterations: ['Sprint 9', 'Sprint 10', 'Sprint 11', 'Sprint 12', 'Sprint 13'],
  totalCases: [280, 300, 310, 320, 290],
  defectCounts: [22, 19, 20, 18, 12],
  passRates: [91.5, 92.8, 93.6, 94.5, 96.2]
}

const pickValue = (obj, ...keys) => {
  for (const key of keys) {
    if (obj[key] !== undefined && obj[key] !== null) return obj[key]
  }
  return undefined
}

const loadIterations = async () => {
  loading.value = true
  try {
    const url = currentProject.value
      ? `/api/v1/iterations?project_id=${currentProject.value.id}`
      : '/api/v1/iterations'
    const response = await fetch(url)
    if (!response.ok) throw new Error(`HTTP ${response.status}`)
    const json = await response.json()
    const data = json.data || json
    const rawList = data.iterations || data.items || data
    const list = Array.isArray(rawList) ? rawList : []

    if (list.length === 0) {
      iterations.value = FALLBACK_ITERATIONS
    } else {
      iterations.value = list.map(item => ({
        id: pickValue(item, 'id', 'iteration_id'),
        name: pickValue(item, 'name', 'iteration_name', 'title') || '',
        status: pickValue(item, 'status', 'state') || '进行中',
        startDate: pickValue(item, 'start_date', 'startDate', 'start_time') || '',
        endDate: pickValue(item, 'end_date', 'endDate', 'end_time') || '',
        owner: pickValue(item, 'owner', 'assignee', 'responsible') || '',
        project: pickValue(item, 'project', 'project_name', 'projectName') || '',
        goal: pickValue(item, 'goal', 'target', 'objective') || ''
      }))
    }

    if (!selectedIteration.value && iterations.value.length > 0) {
      selectedIteration.value = iterations.value[0].id
      await loadIterationDetail(selectedIteration.value)
    }
  } catch (error) {
    console.error('加载迭代列表失败:', error)
    iterations.value = FALLBACK_ITERATIONS
    if (iterations.value.length > 0) {
      selectedIteration.value = iterations.value[0].id
      applyFallbackDetail(selectedIteration.value)
      nextTick(() => {
        renderRadarChart(FALLBACK_RADAR.current, FALLBACK_RADAR.previous)
        renderDefectChart(FALLBACK_DEFECT_DISTRIBUTION)
        renderCompareChart(FALLBACK_COMPARE)
      })
    }
  } finally {
    loading.value = false
  }
}

const loadIterationDetail = async (iterationId) => {
  try {
    const response = await fetch(`/api/v1/stats/iteration/${iterationId}`)
    if (!response.ok) throw new Error(`HTTP ${response.status}`)
    const json = await response.json()
    const detail = json.data || json

    const metrics = pickValue(detail, 'quality_metrics', 'metrics', 'qualityMetrics')
    if (metrics) {
      qualityMetrics.totalCases = pickValue(metrics, 'total_cases', 'totalCases', 'total') ?? 0
      qualityMetrics.passRate = pickValue(metrics, 'pass_rate', 'passRate') ?? 0
      qualityMetrics.defectCount = pickValue(metrics, 'defect_count', 'defectCount') ?? 0
      qualityMetrics.coverageRate = pickValue(metrics, 'coverage_rate', 'coverageRate') ?? 0
    }

    const rawDefects = pickValue(detail, 'defects', 'defect_list', 'defectList')
    if (Array.isArray(rawDefects)) {
      defectList.value = rawDefects.map(d => ({
        id: pickValue(d, 'id', 'bug_id', 'bugId') || '',
        title: pickValue(d, 'title', 'name', 'summary') || '',
        module: pickValue(d, 'module', 'module_name', 'moduleName') || '',
        severity: pickValue(d, 'severity', 'priority') || '一般',
        type: pickValue(d, 'type', 'defect_type', 'defectType') || '',
        status: pickValue(d, 'status', 'state') || '',
        foundDate: pickValue(d, 'found_date', 'foundDate', 'created_at', 'createdAt') || ''
      }))
    } else {
      defectList.value = []
    }

    const radar = pickValue(detail, 'radar', 'radar_chart', 'radarChart')
    if (radar) {
      const current = pickValue(radar, 'current', 'current_values', 'currentValues') || FALLBACK_RADAR.current
      const previous = pickValue(radar, 'previous', 'previous_values', 'previousValues') || FALLBACK_RADAR.previous
      nextTick(() => renderRadarChart(current, previous))
    } else {
      nextTick(() => renderRadarChart(FALLBACK_RADAR.current, FALLBACK_RADAR.previous))
    }

    const distribution = pickValue(detail, 'defect_distribution', 'defectDistribution', 'defect_chart', 'defectChart')
    if (Array.isArray(distribution) && distribution.length > 0) {
      nextTick(() => renderDefectChart(distribution))
    } else {
      nextTick(() => renderDefectChart(FALLBACK_DEFECT_DISTRIBUTION))
    }

    const compare = pickValue(detail, 'compare', 'comparison', 'compare_chart', 'compareChart')
    if (compare) {
      nextTick(() => renderCompareChart(compare))
    } else {
      nextTick(() => renderCompareChart(FALLBACK_COMPARE))
    }
  } catch (error) {
    console.error('加载迭代详情失败:', error)
    applyFallbackDetail(iterationId)
    nextTick(() => {
      renderRadarChart(FALLBACK_RADAR.current, FALLBACK_RADAR.previous)
      renderDefectChart(FALLBACK_DEFECT_DISTRIBUTION)
      renderCompareChart(FALLBACK_COMPARE)
    })
  }
}

const applyFallbackDetail = (iterationId) => {
  const data = FALLBACK_METRICS[iterationId] || FALLBACK_METRICS['iter_2026_sprint12']
  qualityMetrics.totalCases = data.totalCases
  qualityMetrics.passRate = data.passRate
  qualityMetrics.defectCount = data.defectCount
  qualityMetrics.coverageRate = data.coverageRate
  defectList.value = FALLBACK_DEFECTS
}

const renderRadarChart = (currentData, previousData) => {
  if (!radarChartRef.value) return
  if (!radarChart) {
    radarChart = echarts.init(radarChartRef.value)
  }
  radarChart.setOption({
    tooltip: {},
    radar: {
      indicator: [
        { name: '用例覆盖率', max: 100 },
        { name: '通过率', max: 100 },
        { name: '缺陷修复率', max: 100 },
        { name: '自动化率', max: 100 },
        { name: '执行效率', max: 100 },
        { name: '稳定性', max: 100 }
      ],
      shape: 'polygon',
      splitNumber: 5,
      axisName: { color: '#6b7280', fontSize: 12 },
      splitArea: { areaStyle: { color: ['rgba(99, 102, 241, 0.02)', 'rgba(99, 102, 241, 0.05)'] } },
      axisLine: { lineStyle: { color: '#e5e7eb' } },
      splitLine: { lineStyle: { color: '#e5e7eb' } }
    },
    series: [{
      type: 'radar',
      data: [
        {
          value: currentData,
          name: '当前迭代',
          areaStyle: { color: 'rgba(99, 102, 241, 0.3)' },
          lineStyle: { color: '#6366f1', width: 2 },
          itemStyle: { color: '#6366f1' }
        },
        {
          value: previousData,
          name: '上一迭代',
          areaStyle: { color: 'rgba(139, 92, 246, 0.2)' },
          lineStyle: { color: '#8b5cf6', width: 2, type: 'dashed' },
          itemStyle: { color: '#8b5cf6' }
        }
      ]
    }],
    legend: { bottom: 0, textStyle: { color: '#6b7280' } }
  })
}

const renderDefectChart = (distributionData) => {
  if (!defectChartRef.value) return
  if (!defectChart) {
    defectChart = echarts.init(defectChartRef.value)
  }
  defectChart.setOption({
    tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
    legend: { orient: 'vertical', right: '5%', top: 'center', textStyle: { color: '#6b7280' } },
    series: [{
      name: '缺陷分布',
      type: 'pie',
      radius: ['40%', '65%'],
      center: ['38%', '50%'],
      roseType: 'area',
      itemStyle: { borderRadius: 6, borderColor: '#fff', borderWidth: 2 },
      label: { show: false },
      data: distributionData
    }]
  })
}

const renderCompareChart = (compareData) => {
  if (!compareChartRef.value) return
  if (!compareChart) {
    compareChart = echarts.init(compareChartRef.value)
  }
  const categories = compareData.iterations || compareData.categories || []
  const totalCases = compareData.totalCases || compareData.total_cases || []
  const defectCounts = compareData.defectCounts || compareData.defect_counts || []
  const passRates = compareData.passRates || compareData.pass_rates || []

  compareChart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    legend: { top: 0, textStyle: { color: '#6b7280' } },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: { type: 'category', data: categories, axisLabel: { color: '#6b7280' } },
    yAxis: [
      { type: 'value', name: '用例数/缺陷数', axisLabel: { color: '#6b7280' } },
      { type: 'value', name: '通过率(%)', min: 80, max: 100, axisLabel: { formatter: '{value}%', color: '#6b7280' } }
    ],
    series: [
      {
        name: '总用例数',
        type: 'bar',
        data: totalCases,
        barWidth: '20%',
        itemStyle: { color: '#6366f1', borderRadius: [4, 4, 0, 0] }
      },
      {
        name: '缺陷数',
        type: 'bar',
        data: defectCounts,
        barWidth: '20%',
        itemStyle: { color: '#f59e0b', borderRadius: [4, 4, 0, 0] }
      },
      {
        name: '通过率',
        type: 'line',
        yAxisIndex: 1,
        data: passRates,
        smooth: true,
        lineStyle: { color: '#10b981', width: 3 },
        itemStyle: { color: '#10b981' },
        symbol: 'circle',
        symbolSize: 10
      }
    ]
  })
}

const handleIterationChange = async () => {
  const iter = currentIteration.value
  if (!iter) return
  await loadIterationDetail(iter.id)
  ElMessage.success(`已切换至 ${iter.name}`)
}

const handleResize = () => {
  radarChart?.resize()
  defectChart?.resize()
  compareChart?.resize()
}

const handleExport = () => {
  const wsData = defectList.value.map(item => ({
    '缺陷编号': item.id,
    '缺陷标题': item.title,
    '模块': item.module,
    '严重程度': item.severity,
    '缺陷类型': item.type,
    '状态': item.status,
    '发现日期': item.foundDate
  }))
  const ws = XLSX.utils.json_to_sheet(wsData)
  ws['!cols'] = [{ wch: 12 }, { wch: 35 }, { wch: 18 }, { wch: 12 }, { wch: 12 }, { wch: 10 }, { wch: 12 }]
  const wb = XLSX.utils.book_new()
  XLSX.utils.book_append_sheet(wb, ws, '迭代缺陷')

  const metricsData = [{
    '迭代': currentIteration.value?.name || '',
    '总用例数': qualityMetrics.totalCases,
    '通过率(%)': qualityMetrics.passRate,
    '缺陷数': qualityMetrics.defectCount,
    '覆盖率(%)': qualityMetrics.coverageRate
  }]
  const ws2 = XLSX.utils.json_to_sheet(metricsData)
  XLSX.utils.book_append_sheet(wb, ws2, '质量指标')

  XLSX.writeFile(wb, `迭代质量分析_${selectedIteration.value}_${new Date().toISOString().slice(0, 10)}.xlsx`)
  ElMessage.success('导出Excel成功')
}

onMounted(async () => {
  nextTick(() => {
    renderRadarChart(FALLBACK_RADAR.current, FALLBACK_RADAR.previous)
    renderDefectChart(FALLBACK_DEFECT_DISTRIBUTION)
    renderCompareChart(FALLBACK_COMPARE)
  })
  window.addEventListener('resize', handleResize)
  await loadIterations()
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  radarChart?.dispose()
  defectChart?.dispose()
  compareChart?.dispose()
})
</script>

<style scoped>
.iteration-analysis {
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

.filter-row {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.filter-label {
  font-size: 14px;
  color: #374151;
  font-weight: 500;
}

.info-card {
  margin-bottom: 20px;
  border-radius: 12px;
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.04), rgba(139, 92, 246, 0.04));
  border: 1px solid rgba(99, 102, 241, 0.1);
}

.info-row {
  display: flex;
  flex-wrap: wrap;
  gap: 24px;
}

.info-item {
  display: flex;
  align-items: center;
}

.info-label {
  font-size: 13px;
  color: #6b7280;
  margin-right: 4px;
}

.info-value {
  font-size: 14px;
  color: #1f2937;
  font-weight: 600;
}

.metrics-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.metric-card {
  border-radius: 12px;
  transition: box-shadow 0.3s;
}

.metric-card:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
}

.metric-content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.metric-icon {
  width: 44px;
  height: 44px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.metric-info {
  flex: 1;
}

.metric-value {
  font-size: 24px;
  font-weight: 700;
  color: #1f2937;
}

.metric-success {
  color: #10b981;
}

.metric-danger {
  color: #ef4444;
}

.metric-info-value {
  color: #06b6d4;
}

.metric-title {
  font-size: 13px;
  color: #6b7280;
}

.charts-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  margin-bottom: 24px;
}

@media (max-width: 900px) {
  .charts-row {
    grid-template-columns: 1fr;
  }
}

.chart-card {
  min-height: 340px;
}

.chart-card-full {
  min-height: 380px;
}

.chart-container {
  width: 100%;
  height: 280px;
}

.chart-container-large {
  width: 100%;
  height: 320px;
}

.card-title {
  font-size: 16px;
  font-weight: 600;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.card-total {
  font-size: 13px;
  color: #6b7280;
}
</style>