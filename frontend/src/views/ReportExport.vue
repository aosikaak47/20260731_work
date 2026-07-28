<template>
  <div class="report-export">
    <div class="page-header">
      <h2>报表导出</h2>
      <p class="page-desc">导出测试报告和统计数据</p>
    </div>

    <div class="main-content">
      <el-card class="form-card">
        <template #header>
          <span class="card-title">报表配置</span>
        </template>

        <el-form :model="form" label-width="100px" class="export-form">
          <el-form-item label="报表类型">
            <el-select v-model="form.reportType" style="width: 100%">
              <el-option label="执行报告" value="execution" />
              <el-option label="质量统计报表" value="quality" />
              <el-option label="用例覆盖率报表" value="coverage" />
              <el-option label="失败用例汇总" value="failed" />
            </el-select>
          </el-form-item>
          <el-form-item label="时间范围">
            <el-date-picker
              v-model="form.dateRange"
              type="daterange"
              range-separator="至"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
              style="width: 100%"
            />
          </el-form-item>
          <el-form-item label="项目">
            <el-select v-model="form.project" placeholder="请选择项目" style="width: 100%" clearable>
              <el-option v-for="p in activeProjects" :key="p.id" :label="p.name" :value="String(p.id)" />
            </el-select>
          </el-form-item>
          <el-form-item label="迭代">
            <el-select v-model="form.iteration" placeholder="请选择迭代" style="width: 100%" clearable>
              <el-option label="Sprint 12" value="iter_12" />
              <el-option label="Sprint 11" value="iter_11" />
              <el-option label="Sprint 10" value="iter_10" />
              <el-option label="Sprint 9" value="iter_9" />
            </el-select>
          </el-form-item>
          <el-form-item label="导出格式">
            <el-select v-model="form.exportFormat" style="width: 100%">
              <el-option label="Excel (.xlsx)" value="xlsx" />
              <el-option label="PDF (打印)" value="pdf" />
              <el-option label="CSV" value="csv" />
            </el-select>
          </el-form-item>
          <el-form-item label="包含图表">
            <el-checkbox v-model="form.includeCharts" />
            <span class="checkbox-desc">在报表中嵌入统计图表</span>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="handleExport" style="width: 100%">
              <el-icon><component :is="icons.Download" /></el-icon>
              生成报表
            </el-button>
          </el-form-item>
          <el-form-item>
            <el-button @click="handlePreview" style="width: 100%">
              <el-icon><component :is="icons.View" /></el-icon>
              预览报表
            </el-button>
          </el-form-item>
        </el-form>
      </el-card>

      <el-card class="preview-card">
        <template #header>
          <div class="card-header">
            <span class="card-title">报表预览</span>
            <el-button v-if="previewVisible" size="small" @click="refreshPreview">
              <el-icon><component :is="icons.Refresh" /></el-icon>
              刷新
            </el-button>
          </div>
        </template>

        <div v-if="!previewVisible" class="empty-preview">
          <el-icon :size="56" class="empty-icon"><component :is="icons.Document" /></el-icon>
          <p>选择报表参数后点击"预览报表"查看效果</p>
        </div>

        <div v-else ref="previewContainer" class="preview-content" id="reportPreview">
          <div class="report-header">
            <h1>{{ reportTitle }}</h1>
            <p class="report-subtitle">生成时间：{{ currentTime }} | 项目：{{ projectLabel }}</p>
          </div>

          <div class="report-section">
            <h3>一、报告概要</h3>
            <div class="summary-grid">
              <div class="summary-item">
                <div class="summary-value">{{ reportData.totalCases }}</div>
                <div class="summary-label">总用例数</div>
              </div>
              <div class="summary-item success">
                <div class="summary-value">{{ reportData.passedCases }}</div>
                <div class="summary-label">通过用例</div>
              </div>
              <div class="summary-item danger">
                <div class="summary-value">{{ reportData.failedCases }}</div>
                <div class="summary-label">失败用例</div>
              </div>
              <div class="summary-item info">
                <div class="summary-value">{{ reportData.passRate }}%</div>
                <div class="summary-label">通过率</div>
              </div>
            </div>
          </div>

          <div class="report-section">
            <h3>二、趋势图表</h3>
            <div ref="previewTrendChartRef" class="preview-chart"></div>
          </div>

          <div class="report-section">
            <h3>三、{{ reportData.tableTitle }}</h3>
            <table class="report-table">
              <thead>
                <tr>
                  <th v-for="col in reportData.columns" :key="col">{{ col }}</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(row, idx) in reportData.tableData" :key="idx">
                  <td v-for="(cell, cIdx) in row" :key="cIdx">{{ cell }}</td>
                </tr>
              </tbody>
            </table>
          </div>

          <div class="report-section">
            <h3>四、统计图表</h3>
            <div ref="previewBarChartRef" class="preview-chart"></div>
          </div>

          <div class="report-footer">
            <p>本报告由自动化测试平台生成</p>
          </div>
        </div>
      </el-card>
    </div>

    <el-dialog v-model="previewDialogVisible" title="报表预览" width="900px" top="5vh" destroy-on-close>
      <div class="dialog-preview" ref="dialogPreviewContainer">
        <div class="report-header">
          <h1>{{ reportTitle }}</h1>
          <p class="report-subtitle">生成时间：{{ currentTime }} | 项目：{{ projectLabel }}</p>
        </div>
        <div class="report-section">
          <h3>一、报告概要</h3>
          <div class="summary-grid">
            <div class="summary-item">
              <div class="summary-value">{{ reportData.totalCases }}</div>
              <div class="summary-label">总用例数</div>
            </div>
            <div class="summary-item success">
              <div class="summary-value">{{ reportData.passedCases }}</div>
              <div class="summary-label">通过用例</div>
            </div>
            <div class="summary-item danger">
              <div class="summary-value">{{ reportData.failedCases }}</div>
              <div class="summary-label">失败用例</div>
            </div>
            <div class="summary-item info">
              <div class="summary-value">{{ reportData.passRate }}%</div>
              <div class="summary-label">通过率</div>
            </div>
          </div>
        </div>
        <div class="report-section">
          <h3>二、趋势图表</h3>
          <div ref="dialogTrendChartRef" class="preview-chart"></div>
        </div>
        <div class="report-section">
          <h3>三、{{ reportData.tableTitle }}</h3>
          <table class="report-table">
            <thead>
              <tr>
                <th v-for="col in reportData.columns" :key="col">{{ col }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(row, idx) in reportData.tableData" :key="idx">
                <td v-for="(cell, cIdx) in row" :key="cIdx">{{ cell }}</td>
              </tr>
            </tbody>
          </table>
        </div>
        <div class="report-section">
          <h3>四、统计图表</h3>
          <div ref="dialogBarChartRef" class="preview-chart"></div>
        </div>
      </div>
      <template #footer>
        <el-button @click="previewDialogVisible = false">关闭</el-button>
        <el-button type="primary" @click="handleExportFromDialog">导出此报表</el-button>
        <el-button type="success" @click="handlePrintPDF">
          <el-icon><component :is="icons.Printer" /></el-icon>
          打印为PDF
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, nextTick, onBeforeUnmount, onMounted } from 'vue'
import * as echarts from 'echarts'
import * as XLSX from 'xlsx'
import { ElMessage } from 'element-plus'
import * as icons from '@element-plus/icons-vue'
import { useProjects } from '../composables/useProjects'

const { projects, activeProjects, loadProjects } = useProjects()

const form = reactive({
  reportType: 'execution',
  dateRange: [],
  project: '',
  iteration: '',
  exportFormat: 'xlsx',
  includeCharts: true
})

const previewVisible = ref(false)
const previewDialogVisible = ref(false)

const previewTrendChartRef = ref(null)
const previewBarChartRef = ref(null)
const dialogTrendChartRef = ref(null)
const dialogBarChartRef = ref(null)
let previewTrendChart = null
let previewBarChart = null
let dialogTrendChart = null
let dialogBarChart = null

const reportData = ref({
  totalCases: 0,
  passedCases: 0,
  failedCases: 0,
  passRate: 0,
  tableTitle: '',
  columns: [],
  tableData: [],
  trendData: null,
  barData: null
})
const loadingReport = ref(false)

const currentTime = computed(() => {
  const now = new Date()
  return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')} ${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}`
})

const projectLabel = computed(() => {
  const project = projects.value.find(p => String(p.id) === String(form.project))
  return project ? project.name : '全部项目'
})

const reportTitle = computed(() => {
  const titles = {
    execution: '测试执行报告',
    quality: '质量统计报表',
    coverage: '用例覆盖率报表',
    failed: '失败用例汇总报告'
  }
  return titles[form.reportType] || '测试报告'
})

const loadReportData = async () => {
  loadingReport.value = true
  try {
    const params = new URLSearchParams({
      report_type: form.reportType
    })
    if (form.project) {
      params.append('project_id', form.project)
    }
    if (form.dateRange && form.dateRange.length === 2) {
      const startDate = form.dateRange[0] instanceof Date
        ? form.dateRange[0].toISOString().slice(0, 10)
        : form.dateRange[0]
      const endDate = form.dateRange[1] instanceof Date
        ? form.dateRange[1].toISOString().slice(0, 10)
        : form.dateRange[1]
      params.append('start_date', startDate)
      params.append('end_date', endDate)
    }
    if (form.iteration) {
      params.append('iteration', form.iteration)
    }

    const response = await fetch(`/api/v1/stats/report?${params}`)
    const json = await response.json()
    const data = json.data || json

    if (json.success !== false) {
      const report = data.report || data
      reportData.value = {
        totalCases: report.totalCases || 0,
        passedCases: report.passedCases || 0,
        failedCases: report.failedCases || 0,
        passRate: report.passRate || 0,
        tableTitle: report.tableTitle || '',
        columns: report.columns || [],
        tableData: report.tableData || [],
        trendData: report.trendData || null,
        barData: report.barData || null
      }
    } else {
      ElMessage.error(json.message || '加载报表数据失败')
    }
  } catch (error) {
    console.error('加载报表数据失败:', error)
    ElMessage.error('加载报表数据失败')
  } finally {
    loadingReport.value = false
  }
}

const initPreviewCharts = () => {
  nextTick(() => {
    if (!previewTrendChartRef.value) return
    if (previewTrendChart) previewTrendChart.dispose()
    previewTrendChart = echarts.init(previewTrendChartRef.value)

    let dates, values
    const trendData = reportData.value.trendData
    if (trendData && trendData.dates && trendData.values) {
      dates = trendData.dates
      values = trendData.values
    } else {
      dates = []
      values = []
      const now = new Date()
      for (let i = 13; i >= 0; i--) {
        const d = new Date(now)
        d.setDate(d.getDate() - i)
        dates.push(`${d.getMonth() + 1}/${d.getDate()}`)
        values.push(parseFloat((88 + Math.random() * 11).toFixed(1)))
      }
    }

    previewTrendChart.setOption({
      tooltip: { trigger: 'axis', formatter: '{b}<br/>通过率: {c}%' },
      grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
      xAxis: { type: 'category', data: dates, boundaryGap: true, axisLabel: { color: '#6b7280' } },
      yAxis: { type: 'value', min: 80, max: 100, axisLabel: { formatter: '{value}%', color: '#6b7280' } },
      series: [{
        name: '通过率', type: 'line', data: values, smooth: true,
        areaStyle: { color: 'rgba(99, 102, 241, 0.3)' },
        lineStyle: { color: '#6366f1', width: 2 },
        itemStyle: { color: '#6366f1' }
      }]
    })

    if (!previewBarChartRef.value) return
    if (previewBarChart) previewBarChart.dispose()
    previewBarChart = echarts.init(previewBarChartRef.value)

    let barCategories, barValues
    const barData = reportData.value.barData
    if (barData && barData.categories && barData.values) {
      barCategories = barData.categories
      barValues = barData.values
    } else {
      barCategories = ['AI用例', '用例管理', '接口', 'UI', '性能', '数据']
      barValues = [120, 80, 200, 150, 60, 45]
    }

    previewBarChart.setOption({
      tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
      grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
      xAxis: { type: 'category', data: barCategories },
      yAxis: { type: 'value', axisLabel: '{value}' },
      series: [{
        name: '数量', type: 'bar',
        data: barValues,
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#8b5cf6' }, { offset: 1, color: '#6366f1' }
          ]),
          borderRadius: [4, 4, 0, 0]
        }
      }]
    })
  })
}

const initDialogCharts = () => {
  nextTick(() => {
    if (!dialogTrendChartRef.value) return
    if (dialogTrendChart) dialogTrendChart.dispose()
    dialogTrendChart = echarts.init(dialogTrendChartRef.value)

    let dates, values
    const trendData = reportData.value.trendData
    if (trendData && trendData.dates && trendData.values) {
      dates = trendData.dates
      values = trendData.values
    } else {
      dates = []
      values = []
      const now = new Date()
      for (let i = 13; i >= 0; i--) {
        const d = new Date(now)
        d.setDate(d.getDate() - i)
        dates.push(`${d.getMonth() + 1}/${d.getDate()}`)
        values.push(parseFloat((88 + Math.random() * 11).toFixed(1)))
      }
    }

    dialogTrendChart.setOption({
      tooltip: { trigger: 'axis', formatter: '{b}<br/>通过率: {c}%' },
      grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
      xAxis: { type: 'category', data: dates, boundaryGap: true },
      yAxis: { type: 'value', min: 80, max: 100 },
      series: [{
        name: '通过率', type: 'line', data: values, smooth: true,
        areaStyle: { color: 'rgba(99, 102, 241, 0.3)' },
        lineStyle: { color: '#6366f1', width: 2 },
        itemStyle: { color: '#6366f1' }
      }]
    })

    if (!dialogBarChartRef.value) return
    if (dialogBarChart) dialogBarChart.dispose()
    dialogBarChart = echarts.init(dialogBarChartRef.value)

    let barCategories, barValues
    const barData = reportData.value.barData
    if (barData && barData.categories && barData.values) {
      barCategories = barData.categories
      barValues = barData.values
    } else {
      barCategories = ['AI用例', '用例管理', '接口', 'UI', '性能', '数据']
      barValues = [120, 80, 200, 150, 60, 45]
    }

    dialogBarChart.setOption({
      tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
      grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
      xAxis: { type: 'category', data: barCategories },
      yAxis: { type: 'value' },
      series: [{
        name: '数量', type: 'bar',
        data: barValues,
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#8b5cf6' }, { offset: 1, color: '#6366f1' }
          ]),
          borderRadius: [4, 4, 0, 0]
        }
      }]
    })
  })
}

const generateReportHTML = () => {
  const trendImg = previewTrendChart ? previewTrendChart.getDataURL({ type: 'png', pixelRatio: 2, backgroundColor: '#fff' }) : ''
  const barImg = previewBarChart ? previewBarChart.getDataURL({ type: 'png', pixelRatio: 2, backgroundColor: '#fff' }) : ''

  const tableRows = reportData.value.tableData.map(row =>
    '<tr>' + row.map(cell => `<td>${cell}</td>`).join('') + '</tr>'
  ).join('')
  const tableHeaders = reportData.value.columns.map(c => `<th>${c}</th>`).join('')

  return `
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
      <meta charset="UTF-8">
      <title>${reportTitle.value}</title>
      <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif; padding: 40px; background: #fff; color: #1f2937; }
        h1 { text-align: center; color: #1f2937; margin-bottom: 8px; }
        .subtitle { text-align: center; color: #6b7280; margin-bottom: 40px; font-size: 14px; }
        h3 { color: #374151; border-left: 4px solid #6366f1; padding-left: 12px; margin-top: 32px; }
        .summary-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin: 20px 0; }
        .summary-item { text-align: center; padding: 16px; background: #f9fafb; border-radius: 8px; }
        .summary-value { font-size: 28px; font-weight: 700; color: #1f2937; }
        .summary-item.success .summary-value { color: #10b981; }
        .summary-item.danger .summary-value { color: #ef4444; }
        .summary-item.info .summary-value { color: #6366f1; }
        .summary-label { font-size: 13px; color: #6b7280; margin-top: 4px; }
        table { width: 100%; border-collapse: collapse; margin: 16px 0; }
        th { background: #f3f4f6; padding: 10px; text-align: left; font-size: 13px; color: #374151; border: 1px solid #e5e7eb; }
        td { padding: 10px; border: 1px solid #e5e7eb; font-size: 13px; color: #374151; }
        tr:nth-child(even) { background: #f9fafb; }
        .chart-img { width: 100%; max-width: 700px; margin: 16px auto; display: block; }
        .footer { text-align: center; color: #9ca3af; font-size: 12px; margin-top: 40px; padding-top: 20px; border-top: 1px solid #e5e7eb; }
        @media print { body { padding: 20px; } }
      </style>
    </head>
    <body>
      <h1>${reportTitle.value}</h1>
      <p class="subtitle">生成时间：${currentTime.value} | 项目：${projectLabel.value}</p>

      <h3>一、报告概要</h3>
      <div class="summary-grid">
        <div class="summary-item"><div class="summary-value">${reportData.value.totalCases}</div><div class="summary-label">总用例数</div></div>
        <div class="summary-item success"><div class="summary-value">${reportData.value.passedCases}</div><div class="summary-label">通过用例</div></div>
        <div class="summary-item danger"><div class="summary-value">${reportData.value.failedCases}</div><div class="summary-label">失败用例</div></div>
        <div class="summary-item info"><div class="summary-value">${reportData.value.passRate}%</div><div class="summary-label">通过率</div></div>
      </div>

      <h3>二、趋势图表</h3>
      ${trendImg ? `<img class="chart-img" src="${trendImg}" alt="趋势图"/>` : '<p>暂无数据</p>'}

      <h3>三、${reportData.value.tableTitle}</h3>
      <table>
        <thead><tr>${tableHeaders}</tr></thead>
        <tbody>${tableRows}</tbody>
      </table>

      <h3>四、统计图表</h3>
      ${barImg ? `<img class="chart-img" src="${barImg}" alt="统计图"/>` : '<p>暂无数据</p>'}

      <div class="footer">本报告由自动化测试平台生成</div>
    </body>
    </html>
  `
}

const handleExport = async () => {
  await loadReportData()
  if (form.exportFormat === 'xlsx') {
    handleExcelExport()
  } else if (form.exportFormat === 'csv') {
    handleCSVExport()
  } else if (form.exportFormat === 'pdf') {
    handlePrintPDF()
  }
}

const handleExcelExport = () => {
  const wb = XLSX.utils.book_new()

  const summaryData = [{
    '报表标题': reportTitle.value,
    '生成时间': currentTime.value,
    '项目': projectLabel.value,
    '总用例数': reportData.value.totalCases,
    '通过用例': reportData.value.passedCases,
    '失败用例': reportData.value.failedCases,
    '通过率(%)': reportData.value.passRate
  }]
  const wsSummary = XLSX.utils.json_to_sheet(summaryData)
  wsSummary['!cols'] = [{ wch: 15 }, { wch: 20 }, { wch: 18 }, { wch: 10 }, { wch: 10 }, { wch: 10 }, { wch: 10 }]
  XLSX.utils.book_append_sheet(wb, wsSummary, '报告概要')

  const detailData = reportData.value.tableData.map(row => {
    const obj = {}
    reportData.value.columns.forEach((col, idx) => {
      obj[col] = row[idx]
    })
    return obj
  })
  const wsDetail = XLSX.utils.json_to_sheet(detailData)
  const colWidths = reportData.value.columns.map(() => ({ wch: 15 }))
  wsDetail['!cols'] = colWidths
  XLSX.utils.book_append_sheet(wb, wsDetail, reportData.value.tableTitle.slice(0, 30))

  const filename = `${reportTitle.value}_${new Date().toISOString().slice(0, 10)}.xlsx`
  XLSX.writeFile(wb, filename)
  ElMessage.success('Excel导出成功')
}

const handleCSVExport = () => {
  const detailData = reportData.value.tableData.map(row => {
    const obj = {}
    reportData.value.columns.forEach((col, idx) => {
      obj[col] = row[idx]
    })
    return obj
  })
  const ws = XLSX.utils.json_to_sheet(detailData)
  const csv = XLSX.utils.sheet_to_csv(ws)
  const blob = new Blob(['\uFEFF' + csv], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')
  link.href = URL.createObjectURL(blob)
  link.download = `${reportTitle.value}_${new Date().toISOString().slice(0, 10)}.csv`
  link.click()
  ElMessage.success('CSV导出成功')
}

const handlePrintPDF = () => {
  const html = generateReportHTML()
  const printWindow = window.open('', '_blank')
  if (!printWindow) {
    ElMessage.error('无法打开打印窗口，请允许浏览器弹窗')
    return
  }
  printWindow.document.write(html)
  printWindow.document.close()
  printWindow.onload = () => {
    setTimeout(() => {
      printWindow.print()
    }, 300)
  }
  ElMessage.info('请在打印对话框中选择"另存为PDF"')
}

const handlePreview = async () => {
  previewVisible.value = true
  previewDialogVisible.value = true
  await loadReportData()
  nextTick(() => {
    initDialogCharts()
  })
  initPreviewCharts()
  ElMessage.success('预览已生成')
}

const refreshPreview = async () => {
  await loadReportData()
  initPreviewCharts()
  ElMessage.success('预览已刷新')
}

const handleExportFromDialog = () => {
  previewDialogVisible.value = false
  handleExcelExport()
}

const handleResize = () => {
  previewTrendChart?.resize()
  previewBarChart?.resize()
  dialogTrendChart?.resize()
  dialogBarChart?.resize()
}

window.addEventListener('resize', handleResize)

onMounted(async () => {
  await loadProjects()
  await loadReportData()
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  previewTrendChart?.dispose()
  previewBarChart?.dispose()
  dialogTrendChart?.dispose()
  dialogBarChart?.dispose()
})
</script>

<style scoped>
.report-export {
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

.main-content {
  display: grid;
  grid-template-columns: 380px 1fr;
  gap: 20px;
  align-items: start;
}

@media (max-width: 1100px) {
  .main-content {
    grid-template-columns: 1fr;
  }
}

.form-card {
  position: sticky;
  top: 20px;
}

.export-form {
  padding-top: 8px;
}

.checkbox-desc {
  margin-left: 8px;
  font-size: 13px;
  color: #6b7280;
}

.preview-card {
  min-height: 500px;
}

.empty-preview {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 400px;
  color: #9ca3af;
  gap: 16px;
}

.empty-icon {
  color: #d1d5db;
}

.empty-preview p {
  font-size: 14px;
}

.preview-content {
  max-height: 600px;
  overflow-y: auto;
  padding: 16px;
}

.report-header {
  text-align: center;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 2px solid #f3f4f6;
}

.report-header h1 {
  font-size: 22px;
  font-weight: 700;
  color: #1f2937;
  margin-bottom: 8px;
}

.report-subtitle {
  font-size: 13px;
  color: #6b7280;
}

.report-section {
  margin-bottom: 24px;
}

.report-section h3 {
  font-size: 16px;
  font-weight: 600;
  color: #374151;
  margin-bottom: 16px;
  padding-left: 12px;
  border-left: 4px solid #6366f1;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
}

.summary-item {
  text-align: center;
  padding: 16px 8px;
  background: #f9fafb;
  border-radius: 10px;
}

.summary-value {
  font-size: 24px;
  font-weight: 700;
  color: #1f2937;
}

.summary-item.success .summary-value {
  color: #10b981;
}

.summary-item.danger .summary-value {
  color: #ef4444;
}

.summary-item.info .summary-value {
  color: #6366f1;
}

.summary-label {
  font-size: 12px;
  color: #6b7280;
  margin-top: 4px;
}

.preview-chart {
  width: 100%;
  height: 260px;
}

.report-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}

.report-table th {
  background: #f3f4f6;
  padding: 10px 12px;
  text-align: left;
  color: #374151;
  font-weight: 600;
  border: 1px solid #e5e7eb;
}

.report-table td {
  padding: 10px 12px;
  border: 1px solid #e5e7eb;
  color: #374151;
}

.report-table tr:nth-child(even) td {
  background: #f9fafb;
}

.report-footer {
  text-align: center;
  padding-top: 16px;
  border-top: 1px solid #e5e7eb;
  color: #9ca3af;
  font-size: 12px;
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

.dialog-preview {
  max-height: 65vh;
  overflow-y: auto;
  padding: 16px;
}
</style>