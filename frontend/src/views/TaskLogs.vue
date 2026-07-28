<template>
  <div class="task-logs">
    <div class="page-header">
      <h2>任务日志</h2>
      <p class="page-desc">查看自动化测试任务执行日志</p>
    </div>

    <el-card>
      <template #header>
        <div class="card-header">
          <div class="filter-bar">
            <el-select v-model="filterTaskName" placeholder="任务名称" size="small" class="filter-select" clearable filterable>
              <el-option
                v-for="name in taskNameOptions"
                :key="name"
                :label="name"
                :value="name"
              />
            </el-select>
            <el-select v-model="filterStatus" placeholder="执行状态" size="small" class="filter-select" clearable>
              <el-option label="成功" value="success" />
              <el-option label="失败" value="failed" />
              <el-option label="执行中" value="running" />
            </el-select>
            <el-date-picker
              v-model="filterDateRange"
              type="daterange"
              range-separator="至"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
              size="small"
              class="date-picker"
            />
            <el-button size="small" type="primary" @click="handleSearch">
              <el-icon><component :is="icons.Search" /></el-icon>
              查询
            </el-button>
            <el-button size="small" @click="handleReset">重置</el-button>
          </div>
          <div class="header-actions">
            <el-switch
              v-model="autoRefresh"
              active-text="自动刷新"
              inactive-text=""
              @change="handleAutoRefreshChange"
            />
            <el-select v-model="refreshInterval" size="small" class="refresh-select" :disabled="!autoRefresh">
              <el-option label="每5秒" :value="5" />
              <el-option label="每10秒" :value="10" />
              <el-option label="每30秒" :value="30" />
              <el-option label="每60秒" :value="60" />
            </el-select>
            <el-button size="small" @click="handleRefresh" :disabled="autoRefresh">
              <el-icon><component :is="icons.Refresh" /></el-icon>
              刷新
            </el-button>
            <el-button size="small" type="success" @click="handleExport">
              <el-icon><component :is="icons.Download" /></el-icon>
              导出日志
            </el-button>
          </div>
        </div>
      </template>

      <el-table :data="filteredLogs" stripe border v-loading="loading" @row-click="handleViewDetail">
        <el-table-column prop="id" label="日志ID" width="80" />
        <el-table-column prop="taskName" label="任务名称" min-width="150" show-overflow-tooltip />
        <el-table-column prop="taskType" label="任务类型" width="100">
          <template #default="scope">
            <el-tag :type="scope.row.taskType === 'API' ? 'primary' : 'success'" size="small">
              {{ scope.row.taskType === 'API' ? '接口测试' : 'UI测试' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="执行状态" width="100">
          <template #default="scope">
            <el-tag
              :type="getStatusTagType(scope.row.status)"
              size="small"
            >
              {{ getStatusLabel(scope.row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="totalCases" label="总数" width="70" />
        <el-table-column prop="passedCases" label="通过" width="70">
          <template #default="scope">
            <span class="pass-text">{{ scope.row.passedCases }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="failedCases" label="失败" width="70">
          <template #default="scope">
            <span class="fail-text">{{ scope.row.failedCases }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="duration" label="耗时" width="90" />
        <el-table-column prop="startedAt" label="开始时间" width="160">
          <template #default="scope">
            {{ formatDate(scope.row.startedAt) }}
          </template>
        </el-table-column>
        <el-table-column prop="environment" label="环境" width="100">
          <template #default="scope">
            <el-tag size="small" type="info">{{ scope.row.environment }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="160" class-name="action-cell" fixed="right">
          <template #default="scope">
            <div class="action-btns">
              <el-button size="small" type="primary" @click.stop="handleViewDetail(scope.row)">
                详情
              </el-button>
              <el-button size="small" @click.stop="handleExportSingle(scope.row)">
                导出
              </el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-wrapper">
        <el-pagination
          layout="total, sizes, prev, pager, next, jumper"
          :total="filteredLogs.length"
          :page-size="pagination.pageSize"
          v-model:current-page="pagination.currentPage"
          v-model:page-size="pagination.pageSize"
          :page-sizes="[10, 20, 50, 100]"
        />
      </div>
    </el-card>

    <el-dialog
      v-model="detailDialogVisible"
      title="日志详情"
      width="780px"
      top="5vh"
    >
      <div v-if="currentLog" class="log-detail">
        <div class="detail-summary">
          <div class="summary-item">
            <div class="summary-value">{{ currentLog.totalCases }}</div>
            <div class="summary-label">总用例</div>
          </div>
          <div class="summary-item pass">
            <div class="summary-value">{{ currentLog.passedCases }}</div>
            <div class="summary-label">通过</div>
          </div>
          <div class="summary-item fail">
            <div class="summary-value">{{ currentLog.failedCases }}</div>
            <div class="summary-label">失败</div>
          </div>
          <div class="summary-item">
            <div class="summary-value">{{ currentLog.duration }}</div>
            <div class="summary-label">耗时</div>
          </div>
        </div>

        <el-descriptions :column="3" border class="info-desc">
          <el-descriptions-item label="日志ID">{{ currentLog.id }}</el-descriptions-item>
          <el-descriptions-item label="任务名称">{{ currentLog.taskName }}</el-descriptions-item>
          <el-descriptions-item label="任务类型">
            {{ currentLog.taskType === 'API' ? '接口测试' : 'UI测试' }}
          </el-descriptions-item>
          <el-descriptions-item label="执行状态">
            <el-tag :type="getStatusTagType(currentLog.status)" size="small">
              {{ getStatusLabel(currentLog.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="执行环境">{{ currentLog.environment }}</el-descriptions-item>
          <el-descriptions-item label="触发方式">{{ currentLog.triggerType }}</el-descriptions-item>
          <el-descriptions-item label="开始时间">{{ formatDate(currentLog.startedAt) }}</el-descriptions-item>
          <el-descriptions-item label="结束时间">{{ formatDate(currentLog.finishedAt) }}</el-descriptions-item>
          <el-descriptions-item label="执行人">{{ currentLog.executor }}</el-descriptions-item>
        </el-descriptions>

        <el-divider content-position="left">执行步骤</el-divider>

        <el-timeline>
          <el-timeline-item
            v-for="(step, index) in currentLog.steps"
            :key="index"
            :timestamp="step.time"
            :color="step.status === 'failed' ? '#f56c6c' : step.status === 'running' ? '#e6a23c' : '#67c23a'"
          >
            <div class="step-item" :class="{ 'step-failed': step.status === 'failed' }">
              <div class="step-header">
                <span class="step-name">{{ step.name }}</span>
                <el-tag
                  :type="step.status === 'failed' ? 'danger' : step.status === 'running' ? 'warning' : 'success'"
                  size="small"
                >
                  {{ step.status === 'failed' ? '失败' : step.status === 'running' ? '执行中' : '通过' }}
                </el-tag>
                <span class="step-duration">{{ step.duration }}</span>
              </div>
              <div class="step-message" v-if="step.message">{{ step.message }}</div>
              <div class="step-screenshot" v-if="step.screenshot">
                <el-image
                  :src="step.screenshot"
                  :preview-src-list="[step.screenshot]"
                  fit="cover"
                  class="screenshot-thumb"
                />
              </div>
            </div>
          </el-timeline-item>
        </el-timeline>
      </div>
      <template #footer>
        <el-button @click="detailDialogVisible = false">关闭</el-button>
        <el-button type="success" @click="handleExportSingle(currentLog)">
          <el-icon><component :is="icons.Download" /></el-icon>
          导出此日志
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import * as icons from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const loading = ref(false)
const autoRefresh = ref(false)
const refreshInterval = ref(10)
const searchKeyword = ref('')

const filterTaskName = ref('')
const filterStatus = ref('')
const filterDateRange = ref([])

const detailDialogVisible = ref(false)
const currentLog = ref(null)

const pagination = reactive({
  currentPage: 1,
  pageSize: 10
})

let refreshTimer = null

const logs = ref([
  {
    id: 'LOG001',
    taskName: '每日全量回归测试',
    taskType: 'API',
    status: 'success',
    totalCases: 48,
    passedCases: 47,
    failedCases: 1,
    duration: '25m 30s',
    startedAt: '2026-07-23 02:00:00',
    finishedAt: '2026-07-23 02:25:30',
    environment: '测试环境',
    triggerType: '定时触发',
    executor: '系统',
    steps: [
      { name: '用户登录模块', status: 'passed', duration: '3m 20s', time: '02:03:20', message: '' },
      { name: '订单管理模块', status: 'passed', duration: '5m 10s', time: '02:08:30', message: '' },
      { name: '商品管理模块', status: 'failed', duration: '4m 50s', time: '02:13:20', message: '商品列表接口返回500错误', screenshot: 'https://via.placeholder.com/600x300?text=Error+Screenshot' },
      { name: '支付结算模块', status: 'passed', duration: '6m 00s', time: '02:19:20', message: '' },
      { name: '数据报表模块', status: 'passed', duration: '6m 10s', time: '02:25:30', message: '' }
    ]
  },
  {
    id: 'LOG002',
    taskName: '工作日接口冒烟测试',
    taskType: 'API',
    status: 'success',
    totalCases: 15,
    passedCases: 15,
    failedCases: 0,
    duration: '8m 15s',
    startedAt: '2026-07-23 09:00:00',
    finishedAt: '2026-07-23 09:08:15',
    environment: '测试环境',
    triggerType: '定时触发',
    executor: '系统',
    steps: [
      { name: '登录接口验证', status: 'passed', duration: '1m 00s', time: '09:01:00', message: '' },
      { name: '核心业务接口', status: 'passed', duration: '4m 30s', time: '09:05:30', message: '' },
      { name: '健康检查接口', status: 'passed', duration: '2m 45s', time: '09:08:15', message: '' }
    ]
  },
  {
    id: 'LOG003',
    taskName: 'GitLab MR触发测试',
    taskType: 'API',
    status: 'failed',
    totalCases: 12,
    passedCases: 8,
    failedCases: 4,
    duration: '12m 00s',
    startedAt: '2026-07-23 10:30:00',
    finishedAt: '2026-07-23 10:42:00',
    environment: '预发环境',
    triggerType: 'CI触发',
    executor: 'GitLab CI',
    steps: [
      { name: 'API-用户服务', status: 'passed', duration: '2m 00s', time: '10:32:00', message: '' },
      { name: 'API-订单服务', status: 'failed', duration: '3m 00s', time: '10:35:00', message: '订单创建接口超时(>5s)' },
      { name: 'API-支付服务', status: 'failed', duration: '3m 00s', time: '10:38:00', message: '支付回调验证失败' },
      { name: 'API-通知服务', status: 'passed', duration: '2m 00s', time: '10:40:00', message: '' },
      { name: 'API-报表服务', status: 'failed', duration: '2m 00s', time: '10:42:00', message: '报表数据不准确' }
    ]
  },
  {
    id: 'LOG004',
    taskName: 'UI自动化回归测试',
    taskType: 'UI',
    status: 'success',
    totalCases: 25,
    passedCases: 23,
    failedCases: 2,
    duration: '18m 45s',
    startedAt: '2026-07-23 11:00:00',
    finishedAt: '2026-07-23 11:18:45',
    environment: '测试环境',
    triggerType: '手动触发',
    executor: '张三',
    steps: [
      { name: 'UI-登录页面', status: 'passed', duration: '2m 00s', time: '11:02:00', message: '' },
      { name: 'UI-首页导航', status: 'passed', duration: '3m 00s', time: '11:05:00', message: '' },
      { name: 'UI-商品详情页', status: 'failed', duration: '4m 00s', time: '11:09:00', message: '商品图片加载异常', screenshot: 'https://via.placeholder.com/600x300?text=UI+Error' },
      { name: 'UI-购物车功能', status: 'passed', duration: '3m 30s', time: '11:12:30', message: '' },
      { name: 'UI-结算流程', status: 'failed', duration: '3m 15s', time: '11:15:45', message: '结算按钮无响应', screenshot: 'https://via.placeholder.com/600x300?text=UI+Error+2' },
      { name: 'UI-订单详情页', status: 'passed', duration: '2m 30s', time: '11:18:15', message: '' }
    ]
  },
  {
    id: 'LOG005',
    taskName: '主分支自动回归测试',
    taskType: 'API',
    status: 'running',
    totalCases: 100,
    passedCases: 45,
    failedCases: 2,
    duration: '执行中',
    startedAt: '2026-07-23 14:00:00',
    finishedAt: '',
    environment: '生产环境',
    triggerType: 'CI触发',
    executor: 'Jenkins',
    steps: [
      { name: 'API-基础服务', status: 'passed', duration: '5m 00s', time: '14:05:00', message: '' },
      { name: 'API-用户模块', status: 'passed', duration: '6m 00s', time: '14:11:00', message: '' },
      { name: 'API-订单模块', status: 'failed', duration: '5m 30s', time: '14:16:30', message: '部分订单查询失败' },
      { name: 'API-商品模块', status: 'passed', duration: '4m 00s', time: '14:20:30', message: '' },
      { name: 'API-支付模块', status: 'running', duration: '执行中', time: '14:25:30', message: '正在执行支付接口测试...' }
    ]
  },
  {
    id: 'LOG006',
    taskName: '版本标签发布测试',
    taskType: 'API',
    status: 'success',
    totalCases: 35,
    passedCases: 35,
    failedCases: 0,
    duration: '15m 20s',
    startedAt: '2026-07-22 16:00:00',
    finishedAt: '2026-07-22 16:15:20',
    environment: '预发环境',
    triggerType: 'CI触发',
    executor: 'GitHub Actions',
    steps: [
      { name: 'API-冒烟测试', status: 'passed', duration: '3m 00s', time: '16:03:00', message: '' },
      { name: 'API-核心功能', status: 'passed', duration: '8m 00s', time: '16:11:00', message: '' },
      { name: 'API-回归测试', status: 'passed', duration: '4m 20s', time: '16:15:20', message: '' }
    ]
  },
  {
    id: 'LOG007',
    taskName: '每小时健康检查',
    taskType: 'API',
    status: 'failed',
    totalCases: 5,
    passedCases: 3,
    failedCases: 2,
    duration: '2m 30s',
    startedAt: '2026-07-23 14:00:00',
    finishedAt: '2026-07-23 14:02:30',
    environment: '生产环境',
    triggerType: '定时触发',
    executor: '系统',
    steps: [
      { name: '健康检查-网关', status: 'passed', duration: '10s', time: '14:00:10', message: '' },
      { name: '健康检查-用户服务', status: 'failed', duration: '20s', time: '14:00:30', message: '服务不可用' },
      { name: '健康检查-订单服务', status: 'passed', duration: '15s', time: '14:00:45', message: '' },
      { name: '健康检查-支付服务', status: 'failed', duration: '25s', time: '14:01:10', message: '连接超时' },
      { name: '健康检查-缓存服务', status: 'passed', duration: '10s', time: '14:01:20', message: '' }
    ]
  },
  {
    id: 'LOG008',
    taskName: '周末数据清理测试',
    taskType: 'API',
    status: 'success',
    totalCases: 8,
    passedCases: 8,
    failedCases: 0,
    duration: '6m 40s',
    startedAt: '2026-07-20 03:00:00',
    finishedAt: '2026-07-20 03:06:40',
    environment: '测试环境',
    triggerType: '定时触发',
    executor: '系统',
    steps: [
      { name: '数据清理-日志归档', status: 'passed', duration: '2m 00s', time: '03:02:00', message: '' },
      { name: '数据清理-临时文件', status: 'passed', duration: '2m 20s', time: '03:04:20', message: '' },
      { name: '数据清理-缓存清理', status: 'passed', duration: '2m 20s', time: '03:06:40', message: '' }
    ]
  }
])

const taskNameOptions = computed(() => {
  const names = [...new Set(logs.value.map(l => l.taskName))]
  return names
})

const filteredLogs = computed(() => {
  return logs.value.filter(log => {
    const matchTaskName = !filterTaskName.value || log.taskName === filterTaskName.value
    const matchStatus = !filterStatus.value || log.status === filterStatus.value
    let matchDate = true
    if (filterDateRange.value && filterDateRange.value.length === 2) {
      const [start, end] = filterDateRange.value
      const logDate = new Date(log.startedAt)
      if (start && end) {
        matchDate = logDate >= start && logDate <= end
      }
    }
    return matchTaskName && matchStatus && matchDate
  })
})

function getStatusTagType(status) {
  const types = { success: 'success', failed: 'danger', running: 'warning' }
  return types[status] || 'info'
}

function getStatusLabel(status) {
  const labels = { success: '成功', failed: '失败', running: '执行中' }
  return labels[status] || status
}

function formatDate(dateStr) {
  if (!dateStr) return '-'
  return dateStr
}

function handleSearch() {
  ElMessage.success('查询完成')
}

function handleReset() {
  filterTaskName.value = ''
  filterStatus.value = ''
  filterDateRange.value = []
  ElMessage.info('筛选条件已重置')
}

function handleRefresh() {
  loading.value = true
  setTimeout(() => {
    loading.value = false
    ElMessage.success('日志已刷新')
  }, 500)
}

function handleAutoRefreshChange(val) {
  if (val) {
    startAutoRefresh()
  } else {
    stopAutoRefresh()
  }
}

function startAutoRefresh() {
  stopAutoRefresh()
  refreshTimer = setInterval(() => {
    loading.value = true
    setTimeout(() => {
      loading.value = false
    }, 300)
  }, refreshInterval.value * 1000)
  ElMessage.success(`已开启自动刷新（每${refreshInterval.value}秒）`)
}

function stopAutoRefresh() {
  if (refreshTimer) {
    clearInterval(refreshTimer)
    refreshTimer = null
  }
}

function handleViewDetail(row) {
  currentLog.value = row
  detailDialogVisible.value = true
}

function handleExport() {
  ElMessage.success(`已导出 ${filteredLogs.value.length} 条日志为 Excel 文件`)
}

function handleExportSingle(row) {
  if (!row) return
  ElMessage.success(`日志 ${row.id} 已导出`)
}

onMounted(() => {
  loading.value = true
  setTimeout(() => {
    loading.value = false
  }, 300)
})

onUnmounted(() => {
  stopAutoRefresh()
})
</script>

<style scoped>
.task-logs {
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

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 12px;
}

.card-title {
  font-size: 16px;
  font-weight: 600;
}

.filter-bar {
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.filter-select {
  width: 160px;
}

.date-picker {
  width: 260px;
}

.refresh-select {
  width: 120px;
}

.pagination-wrapper {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}

.pass-text {
  color: #67c23a;
  font-weight: 600;
}

.fail-text {
  color: #f56c6c;
  font-weight: 600;
}

.log-detail {
  max-height: 70vh;
  overflow-y: auto;
}

.detail-summary {
  display: flex;
  justify-content: space-around;
  margin-bottom: 16px;
}

.summary-item {
  text-align: center;
  padding: 16px 24px;
  background: #f5f7fa;
  border-radius: 8px;
  min-width: 100px;
}

.summary-item.pass {
  background: #f0f9eb;
}

.summary-item.fail {
  background: #fef0f0;
}

.summary-value {
  font-size: 28px;
  font-weight: 600;
  color: #1f2937;
}

.summary-item.pass .summary-value {
  color: #67c23a;
}

.summary-item.fail .summary-value {
  color: #f56c6c;
}

.summary-label {
  font-size: 13px;
  color: #6b7280;
  margin-top: 4px;
}

.info-desc {
  margin-bottom: 16px;
}

.step-item {
  padding: 8px 12px;
  background: #f9fafb;
  border-radius: 6px;
  margin-bottom: 8px;
}

.step-item.step-failed {
  background: #fef2f2;
}

.step-header {
  display: flex;
  align-items: center;
  gap: 12px;
}

.step-name {
  font-weight: 600;
  color: #1f2937;
  flex: 1;
}

.step-duration {
  font-size: 12px;
  color: #909399;
}

.step-message {
  margin-top: 8px;
  font-size: 13px;
  color: #f56c6c;
}

.step-screenshot {
  margin-top: 8px;
}

.screenshot-thumb {
  width: 300px;
  height: 150px;
  border-radius: 6px;
  cursor: pointer;
}
</style>