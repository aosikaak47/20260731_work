<template>
  <div class="scheduled-tasks">
    <div class="page-header">
      <h2>定时任务</h2>
      <p class="page-desc">配置和管理定时自动化测试任务</p>
    </div>

    <el-card>
      <template #header>
        <div class="card-header">
          <span class="card-title">任务列表</span>
          <div class="header-actions">
            <el-input
              v-model="searchKeyword"
              placeholder="搜索任务名称"
              :prefix-icon="icons.Search"
              size="small"
              class="search-input"
              clearable
            />
            <el-select v-model="filterStatus" placeholder="状态" size="small" class="filter-select" clearable>
              <el-option label="已启用" value="enabled" />
              <el-option label="已禁用" value="disabled" />
            </el-select>
            <el-button type="primary" @click="handleCreateTask">
              <el-icon><component :is="icons.Plus" /></el-icon>
              创建任务
            </el-button>
          </div>
        </div>
      </template>

      <el-table :data="filteredTasks" stripe border>
        <el-table-column prop="name" label="任务名称" min-width="160" show-overflow-tooltip />
        <el-table-column prop="cronExpression" label="Cron表达式" min-width="140">
          <template #default="scope">
            <el-tag type="info" size="small" class="cron-tag">{{ scope.row.cronExpression }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="nextRunTime" label="下次执行时间" min-width="150">
          <template #default="scope">
            {{ scope.row.nextRunTime }}
          </template>
        </el-table-column>
        <el-table-column prop="lastRunTime" label="上次执行时间" min-width="150">
          <template #default="scope">
            {{ scope.row.lastRunTime || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="lastResult" label="上次结果" width="100">
          <template #default="scope">
            <el-tag
              v-if="scope.row.lastResult"
              :type="scope.row.lastResult === 'success' ? 'success' : 'danger'"
              size="small"
            >
              {{ scope.row.lastResult === 'success' ? '成功' : '失败' }}
            </el-tag>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="scope">
            <el-switch
              v-model="scope.row.status"
              :active-value="'enabled'"
              :inactive-value="'disabled'"
              @change="handleToggleStatus(scope.row)"
            />
          </template>
        </el-table-column>
        <el-table-column label="操作" width="280" class-name="action-cell" fixed="right">
          <template #default="scope">
            <div class="action-btns">
              <el-button size="small" @click="handleEdit(scope.row)">
                <el-icon><component :is="icons.Edit" /></el-icon>
                编辑
              </el-button>
              <el-button size="small" type="primary" @click="handleRunNow(scope.row)">
                <el-icon><component :is="icons.VideoPlay" /></el-icon>
                立即执行
              </el-button>
              <el-button size="small" @click="handleViewHistory(scope.row)">
                <el-icon><component :is="icons.Clock" /></el-icon>
                历史
              </el-button>
              <el-button size="small" type="danger" @click="handleDelete(scope.row)">
                <el-icon><component :is="icons.Delete" /></el-icon>
              </el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-wrapper">
        <el-pagination
          layout="total, prev, pager, next"
          :total="filteredTasks.length"
          :page-size="10"
          v-model:current-page="currentPage"
        />
      </div>
    </el-card>

    <el-dialog
      v-model="editDialogVisible"
      :title="editingTask ? '编辑定时任务' : '创建定时任务'"
      width="600px"
      :close-on-click-modal="false"
    >
      <el-form :model="editForm" label-width="120px" :rules="formRules" ref="formRef">
        <el-form-item label="任务名称" prop="name">
          <el-input v-model="editForm.name" placeholder="请输入任务名称" />
        </el-form-item>
        <el-form-item label="Cron表达式" prop="cronExpression">
          <el-select v-model="editForm.cronType" placeholder="选择频率" @change="handleCronTypeChange">
            <el-option label="每小时执行" value="hourly" />
            <el-option label="每天早上9点" value="daily_9am" />
            <el-option label="每个工作日" value="weekday" />
            <el-option label="每周一早上8点" value="weekly" />
            <el-option label="每月1号零点" value="monthly" />
            <el-option label="自定义" value="custom" />
          </el-select>
        </el-form-item>
        <el-form-item v-if="editForm.cronType === 'custom'" label="自定义Cron" prop="cronExpression">
          <el-input v-model="editForm.customCron" placeholder="分 时 日 月 周 (如: 0 0 9 * * 1-5)" />
          <div class="cron-hint">格式：分 时 日 月 周，例如 0 0 9 * * 1-5 表示工作日9点执行</div>
        </el-form-item>
        <el-form-item label="关联用例" prop="caseIds">
          <el-select v-model="editForm.caseIds" multiple placeholder="请选择关联的测试用例" filterable>
            <el-option v-for="c in availableCases" :key="c.id" :label="c.name" :value="c.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="执行环境">
          <el-select v-model="editForm.environment" placeholder="选择执行环境">
            <el-option label="测试环境" value="test" />
            <el-option label="预发环境" value="staging" />
            <el-option label="生产环境" value="production" />
          </el-select>
        </el-form-item>
        <el-form-item label="超时时间(分)">
          <el-input-number v-model="editForm.timeout" :min="1" :max="120" />
        </el-form-item>
        <el-form-item label="启用任务">
          <el-switch v-model="editForm.status" :active-value="'enabled'" :inactive-value="'disabled'" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSaveTask">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog
      v-model="historyDialogVisible"
      title="执行历史"
      width="700px"
    >
      <div v-if="currentHistoryTask">
        <div class="history-header">
          <span>任务：<strong>{{ currentHistoryTask.name }}</strong></span>
          <span class="enabled-tag">
            <el-tag :type="currentHistoryTask.status === 'enabled' ? 'success' : 'info'" size="small">
              {{ currentHistoryTask.status === 'enabled' ? '已启用' : '已禁用' }}
            </el-tag>
          </span>
        </div>
        <el-table :data="executionHistory" stripe size="small">
          <el-table-column prop="executeTime" label="执行时间" width="170" />
          <el-table-column prop="result" label="结果" width="100">
            <template #default="scope">
              <el-tag
                :type="scope.row.result === 'success' ? 'success' : 'danger'"
                size="small"
              >
                {{ scope.row.result === 'success' ? '成功' : '失败' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="total" label="总数" width="70" />
          <el-table-column prop="passed" label="通过" width="70">
            <template #default="scope">
              <span class="pass-text">{{ scope.row.passed }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="failed" label="失败" width="70">
            <template #default="scope">
              <span class="fail-text">{{ scope.row.failed }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="duration" label="耗时" width="80" />
          <el-table-column prop="message" label="备注" show-overflow-tooltip />
        </el-table>
        <div v-if="executionHistory.length === 0" class="empty-history">
          <el-icon :size="40"><component :is="icons.Clock" /></el-icon>
          <p>暂无执行记录</p>
        </div>
      </div>
      <template #footer>
        <el-button @click="historyDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import * as icons from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const searchKeyword = ref('')
const filterStatus = ref('')
const currentPage = ref(1)

const editDialogVisible = ref(false)
const historyDialogVisible = ref(false)
const formRef = ref(null)

const editingTask = ref(null)
const currentHistoryTask = ref(null)

const tasks = ref([
  {
    id: 1,
    name: '每日全量回归测试',
    cronExpression: '0 0 2 * * *',
    nextRunTime: '2026-07-24 02:00:00',
    lastRunTime: '2026-07-23 02:00:00',
    lastResult: 'success',
    status: 'enabled',
    caseIds: ['case1', 'case2', 'case3'],
    environment: 'test',
    timeout: 60
  },
  {
    id: 2,
    name: '工作日接口冒烟测试',
    cronExpression: '0 0 9 * * 1-5',
    nextRunTime: '2026-07-24 09:00:00',
    lastRunTime: '2026-07-23 09:00:00',
    lastResult: 'success',
    status: 'enabled',
    caseIds: ['case1', 'case4'],
    environment: 'test',
    timeout: 30
  },
  {
    id: 3,
    name: '每小时健康检查',
    cronExpression: '0 0 * * * *',
    nextRunTime: '2026-07-23 15:00:00',
    lastRunTime: '2026-07-23 14:00:00',
    lastResult: 'failed',
    status: 'disabled',
    caseIds: ['case1'],
    environment: 'production',
    timeout: 10
  },
  {
    id: 4,
    name: '每周UI自动化测试',
    cronExpression: '0 0 8 ? * MON',
    nextRunTime: '2026-07-28 08:00:00',
    lastRunTime: '2026-07-21 08:00:00',
    lastResult: 'success',
    status: 'enabled',
    caseIds: ['case5', 'case6', 'case7', 'case8'],
    environment: 'staging',
    timeout: 90
  },
  {
    id: 5,
    name: '月度支付接口验证',
    cronExpression: '0 0 0 1 * ?',
    nextRunTime: '2026-08-01 00:00:00',
    lastRunTime: '2026-07-01 00:00:00',
    lastResult: 'success',
    status: 'enabled',
    caseIds: ['case7', 'case8'],
    environment: 'production',
    timeout: 45
  }
])

const availableCases = [
  { id: 'case1', name: '用户登录-正常登录' },
  { id: 'case2', name: '用户登录-密码错误' },
  { id: 'case3', name: '用户登录-账号锁定' },
  { id: 'case4', name: '订单管理-创建订单' },
  { id: 'case5', name: '订单管理-取消订单' },
  { id: 'case6', name: '商品管理-添加商品' },
  { id: 'case7', name: '支付结算-微信支付' },
  { id: 'case8', name: '支付结算-支付宝支付' }
]

const editForm = reactive({
  name: '',
  cronType: 'hourly',
  cronExpression: '0 0 * * * *',
  customCron: '',
  caseIds: [],
  environment: 'test',
  timeout: 30,
  status: 'enabled'
})

const formRules = {
  name: [{ required: true, message: '请输入任务名称', trigger: 'blur' }],
  cronExpression: [{ required: true, message: '请选择Cron表达式', trigger: 'change' }]
}

const cronPresets = {
  hourly: '0 0 * * * *',
  daily_9am: '0 0 9 * * *',
  weekday: '0 0 9 * * 1-5',
  weekly: '0 0 8 ? * MON',
  monthly: '0 0 0 1 * ?'
}

const filteredTasks = computed(() => {
  return tasks.value.filter(task => {
    const matchKeyword = !searchKeyword.value || task.name.includes(searchKeyword.value)
    const matchStatus = !filterStatus.value || task.status === filterStatus.value
    return matchKeyword && matchStatus
  })
})

const executionHistory = ref([])

function handleCronTypeChange() {
  if (editForm.cronType !== 'custom') {
    editForm.cronExpression = cronPresets[editForm.cronType] || ''
  } else {
    editForm.cronExpression = editForm.customCron
  }
}

function handleCreateTask() {
  editingTask.value = null
  editForm.name = ''
  editForm.cronType = 'hourly'
  editForm.cronExpression = cronPresets.hourly
  editForm.customCron = ''
  editForm.caseIds = []
  editForm.environment = 'test'
  editForm.timeout = 30
  editForm.status = 'enabled'
  editDialogVisible.value = true
}

function handleEdit(row) {
  editingTask.value = row
  editForm.name = row.name
  editForm.cronExpression = row.cronExpression
  editForm.caseIds = [...(row.caseIds || [])]
  editForm.environment = row.environment
  editForm.timeout = row.timeout
  editForm.status = row.status

  const matched = Object.entries(cronPresets).find(([_, v]) => v === row.cronExpression)
  editForm.cronType = matched ? matched[0] : 'custom'
  editForm.customCron = matched ? '' : row.cronExpression

  editDialogVisible.value = true
}

async function handleSaveTask() {
  if (!formRef.value) return
  await formRef.value.validate((valid) => {
    if (valid) {
      if (editForm.cronType === 'custom') {
        editForm.cronExpression = editForm.customCron
      }

      if (editingTask.value) {
        const index = tasks.value.findIndex(t => t.id === editingTask.value.id)
        if (index > -1) {
          tasks.value[index] = {
            ...tasks.value[index],
            name: editForm.name,
            cronExpression: editForm.cronExpression,
            caseIds: editForm.caseIds,
            environment: editForm.environment,
            timeout: editForm.timeout,
            status: editForm.status
          }
          ElMessage.success('任务更新成功')
        }
      } else {
        tasks.value.unshift({
          id: Date.now(),
          name: editForm.name,
          cronExpression: editForm.cronExpression,
          nextRunTime: calculateNextRun(editForm.cronExpression),
          lastRunTime: '',
          lastResult: null,
          status: editForm.status,
          caseIds: editForm.caseIds,
          environment: editForm.environment,
          timeout: editForm.timeout
        })
        ElMessage.success('任务创建成功')
      }
      editDialogVisible.value = false
    }
  })
}

function calculateNextRun(cron) {
  const now = new Date()
  const next = new Date(now.getTime() + 60 * 60 * 1000)
  return next.toLocaleString('zh-CN')
}

function handleToggleStatus(row) {
  ElMessage.success(`任务已${row.status === 'enabled' ? '启用' : '禁用'}`)
}

function handleRunNow(row) {
  ElMessageBox.confirm(`确定要立即执行任务 "${row.name}" 吗？`, '确认执行', {
    confirmButtonText: '执行',
    cancelButtonText: '取消',
    type: 'info'
  }).then(() => {
    row.lastRunTime = new Date().toLocaleString('zh-CN')
    row.lastResult = Math.random() > 0.3 ? 'success' : 'failed'
    ElMessage.success(`任务 "${row.name}" 执行完成`)
  }).catch(() => {})
}

function handleViewHistory(row) {
  currentHistoryTask.value = row
  executionHistory.value = generateMockHistory(row)
  historyDialogVisible.value = true
}

function generateMockHistory(task) {
  const history = []
  const baseTime = new Date()
  for (let i = 0; i < 10; i++) {
    const time = new Date(baseTime.getTime() - i * 24 * 60 * 60 * 1000)
    const result = Math.random() > 0.25 ? 'success' : 'failed'
    const total = Math.floor(Math.random() * 20) + 5
    history.push({
      executeTime: time.toLocaleString('zh-CN'),
      result,
      total,
      passed: result === 'success' ? total : Math.floor(total * 0.7),
      failed: result === 'success' ? 0 : total - Math.floor(total * 0.7),
      duration: `${Math.floor(Math.random() * 10) + 2}m ${Math.floor(Math.random() * 60)}s`,
      message: result === 'success' ? '执行成功' : ['接口超时', '元素定位失败', '断言失败'][Math.floor(Math.random() * 3)]
    })
  }
  return history
}

function handleDelete(row) {
  ElMessageBox.confirm(`确定要删除任务 "${row.name}" 吗？`, '确认删除', {
    confirmButtonText: '删除',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    const index = tasks.value.findIndex(t => t.id === row.id)
    if (index > -1) {
      tasks.value.splice(index, 1)
      ElMessage.success('删除成功')
    }
  }).catch(() => {})
}
</script>

<style scoped>
.scheduled-tasks {
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

.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.search-input {
  width: 220px;
}

.filter-select {
  width: 120px;
}

.pagination-wrapper {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}

.cron-tag {
  font-family: monospace;
  font-size: 12px;
}

.cron-hint {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.history-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.enabled-tag {
  margin-left: auto;
}

.empty-history {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 40px;
  color: #909399;
  gap: 8px;
}

.empty-history p {
  margin: 0;
  font-size: 14px;
}

.pass-text {
  color: #67c23a;
  font-weight: 600;
}

.fail-text {
  color: #f56c6c;
  font-weight: 600;
}
</style>