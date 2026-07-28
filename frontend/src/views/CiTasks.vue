<template>
  <div class="ci-tasks">
    <div class="page-header">
      <h2>CI触发任务</h2>
      <p class="page-desc">配置CI/CD触发自动化测试</p>
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
            <el-select v-model="filterCiType" placeholder="CI类型" size="small" class="filter-select" clearable>
              <el-option label="Jenkins" value="Jenkins" />
              <el-option label="GitLab CI" value="GitLab CI" />
              <el-option label="GitHub Actions" value="GitHub Actions" />
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
        <el-table-column prop="ciType" label="CI类型" width="140">
          <template #default="scope">
            <el-tag :type="getCiTypeTag(scope.row.ciType)" size="small">
              {{ scope.row.ciType }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="triggerCondition" label="触发条件" width="120">
          <template #default="scope">
            <el-tag type="warning" size="small">{{ getTriggerLabel(scope.row.triggerCondition) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="webhookUrl" label="Webhook URL" min-width="200" show-overflow-tooltip>
          <template #default="scope">
            <span class="url-text">{{ scope.row.webhookUrl }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="lastTriggeredAt" label="最后触发时间" min-width="160">
          <template #default="scope">
            {{ scope.row.lastTriggeredAt || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="scope">
            <el-tag :type="scope.row.status === 'active' ? 'success' : 'info'" size="small">
              {{ scope.row.status === 'active' ? '已启用' : '已禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="280" class-name="action-cell" fixed="right">
          <template #default="scope">
            <div class="action-btns">
              <el-button size="small" @click="handleEdit(scope.row)">
                <el-icon><component :is="icons.Edit" /></el-icon>
                编辑
              </el-button>
              <el-button size="small" type="warning" @click="handleTestConnection(scope.row)">
                <el-icon><component :is="icons.Connection" /></el-icon>
                测试连接
              </el-button>
              <el-button size="small" @click="handleViewHistory(scope.row)">
                <el-icon><component :is="icons.Clock" /></el-icon>
                触发历史
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
      :title="editingTask ? '编辑CI触发任务' : '创建CI触发任务'"
      width="620px"
      :close-on-click-modal="false"
    >
      <el-form :model="editForm" label-width="120px" :rules="formRules" ref="formRef">
        <el-form-item label="任务名称" prop="name">
          <el-input v-model="editForm.name" placeholder="请输入任务名称" />
        </el-form-item>
        <el-form-item label="CI类型" prop="ciType">
          <el-select v-model="editForm.ciType" placeholder="请选择CI类型" @change="handleCiTypeChange">
            <el-option label="Jenkins" value="Jenkins" />
            <el-option label="GitLab CI" value="GitLab CI" />
            <el-option label="GitHub Actions" value="GitHub Actions" />
          </el-select>
        </el-form-item>
        <el-form-item label="Webhook URL" prop="webhookUrl">
          <el-input v-model="editForm.webhookUrl" placeholder="https://ci.example.com/webhook/..." />
        </el-form-item>
        <el-form-item label="访问令牌">
          <el-input v-model="editForm.token" type="password" show-password placeholder="CI访问令牌（可选）" />
        </el-form-item>
        <el-form-item label="触发条件" prop="triggerCondition">
          <el-checkbox-group v-model="editForm.triggerConditions">
            <el-checkbox value="push">代码推送</el-checkbox>
            <el-checkbox value="tag">标签发布</el-checkbox>
            <el-checkbox value="mr">合并请求</el-checkbox>
            <el-checkbox value="schedule">定时触发</el-checkbox>
          </el-checkbox-group>
        </el-form-item>
        <el-form-item label="分支过滤">
          <el-input v-model="editForm.branches" placeholder="多个分支用逗号分隔，如: main,develop" />
        </el-form-item>
        <el-form-item label="关联用例" prop="caseIds">
          <el-select v-model="editForm.caseIds" multiple placeholder="请选择关联的测试用例" filterable>
            <el-option v-for="c in availableCases" :key="c.id" :label="c.name" :value="c.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="执行参数">
          <el-input
            v-model="editForm.params"
            type="textarea"
            :rows="3"
            placeholder='{"env":"test","browser":"chrome"}'
          />
        </el-form-item>
        <el-form-item label="启用任务">
          <el-switch v-model="editForm.status" active-value="active" inactive-value="inactive" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editDialogVisible = false">取消</el-button>
        <el-button type="warning" @click="handleTestConnectionFromForm">
          <el-icon><component :is="icons.Connection" /></el-icon>
          测试连接
        </el-button>
        <el-button type="primary" @click="handleSaveTask">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog
      v-model="historyDialogVisible"
      title="触发历史"
      width="750px"
    >
      <div v-if="currentHistoryTask">
        <div class="history-header">
          <span>任务：<strong>{{ currentHistoryTask.name }}</strong></span>
          <el-tag :type="getCiTypeTag(currentHistoryTask.ciType)" size="small">
            {{ currentHistoryTask.ciType }}
          </el-tag>
        </div>
        <el-table :data="triggerHistory" stripe size="small">
          <el-table-column prop="triggeredAt" label="触发时间" width="170" />
          <el-table-column prop="triggerCondition" label="触发条件" width="110">
            <template #default="scope">
              <el-tag type="warning" size="small">{{ getTriggerLabel(scope.row.triggerCondition) }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="branch" label="分支" width="100" />
          <el-table-column prop="commitId" label="Commit ID" width="120">
            <template #default="scope">
              <span class="commit-id">{{ scope.row.commitId }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="result" label="执行结果" width="100">
            <template #default="scope">
              <el-tag
                :type="scope.row.result === 'success' ? 'success' : scope.row.result === 'failed' ? 'danger' : 'info'"
                size="small"
              >
                {{ scope.row.result === 'success' ? '成功' : scope.row.result === 'failed' ? '失败' : '执行中' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="duration" label="耗时" width="80" />
          <el-table-column prop="message" label="备注" show-overflow-tooltip />
        </el-table>
        <div v-if="triggerHistory.length === 0" class="empty-history">
          <el-icon :size="40"><component :is="icons.Clock" /></el-icon>
          <p>暂无触发记录</p>
        </div>
      </div>
      <template #footer>
        <el-button @click="historyDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>

    <el-dialog
      v-model="testConnectionVisible"
      title="测试连接"
      width="450px"
    >
      <div class="test-connection-content">
        <div v-if="testing" class="testing-state">
          <el-icon :size="32" class="is-loading"><component :is="icons.Loading" /></el-icon>
          <p>正在连接CI服务器...</p>
        </div>
        <div v-else-if="testResult" class="test-result">
          <el-alert
            :title="testResult.success ? '连接成功' : '连接失败'"
            :type="testResult.success ? 'success' : 'error'"
            :description="testResult.message"
            show-icon
            :closable="false"
          />
          <div v-if="testResult.success" class="connection-details">
            <div>响应时间：{{ testResult.responseTime }}ms</div>
            <div>服务器版本：{{ testResult.serverVersion }}</div>
          </div>
        </div>
        <div v-else class="ready-state">
          <el-icon :size="32" color="#909399"><component :is="icons.Connection" /></el-icon>
          <p>准备测试连接</p>
          <p class="hint">点击下方按钮开始测试</p>
        </div>
      </div>
      <template #footer>
        <el-button @click="testConnectionVisible = false">关闭</el-button>
        <el-button type="primary" @click="performTestConnection" :loading="testing" :disabled="testResult?.success">
          {{ testing ? '测试中...' : '开始测试' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import * as icons from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const searchKeyword = ref('')
const filterCiType = ref('')
const currentPage = ref(1)

const editDialogVisible = ref(false)
const historyDialogVisible = ref(false)
const testConnectionVisible = ref(false)
const formRef = ref(null)

const editingTask = ref(null)
const currentHistoryTask = ref(null)
const testing = ref(false)
const testResult = ref(null)

const tasks = ref([
  {
    id: 1,
    name: '主分支自动回归测试',
    ciType: 'Jenkins',
    triggerConditions: ['push'],
    triggerCondition: 'push',
    webhookUrl: 'https://ci.company.com/jenkins/job/AutoTest/build',
    token: '********',
    branches: 'main',
    caseIds: ['case1', 'case2', 'case3', 'case4'],
    params: '{"env":"production"}',
    status: 'active',
    lastTriggeredAt: '2026-07-23 10:30:00'
  },
  {
    id: 2,
    name: 'GitLab MR触发测试',
    ciType: 'GitLab CI',
    triggerConditions: ['mr'],
    triggerCondition: 'mr',
    webhookUrl: 'https://gitlab.com/api/v4/projects/123/trigger/pipeline',
    token: '********',
    branches: 'develop,feature/*',
    caseIds: ['case5', 'case6'],
    params: '{"env":"staging"}',
    status: 'active',
    lastTriggeredAt: '2026-07-23 09:15:00'
  },
  {
    id: 3,
    name: '版本标签发布测试',
    ciType: 'GitHub Actions',
    triggerConditions: ['tag'],
    triggerCondition: 'tag',
    webhookUrl: 'https://github.com/company/repo/actions/workflows/test.yml',
    token: '********',
    branches: 'v*',
    caseIds: ['case1', 'case7', 'case8'],
    params: '{"env":"production","full":true}',
    status: 'active',
    lastTriggeredAt: '2026-07-22 16:00:00'
  },
  {
    id: 4,
    name: '定时夜间构建',
    ciType: 'Jenkins',
    triggerConditions: ['schedule'],
    triggerCondition: 'schedule',
    webhookUrl: 'https://ci.company.com/jenkins/job/Nightly/build',
    token: '********',
    branches: 'main',
    caseIds: ['case1', 'case2', 'case3', 'case4', 'case5', 'case6'],
    params: '{"env":"test","nightly":true}',
    status: 'inactive',
    lastTriggeredAt: '2026-07-21 02:00:00'
  },
  {
    id: 5,
    name: 'GitHub PR快速测试',
    ciType: 'GitHub Actions',
    triggerConditions: ['mr', 'push'],
    triggerCondition: 'mr',
    webhookUrl: 'https://github.com/company/repo/actions/workflows/pr-test.yml',
    token: '********',
    branches: 'pull_requests',
    caseIds: ['case1', 'case4'],
    params: '{"env":"ci","quick":true}',
    status: 'active',
    lastTriggeredAt: '2026-07-23 11:00:00'
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
  ciType: 'Jenkins',
  webhookUrl: '',
  token: '',
  triggerConditions: ['push'],
  triggerCondition: 'push',
  branches: '',
  caseIds: [],
  params: '',
  status: 'active'
})

const formRules = {
  name: [{ required: true, message: '请输入任务名称', trigger: 'blur' }],
  ciType: [{ required: true, message: '请选择CI类型', trigger: 'change' }],
  webhookUrl: [{ required: true, message: '请输入Webhook URL', trigger: 'blur' }]
}

const filteredTasks = computed(() => {
  return tasks.value.filter(task => {
    const matchKeyword = !searchKeyword.value || task.name.includes(searchKeyword.value)
    const matchCiType = !filterCiType.value || task.ciType === filterCiType.value
    return matchKeyword && matchCiType
  })
})

const triggerHistory = ref([])

function getCiTypeTag(ciType) {
  const types = { 'Jenkins': 'primary', 'GitLab CI': 'success', 'GitHub Actions': 'warning' }
  return types[ciType] || 'info'
}

function getTriggerLabel(condition) {
  const labels = { push: '代码推送', tag: '标签发布', mr: '合并请求', schedule: '定时触发' }
  return labels[condition] || condition
}

function handleCiTypeChange() {
  const defaults = {
    'Jenkins': { url: 'https://ci.company.com/jenkins/job/', placeholder: 'Jenkins Job URL' },
    'GitLab CI': { url: 'https://gitlab.com/api/v4/projects/', placeholder: 'GitLab Project URL' },
    'GitHub Actions': { url: 'https://github.com/', placeholder: 'GitHub Actions Workflow URL' }
  }
  const selected = defaults[editForm.ciType]
  if (selected && !editForm.webhookUrl) {
    editForm.webhookUrl = selected.url
  }
}

function handleCreateTask() {
  editingTask.value = null
  editForm.name = ''
  editForm.ciType = 'Jenkins'
  editForm.webhookUrl = ''
  editForm.token = ''
  editForm.triggerConditions = ['push']
  editForm.triggerCondition = 'push'
  editForm.branches = ''
  editForm.caseIds = []
  editForm.params = ''
  editForm.status = 'active'
  editDialogVisible.value = true
}

function handleEdit(row) {
  editingTask.value = row
  editForm.name = row.name
  editForm.ciType = row.ciType
  editForm.webhookUrl = row.webhookUrl
  editForm.token = row.token || ''
  editForm.triggerConditions = [...(row.triggerConditions || [row.triggerCondition])]
  editForm.triggerCondition = row.triggerCondition
  editForm.branches = row.branches || ''
  editForm.caseIds = [...(row.caseIds || [])]
  editForm.params = row.params || ''
  editForm.status = row.status
  editDialogVisible.value = true
}

async function handleSaveTask() {
  if (!formRef.value) return
  await formRef.value.validate((valid) => {
    if (valid) {
      editForm.triggerCondition = editForm.triggerConditions[0] || 'push'

      if (editingTask.value) {
        const index = tasks.value.findIndex(t => t.id === editingTask.value.id)
        if (index > -1) {
          tasks.value[index] = {
            ...tasks.value[index],
            name: editForm.name,
            ciType: editForm.ciType,
            webhookUrl: editForm.webhookUrl,
            token: editForm.token,
            triggerConditions: editForm.triggerConditions,
            triggerCondition: editForm.triggerCondition,
            branches: editForm.branches,
            caseIds: editForm.caseIds,
            params: editForm.params,
            status: editForm.status
          }
          ElMessage.success('任务更新成功')
        }
      } else {
        tasks.value.unshift({
          id: Date.now(),
          name: editForm.name,
          ciType: editForm.ciType,
          triggerConditions: editForm.triggerConditions,
          triggerCondition: editForm.triggerCondition,
          webhookUrl: editForm.webhookUrl,
          token: editForm.token,
          branches: editForm.branches,
          caseIds: editForm.caseIds,
          params: editForm.params,
          status: editForm.status,
          lastTriggeredAt: ''
        })
        ElMessage.success('任务创建成功')
      }
      editDialogVisible.value = false
    }
  })
}

function handleTestConnection(row) {
  testResult.value = null
  testConnectionVisible.value = true
  performTestConnection()
}

function handleTestConnectionFromForm() {
  testResult.value = null
  testConnectionVisible.value = true
  performTestConnection()
}

function performTestConnection() {
  testing.value = true
  testResult.value = null

  setTimeout(() => {
    const success = Math.random() > 0.2
    testing.value = false
    testResult.value = {
      success,
      message: success
        ? `成功连接到CI服务器 ${editForm.ciType || 'Jenkins'}`
        : '连接超时或认证失败，请检查URL和令牌配置',
      responseTime: Math.floor(Math.random() * 200) + 50,
      serverVersion: success ? `${editForm.ciType || 'Jenkins'} v${Math.floor(Math.random() * 3) + 2}.${Math.floor(Math.random() * 10)}` : ''
    }
  }, 2000)
}

function handleViewHistory(row) {
  currentHistoryTask.value = row
  triggerHistory.value = generateMockHistory(row)
  historyDialogVisible.value = true
}

function generateMockHistory(task) {
  const history = []
  const conditions = ['push', 'tag', 'mr', 'schedule']
  const branches = ['main', 'develop', 'feature/login', 'release/v1.2']
  const baseTime = new Date()
  for (let i = 0; i < 8; i++) {
    const time = new Date(baseTime.getTime() - i * 60 * 60 * 1000)
    const result = Math.random() > 0.2 ? 'success' : Math.random() > 0.5 ? 'failed' : 'running'
    history.push({
      triggeredAt: time.toLocaleString('zh-CN'),
      triggerCondition: conditions[Math.floor(Math.random() * conditions.length)],
      branch: branches[Math.floor(Math.random() * branches.length)],
      commitId: `${Math.random().toString(16).substr(2, 8)}`,
      result,
      duration: result === 'running' ? '执行中' : `${Math.floor(Math.random() * 10) + 2}m`,
      message: result === 'success' ? '执行成功' : result === 'failed' ? '部分用例失败' : '正在执行测试...'
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
.ci-tasks {
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
  width: 140px;
}

.pagination-wrapper {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}

.url-text {
  font-family: monospace;
  font-size: 12px;
  color: #606266;
}

.commit-id {
  font-family: monospace;
  font-size: 12px;
  color: #606266;
}

.history-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
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

.test-connection-content {
  text-align: center;
  padding: 20px 0;
}

.testing-state,
.ready-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  color: #606266;
}

.test-result {
  text-align: left;
}

.connection-details {
  margin-top: 12px;
  padding: 12px;
  background: #f5f7fa;
  border-radius: 6px;
  font-size: 13px;
  color: #606266;
  line-height: 1.8;
}

.hint {
  font-size: 12px;
  color: #909399;
}
</style>