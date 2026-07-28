<template>
  <div class="manual-tasks">
    <div class="page-header">
      <h2>手动任务</h2>
      <p class="page-desc">手动执行自动化测试任务</p>
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
              <el-option label="待执行" value="pending" />
              <el-option label="执行中" value="running" />
              <el-option label="已完成" value="completed" />
              <el-option label="失败" value="failed" />
            </el-select>
            <el-button type="primary" @click="handleCreateTask">
              <el-icon><component :is="icons.Plus" /></el-icon>
              创建任务
            </el-button>
          </div>
        </div>
      </template>

      <el-table :data="filteredTasks" stripe border v-loading="loading">
        <el-table-column prop="name" label="任务名称" min-width="160" show-overflow-tooltip />
        <el-table-column prop="type" label="类型" width="100">
          <template #default="scope">
            <el-tag :type="scope.row.type === 'API' ? 'primary' : 'success'" size="small">
              {{ scope.row.type === 'API' ? '接口测试' : 'UI测试' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="target" label="执行目标" min-width="150" show-overflow-tooltip />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="scope">
            <el-tag :type="getStatusType(scope.row.status)" size="small">
              {{ getStatusLabel(scope.row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="progress" label="进度" width="140">
          <template #default="scope">
            <el-progress
              :percentage="scope.row.progress"
              :status="getProgressStatus(scope.row)"
              :stroke-width="8"
            />
          </template>
        </el-table-column>
        <el-table-column prop="createdAt" label="创建时间" width="160">
          <template #default="scope">
            {{ formatDate(scope.row.createdAt) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="340" class-name="action-cell" fixed="right">
          <template #default="scope">
            <div class="action-btns">
              <el-button
                size="small"
                type="primary"
                :disabled="scope.row.status === 'running'"
                @click="handleExecute(scope.row)"
              >
                <el-icon><component :is="icons.VideoPlay" /></el-icon>
                执行
              </el-button>
              <el-button
                size="small"
                type="warning"
                :disabled="scope.row.status !== 'running'"
                @click="handleStop(scope.row)"
              >
                <el-icon><component :is="icons.Close" /></el-icon>
                停止
              </el-button>
              <el-button
                size="small"
                :disabled="scope.row.status === 'pending'"
                @click="handleViewResult(scope.row)"
              >
                <el-icon><component :is="icons.View" /></el-icon>
                结果
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
      v-model="createDialogVisible"
      title="创建手动任务"
      width="560px"
      :close-on-click-modal="false"
    >
      <el-form :model="createForm" label-width="100px" :rules="formRules" ref="formRef">
        <el-form-item label="任务名称" prop="name">
          <el-input v-model="createForm.name" placeholder="请输入任务名称" />
        </el-form-item>
        <el-form-item label="任务类型" prop="type">
          <el-select v-model="createForm.type" placeholder="请选择任务类型">
            <el-option label="接口测试" value="API" />
            <el-option label="UI测试" value="UI" />
          </el-select>
        </el-form-item>
        <el-form-item label="执行目标" prop="target">
          <el-select v-model="createForm.target" placeholder="请选择执行目标" multiple filterable allow-create>
            <el-option label="用户登录模块" value="用户登录模块" />
            <el-option label="订单管理模块" value="订单管理模块" />
            <el-option label="商品管理模块" value="商品管理模块" />
            <el-option label="支付结算模块" value="支付结算模块" />
            <el-option label="数据报表模块" value="数据报表模块" />
          </el-select>
        </el-form-item>
        <el-form-item label="选择用例" prop="caseIds">
          <el-select v-model="createForm.caseIds" multiple placeholder="请选择要执行的测试用例" filterable>
            <el-option v-for="c in availableCases" :key="c.id" :label="c.name" :value="c.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="执行参数">
          <el-input
            v-model="createForm.params"
            type="textarea"
            :rows="3"
            placeholder='{"browser":"chrome","headless":true,"timeout":30}'
          />
        </el-form-item>
        <el-form-item label="优先级">
          <el-radio-group v-model="createForm.priority">
            <el-radio value="high">高</el-radio>
            <el-radio value="medium">中</el-radio>
            <el-radio value="low">低</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleConfirmCreate">确认创建</el-button>
      </template>
    </el-dialog>

    <el-dialog
      v-model="resultDialogVisible"
      title="任务执行结果"
      width="600px"
    >
      <div v-if="currentResult" class="result-container">
        <div class="result-summary">
          <div class="summary-item">
            <div class="summary-value">{{ currentResult.total }}</div>
            <div class="summary-label">总用例</div>
          </div>
          <div class="summary-item pass">
            <div class="summary-value">{{ currentResult.passed }}</div>
            <div class="summary-label">通过</div>
          </div>
          <div class="summary-item fail">
            <div class="summary-value">{{ currentResult.failed }}</div>
            <div class="summary-label">失败</div>
          </div>
          <div class="summary-item">
            <div class="summary-value">{{ currentResult.duration }}</div>
            <div class="summary-label">耗时</div>
          </div>
        </div>
        <el-divider content-position="left">执行详情</el-divider>
        <el-table :data="currentResult.details" size="small" max-height="260">
          <el-table-column prop="name" label="用例名称" />
          <el-table-column prop="status" label="结果" width="80">
            <template #default="scope">
              <el-tag :type="scope.row.status === 'passed' ? 'success' : 'danger'" size="small">
                {{ scope.row.status === 'passed' ? '通过' : '失败' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="duration" label="耗时" width="80" />
          <el-table-column prop="message" label="备注" show-overflow-tooltip />
        </el-table>
      </div>
      <template #footer>
        <el-button @click="resultDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import * as icons from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const loading = ref(false)
const searchKeyword = ref('')
const filterStatus = ref('')
const currentPage = ref(1)

const createDialogVisible = ref(false)
const resultDialogVisible = ref(false)
const formRef = ref(null)

const currentResult = ref(null)

const tasks = ref([
  {
    id: 1,
    name: '登录接口回归测试',
    type: 'API',
    target: '用户登录模块',
    status: 'pending',
    progress: 0,
    createdAt: '2026-07-23 09:30:00',
    result: null
  },
  {
    id: 2,
    name: '订单管理UI测试',
    type: 'UI',
    target: '订单管理模块',
    status: 'completed',
    progress: 100,
    createdAt: '2026-07-23 08:15:00',
    result: {
      total: 20,
      passed: 18,
      failed: 2,
      duration: '5m 32s',
      details: [
        { name: '创建订单', status: 'passed', duration: '15s', message: '' },
        { name: '支付订单', status: 'passed', duration: '22s', message: '' },
        { name: '取消订单', status: 'failed', duration: '18s', message: '元素定位失败' },
        { name: '查询订单', status: 'passed', duration: '12s', message: '' },
        { name: '修改订单', status: 'passed', duration: '20s', message: '' }
      ]
    }
  },
  {
    id: 3,
    name: '商品接口批量测试',
    type: 'API',
    target: '商品管理模块',
    status: 'running',
    progress: 45,
    createdAt: '2026-07-23 10:00:00',
    result: null
  },
  {
    id: 4,
    name: '支付流程E2E测试',
    type: 'UI',
    target: '支付结算模块',
    status: 'failed',
    progress: 60,
    createdAt: '2026-07-22 16:20:00',
    result: {
      total: 15,
      passed: 10,
      failed: 5,
      duration: '8m 15s',
      details: [
        { name: '选择商品', status: 'passed', duration: '10s', message: '' },
        { name: '加入购物车', status: 'passed', duration: '12s', message: '' },
        { name: '结算页面', status: 'failed', duration: '25s', message: '页面加载超时' },
        { name: '支付验证', status: 'failed', duration: '30s', message: '支付接口500错误' }
      ]
    }
  },
  {
    id: 5,
    name: '数据报表接口测试',
    type: 'API',
    target: '数据报表模块',
    status: 'completed',
    progress: 100,
    createdAt: '2026-07-22 14:00:00',
    result: {
      total: 12,
      passed: 12,
      failed: 0,
      duration: '3m 20s',
      details: [
        { name: '销售报表', status: 'passed', duration: '25s', message: '' },
        { name: '库存报表', status: 'passed', duration: '20s', message: '' },
        { name: '用户报表', status: 'passed', duration: '18s', message: '' }
      ]
    }
  },
  {
    id: 6,
    name: '用户权限UI测试',
    type: 'UI',
    target: '用户登录模块',
    status: 'pending',
    progress: 0,
    createdAt: '2026-07-23 11:00:00',
    result: null
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

const createForm = reactive({
  name: '',
  type: 'API',
  target: [],
  caseIds: [],
  params: '',
  priority: 'medium'
})

const formRules = {
  name: [{ required: true, message: '请输入任务名称', trigger: 'blur' }],
  type: [{ required: true, message: '请选择任务类型', trigger: 'change' }],
  target: [{ required: true, message: '请选择执行目标', trigger: 'change' }]
}

const filteredTasks = computed(() => {
  return tasks.value.filter(task => {
    const matchKeyword = !searchKeyword.value || task.name.includes(searchKeyword.value)
    const matchStatus = !filterStatus.value || task.status === filterStatus.value
    return matchKeyword && matchStatus
  })
})

function getStatusType(status) {
  const types = { pending: 'info', running: 'warning', completed: 'success', failed: 'danger' }
  return types[status] || 'info'
}

function getStatusLabel(status) {
  const labels = { pending: '待执行', running: '执行中', completed: '已完成', failed: '失败' }
  return labels[status] || status
}

function getProgressStatus(row) {
  if (row.status === 'failed') return 'exception'
  if (row.status === 'completed') return 'success'
  if (row.status === 'running') return ''
  return ''
}

function formatDate(dateStr) {
  if (!dateStr) return '-'
  return dateStr
}

function handleCreateTask() {
  createForm.name = ''
  createForm.type = 'API'
  createForm.target = []
  createForm.caseIds = []
  createForm.params = ''
  createForm.priority = 'medium'
  createDialogVisible.value = true
}

async function handleConfirmCreate() {
  if (!formRef.value) return
  await formRef.value.validate((valid) => {
    if (valid) {
      const newTask = {
        id: Date.now(),
        name: createForm.name,
        type: createForm.type,
        target: Array.isArray(createForm.target) ? createForm.target.join(', ') : createForm.target,
        status: 'pending',
        progress: 0,
        createdAt: new Date().toLocaleString('zh-CN'),
        result: null
      }
      tasks.value.unshift(newTask)
      createDialogVisible.value = false
      ElMessage.success('任务创建成功')
    }
  })
}

function handleExecute(row) {
  row.status = 'running'
  row.progress = 0
  row.result = null

  const timer = setInterval(() => {
    if (row.status !== 'running') {
      clearInterval(timer)
      return
    }
    row.progress += Math.random() * 15 + 5
    if (row.progress >= 100) {
      row.progress = 100
      clearInterval(timer)
      const isSuccess = Math.random() > 0.2
      row.status = isSuccess ? 'completed' : 'failed'
      const total = Math.floor(Math.random() * 15) + 5
      row.result = {
        total,
        passed: isSuccess ? total : Math.floor(total * 0.7),
        failed: isSuccess ? 0 : total - Math.floor(total * 0.7),
        duration: `${Math.floor(Math.random() * 10) + 2}m ${Math.floor(Math.random() * 60)}s`,
        details: generateMockDetails(total, isSuccess)
      }
      ElMessage.success(isSuccess ? '任务执行完成' : '任务执行失败')
    }
  }, 500)

  ElMessage.info(`任务 "${row.name}" 开始执行`)
}

function generateMockDetails(total, success) {
  const details = []
  const caseNames = ['功能验证', '接口响应', '数据校验', '异常处理', '性能测试']
  for (let i = 0; i < total; i++) {
    const passed = success || Math.random() > 0.3
    details.push({
      name: `${caseNames[i % caseNames.length]}_${i + 1}`,
      status: passed ? 'passed' : 'failed',
      duration: `${Math.floor(Math.random() * 30) + 5}s`,
      message: passed ? '' : ['元素定位失败', '接口超时', '断言不匹配', '页面加载异常'][Math.floor(Math.random() * 4)]
    })
  }
  return details
}

function handleStop(row) {
  ElMessageBox.confirm(`确定要停止任务 "${row.name}" 吗？`, '确认停止', {
    confirmButtonText: '停止',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    row.status = 'failed'
    row.progress = Math.max(row.progress, 30)
    if (!row.result) {
      row.result = {
        total: 10,
        passed: Math.floor(Math.random() * 5),
        failed: 0,
        duration: '已停止',
        details: []
      }
    }
    ElMessage.info('任务已停止')
  }).catch(() => {})
}

function handleViewResult(row) {
  if (row.result) {
    currentResult.value = row.result
    resultDialogVisible.value = true
  } else {
    ElMessage.warning('该任务暂无执行结果')
  }
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
.manual-tasks {
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

.result-container {
  padding: 10px 0;
}

.result-summary {
  display: flex;
  justify-content: space-around;
  margin-bottom: 10px;
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
</style>