<template>
  <div class="api-tasks">
    <div class="page-header">
      <h2>接口任务管理</h2>
      <p class="page-desc">管理接口自动化测试任务，支持定时执行和手动触发</p>
    </div>
    
    <el-card>
      <el-tabs v-model="activeTab">
        <el-tab-pane name="api">
          <template #label>
            <span><el-icon><component :is="icons.Connection" /></el-icon> 接口任务</span>
          </template>
          
          <div class="tab-header">
            <div class="header-actions">
              <el-button type="primary" @click="handleAdd">
                <el-icon><component :is="icons.Plus" /></el-icon>
                新建任务
              </el-button>
              <el-button @click="handleBatchExecute" :disabled="selectedTasks.length === 0">
                <el-icon><component :is="icons.VideoPlay" /></el-icon>
                批量执行
              </el-button>
              <el-button @click="handleBatchToggle" :disabled="selectedTasks.length === 0">
                <el-icon><component :is="icons.Switch" /></el-icon>
                批量{{ allSelectedEnabled ? '禁用' : '启用' }}
              </el-button>
              <el-button type="danger" @click="handleBatchDelete" :disabled="selectedTasks.length === 0">
                <el-icon><component :is="icons.Delete" /></el-icon>
                批量删除
              </el-button>
            </div>
          </div>
          
          <div class="filter-bar">
            <el-select v-model="filterStatus" size="small" placeholder="任务状态">
              <el-option label="全部" value="" />
              <el-option label="已启用" value="已启用" />
              <el-option label="已禁用" value="已禁用" />
            </el-select>
            <el-select v-model="filterLastRun" size="small" placeholder="上次执行">
              <el-option label="全部" value="" />
              <el-option label="成功" value="成功" />
              <el-option label="失败" value="失败" />
            </el-select>
            <el-input 
              v-model="searchKeyword" 
              placeholder="搜索任务名称或场景..." 
              size="small"
              class="search-input"
              @keyup.enter="loadTasks"
            >
              <template #prefix>
                <el-icon><component :is="icons.Search" /></el-icon>
              </template>
            </el-input>
          </div>
          
          <div v-if="filteredTasks.length === 0" class="empty-state">
            <el-icon :size="48" class="empty-icon"><component :is="icons.Box" /></el-icon>
            <span>暂无任务</span>
            <el-button size="small" type="primary" @click="handleAdd">新建任务</el-button>
          </div>
          
          <el-table v-else :data="filteredTasks" stripe border @selection-change="handleSelectionChange">
            <el-table-column type="selection" width="50" />
            <el-table-column label="编号" width="60">
              <template #default="scope">{{ scope.$index + 1 }}</template>
            </el-table-column>
            <el-table-column prop="name" label="任务名称" min-width="150" />
            <el-table-column prop="scenario_name" label="关联场景" width="150" />
            <el-table-column prop="environment_name" label="测试环境" width="120" />
            <el-table-column prop="cron_expression" label="定时规则" width="150">
              <template #default="scope">
                <span v-if="scope.row.cron_expression">{{ scope.row.cron_expression }}</span>
                <span v-else class="text-gray">手动执行</span>
              </template>
            </el-table-column>
            <el-table-column prop="status" label="状态" width="80">
              <template #default="scope">
                <el-tag :type="scope.row.status === '已启用' ? 'success' : 'info'">{{ scope.row.status }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="last_run_status" label="上次执行" width="100">
              <template #default="scope">
                <el-tag v-if="scope.row.last_run_status" :type="scope.row.last_run_status === '成功' ? 'success' : 'danger'">
                  {{ scope.row.last_run_status }}
                </el-tag>
                <span v-else class="text-gray">未执行</span>
              </template>
            </el-table-column>
            <el-table-column prop="last_run_time" label="上次执行时间" width="160" />
            <el-table-column label="操作" width="300" class-name="action-cell">
              <template #default="scope">
                <div class="action-btns">
                  <el-button size="small" @click="handleExecute(scope.row)">执行</el-button>
                  <el-button size="small" @click="handleEdit(scope.row)">编辑</el-button>
                  <el-button size="small" @click="handleToggleStatus(scope.row)">
                    {{ scope.row.status === '已启用' ? '禁用' : '启用' }}
                  </el-button>
                  <el-button size="small" type="danger" @click="handleDelete(scope.row)">删除</el-button>
                </div>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>
        
        <el-tab-pane name="git">
          <template #label>
            <span><el-icon><component :is="icons.Link" /></el-icon> Git任务</span>
          </template>
          
          <div class="tab-header">
            <div class="header-actions">
              <el-button type="primary" @click="handleGitAdd">
                <el-icon><component :is="icons.Plus" /></el-icon>
                新建Git任务
              </el-button>
            </div>
          </div>
          
          <div class="filter-bar">
            <el-input 
              v-model="gitSearchKeyword" 
              placeholder="搜索Git任务名称..." 
              size="small"
              class="search-input"
            >
              <template #prefix>
                <el-icon><component :is="icons.Search" /></el-icon>
              </template>
            </el-input>
          </div>
          
          <div v-if="filteredGitTasks.length === 0" class="empty-state">
            <el-icon :size="48" class="empty-icon"><component :is="icons.Box" /></el-icon>
            <span>暂无Git任务</span>
            <el-button size="small" type="primary" @click="handleGitAdd">新建Git任务</el-button>
          </div>
          
          <el-table v-else :data="filteredGitTasks" stripe border>
            <el-table-column label="编号" width="60">
              <template #default="scope">{{ scope.$index + 1 }}</template>
            </el-table-column>
            <el-table-column prop="name" label="任务名称" min-width="150" />
            <el-table-column prop="repo_url" label="仓库地址" min-width="200">
              <template #default="scope">
                <el-tooltip :content="scope.row.repo_url" placement="top">
                  <span class="repo-url">{{ scope.row.repo_url }}</span>
                </el-tooltip>
              </template>
            </el-table-column>
            <el-table-column prop="branch" label="分支" width="100" />
            <el-table-column prop="script_path" label="脚本路径" width="150">
              <template #default="scope">
                <span v-if="scope.row.script_path">{{ scope.row.script_path }}</span>
                <span v-else class="text-gray">根目录</span>
              </template>
            </el-table-column>
            <el-table-column prop="run_command" label="运行命令" width="120" />
            <el-table-column prop="cron_expression" label="定时规则" width="150">
              <template #default="scope">
                <span v-if="scope.row.cron_expression">{{ scope.row.cron_expression }}</span>
                <span v-else class="text-gray">手动执行</span>
              </template>
            </el-table-column>
            <el-table-column prop="status" label="状态" width="80">
              <template #default="scope">
                <el-tag :type="scope.row.status === '已启用' ? 'success' : 'info'">{{ scope.row.status }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="last_run_status" label="上次执行" width="100">
              <template #default="scope">
                <el-tag v-if="scope.row.last_run_status" :type="scope.row.last_run_status === '成功' ? 'success' : 'danger'">
                  {{ scope.row.last_run_status }}
                </el-tag>
                <span v-else class="text-gray">未执行</span>
              </template>
            </el-table-column>
            <el-table-column prop="last_run_time" label="上次执行时间" width="160" />
            <el-table-column label="操作" width="340" class-name="action-cell">
              <template #default="scope">
                <div class="action-btns">
                  <el-button size="small" type="primary" @click="handleGitPull(scope.row)">拉取</el-button>
                  <el-button size="small" type="success" @click="handleGitExecute(scope.row)">执行</el-button>
                  <el-button size="small" @click="handleGitEdit(scope.row)">编辑</el-button>
                  <el-button size="small" type="danger" @click="handleGitDelete(scope.row)">删除</el-button>
                </div>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑任务' : '新建任务'" width="600px">
      <el-form :model="taskForm" label-width="100px">
        <el-form-item label="任务名称" required>
          <el-input v-model="taskForm.name" placeholder="请输入任务名称" />
        </el-form-item>
        <el-form-item label="关联场景" required>
          <el-select v-model="taskForm.scenario_id" placeholder="选择场景" @change="handleScenarioChange">
            <el-option v-for="scenario in scenarios" :key="scenario.id" :label="scenario.name" :value="scenario.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="测试环境" required>
          <el-select v-model="taskForm.environment_id" placeholder="选择环境" @change="handleEnvChange">
            <el-option v-for="env in environments" :key="env.id" :label="env.name" :value="env.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="定时规则">
          <el-input v-model="taskForm.cron_expression" placeholder="Cron表达式，如 0 9 * * *" />
          <div class="cron-help">
            <el-icon :size="14"><component :is="icons.InfoFilled" /></el-icon>
            <span>Cron表达式格式: 秒 分 时 日 月 周</span>
          </div>
          <div class="cron-examples">
            <el-tag size="small" @click="taskForm.cron_expression = '0 0 9 * * *'">每天9点</el-tag>
            <el-tag size="small" @click="taskForm.cron_expression = '0 0 9 * * 1-5'">工作日9点</el-tag>
            <el-tag size="small" @click="taskForm.cron_expression = '0 */30 * * * *'">每30分钟</el-tag>
            <el-tag size="small" @click="taskForm.cron_expression = '0 0 0 * * 0'">每周日零点</el-tag>
          </div>
        </el-form-item>
        <el-form-item label="状态">
          <el-radio-group v-model="taskForm.status">
            <el-radio label="已启用" />
            <el-radio label="已禁用" />
          </el-radio-group>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSave">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="gitDialogVisible" :title="isGitEdit ? '编辑Git任务' : '新建Git任务'" width="700px">
      <el-form :model="gitTaskForm" label-width="100px">
        <el-form-item label="任务名称" required>
          <el-input v-model="gitTaskForm.name" placeholder="请输入任务名称" />
        </el-form-item>
        <el-form-item label="Git仓库地址" required>
          <el-input v-model="gitTaskForm.repo_url" placeholder="如: https://github.com/user/repo.git" />
        </el-form-item>
        <el-form-item label="分支名称">
          <el-input v-model="gitTaskForm.branch" placeholder="默认为main" />
        </el-form-item>
        <el-form-item label="认证方式">
          <el-radio-group v-model="gitTaskForm.auth_type">
            <el-radio label="none">无认证</el-radio>
            <el-radio label="https">HTTPS认证</el-radio>
            <el-radio label="ssh">SSH密钥</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item v-if="gitTaskForm.auth_type === 'https'" label="用户名">
          <el-input v-model="gitTaskForm.username" placeholder="Git用户名" />
        </el-form-item>
        <el-form-item v-if="gitTaskForm.auth_type === 'https'" label="密码/Token">
          <el-input v-model="gitTaskForm.password" type="password" placeholder="密码或访问令牌" show-password />
        </el-form-item>
        <el-form-item v-if="gitTaskForm.auth_type === 'ssh'" label="SSH密钥">
          <el-input v-model="gitTaskForm.ssh_key" type="textarea" :rows="4" placeholder="粘贴SSH私钥内容" />
        </el-form-item>
        <el-form-item label="脚本路径">
          <el-input v-model="gitTaskForm.script_path" placeholder="脚本所在目录，如: tests/api（留空为根目录）" />
        </el-form-item>
        <el-form-item label="运行命令" required>
          <el-input v-model="gitTaskForm.run_command" placeholder="如: pytest -v 或 python main.py" />
          <div class="cron-help">
            <el-icon :size="14"><component :is="icons.InfoFilled" /></el-icon>
            <span>在脚本路径下执行的命令</span>
          </div>
        </el-form-item>
        <el-form-item label="测试环境">
          <el-select v-model="gitTaskForm.environment_id" placeholder="选择环境（可选）" @change="handleGitEnvChange">
            <el-option v-for="env in environments" :key="env.id" :label="env.name" :value="env.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="定时规则">
          <el-input v-model="gitTaskForm.cron_expression" placeholder="Cron表达式，如 0 9 * * *" />
          <div class="cron-help">
            <el-icon :size="14"><component :is="icons.InfoFilled" /></el-icon>
            <span>留空为手动执行</span>
          </div>
        </el-form-item>
        <el-form-item label="状态">
          <el-radio-group v-model="gitTaskForm.status">
            <el-radio label="已启用" />
            <el-radio label="已禁用" />
          </el-radio-group>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="gitDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleGitSave">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="gitResultDialogVisible" title="执行结果" width="800px">
      <div v-if="gitExecuteResult" class="git-result">
        <div class="result-summary">
          <el-tag :type="gitExecuteResult.success ? 'success' : 'danger'" size="large">
            {{ gitExecuteResult.success ? '执行成功' : '执行失败' }}
          </el-tag>
          <span class="summary-item">耗时: {{ gitExecuteResult.report?.total_time || 0 }}ms</span>
        </div>
        
        <div v-if="gitExecuteResult.report" class="result-detail">
          <div class="detail-item">
            <span class="label">返回码:</span>
            <el-tag :type="gitExecuteResult.report.return_code === 0 ? 'success' : 'danger'" size="small">
              {{ gitExecuteResult.report.return_code }}
            </el-tag>
          </div>
          <div class="detail-item">
            <span class="label">工作目录:</span>
            <code>{{ gitExecuteResult.report.work_dir }}</code>
          </div>
          <div class="detail-item">
            <span class="label">执行命令:</span>
            <code>{{ gitExecuteResult.report.command }}</code>
          </div>
        </div>
        
        <div v-if="gitExecuteResult.report?.output" class="output-section">
          <div class="section-title">输出日志</div>
          <pre class="output-log">{{ gitExecuteResult.report.output }}</pre>
        </div>
        
        <div v-if="gitExecuteResult.report?.error" class="error-section">
          <div class="section-title">错误信息</div>
          <pre class="error-log">{{ gitExecuteResult.report.error }}</pre>
        </div>
      </div>
      
      <template #footer>
        <el-button @click="gitResultDialogVisible = false">关闭</el-button>
        <el-button type="primary" @click="viewGitReport">查看报告</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, reactive } from 'vue'
import * as icons from '@element-plus/icons-vue'

const activeTab = ref('api')
const searchKeyword = ref('')
const filterStatus = ref('')
const filterLastRun = ref('')
const currentPage = ref(1)

const apiTasks = ref([])
const gitTasks = ref([])
const scenarios = ref([])
const environments = ref([])
const selectedTasks = ref([])

const dialogVisible = ref(false)
const isEdit = ref(false)
const editingTask = ref(null)

const gitDialogVisible = ref(false)
const isGitEdit = ref(false)
const editingGitTask = ref(null)
const gitSearchKeyword = ref('')
const gitResultDialogVisible = ref(false)
const gitExecuteResult = ref(null)

const taskForm = reactive({
  name: '',
  scenario_id: '',
  scenario_name: '',
  environment_id: '',
  environment_name: '',
  cron_expression: '',
  status: '已启用'
})

const gitTaskForm = reactive({
  name: '',
  repo_url: '',
  branch: 'main',
  auth_type: 'none',
  username: '',
  password: '',
  ssh_key: '',
  script_path: '',
  run_command: 'pytest',
  environment_id: '',
  environment_name: '',
  cron_expression: '',
  status: '已启用'
})

const allSelectedEnabled = computed(() => {
  return selectedTasks.value.length > 0 && selectedTasks.value.every(t => t.status === '已启用')
})

const filteredTasks = computed(() => {
  let result = apiTasks.value
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    result = result.filter(t => t.name.toLowerCase().includes(keyword) || t.scenario_name.toLowerCase().includes(keyword))
  }
  if (filterStatus.value) {
    result = result.filter(t => t.status === filterStatus.value)
  }
  if (filterLastRun.value) {
    result = result.filter(t => t.last_run_status === filterLastRun.value)
  }
  return result
})

const filteredGitTasks = computed(() => {
  if (!gitSearchKeyword.value) return gitTasks.value
  const keyword = gitSearchKeyword.value.toLowerCase()
  return gitTasks.value.filter(t => t.name.toLowerCase().includes(keyword) || t.repo_url.toLowerCase().includes(keyword))
})

const loadTasks = async () => {
  try {
    const response = await fetch('/api/v1/tasks')
    const data = await response.json()
    apiTasks.value = data.tasks || []
  } catch (error) {
    console.error('加载任务列表失败:', error)
  }
}

const loadGitTasks = async () => {
  try {
    const response = await fetch('/api/v1/git-tasks')
    const data = await response.json()
    gitTasks.value = data.tasks || []
  } catch (error) {
    console.error('加载Git任务列表失败:', error)
  }
}

const loadScenarios = async () => {
  try {
    const response = await fetch('/api/v1/scenarios')
    const data = await response.json()
    scenarios.value = data.scenarios || []
  } catch (error) {
    console.error('加载场景列表失败:', error)
  }
}

const loadEnvironments = async () => {
  try {
    const response = await fetch('/api/v1/environments')
    const data = await response.json()
    environments.value = data.environments || []
  } catch (error) {
    console.error('加载环境列表失败:', error)
  }
}

const resetForm = () => {
  taskForm.name = ''
  taskForm.scenario_id = ''
  taskForm.scenario_name = ''
  taskForm.environment_id = ''
  taskForm.environment_name = ''
  taskForm.cron_expression = ''
  taskForm.status = '已启用'
}

const resetGitForm = () => {
  gitTaskForm.name = ''
  gitTaskForm.repo_url = ''
  gitTaskForm.branch = 'main'
  gitTaskForm.auth_type = 'none'
  gitTaskForm.username = ''
  gitTaskForm.password = ''
  gitTaskForm.ssh_key = ''
  gitTaskForm.script_path = ''
  gitTaskForm.run_command = 'pytest'
  gitTaskForm.environment_id = ''
  gitTaskForm.environment_name = ''
  gitTaskForm.cron_expression = ''
  gitTaskForm.status = '已启用'
}

const handleSelectionChange = (val) => {
  selectedTasks.value = val
}

const handleAdd = () => {
  isEdit.value = false
  editingTask.value = null
  resetForm()
  dialogVisible.value = true
}

const handleEdit = (row) => {
  isEdit.value = true
  editingTask.value = row
  taskForm.name = row.name
  taskForm.scenario_id = row.scenario_id
  taskForm.scenario_name = row.scenario_name
  taskForm.environment_id = row.environment_id
  taskForm.environment_name = row.environment_name
  taskForm.cron_expression = row.cron_expression
  taskForm.status = row.status
  dialogVisible.value = true
}

const handleScenarioChange = () => {
  const scenario = scenarios.value.find(s => s.id === taskForm.scenario_id)
  taskForm.scenario_name = scenario ? scenario.name : ''
}

const handleEnvChange = () => {
  const env = environments.value.find(e => e.id === taskForm.environment_id)
  taskForm.environment_name = env ? env.name : ''
}

const handleGitEnvChange = () => {
  const env = environments.value.find(e => e.id === gitTaskForm.environment_id)
  gitTaskForm.environment_name = env ? env.name : ''
}

const handleExecute = async (row) => {
  if (!confirm(`确定要执行任务「${row.name}」吗？`)) return
  
  try {
    const response = await fetch(`/api/v1/tasks/${row.id}/execute`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' }
    })
    
    const data = await response.json()
    if (data.success) {
      alert('任务执行完成')
      loadTasks()
      
      const goToReport = confirm('执行报告已生成，是否查看报告？')
      if (goToReport) {
        window.location.href = '/#/interface-reports'
      }
    } else {
      alert(data.message)
    }
  } catch (error) {
    console.error('执行任务失败:', error)
    alert('执行任务失败')
  }
}

const handleBatchExecute = async () => {
  if (!confirm(`确定要批量执行选中的 ${selectedTasks.value.length} 个任务吗？`)) return
  
  let successCount = 0
  let failCount = 0
  
  for (const task of selectedTasks.value) {
    try {
      const response = await fetch(`/api/v1/tasks/${task.id}/execute`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      })
      const data = await response.json()
      if (data.success) {
        successCount++
      } else {
        failCount++
      }
    } catch {
      failCount++
    }
  }
  
  alert(`批量执行完成：成功 ${successCount} 个，失败 ${failCount} 个`)
  loadTasks()
}

const handleToggleStatus = async (row) => {
  const newStatus = row.status === '已启用' ? '已禁用' : '已启用'
  try {
    const response = await fetch(`/api/v1/tasks/${row.id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status: newStatus })
    })
    
    const data = await response.json()
    if (data.success) {
      alert(data.message)
      loadTasks()
    }
  } catch (error) {
    console.error('修改任务状态失败:', error)
    alert('修改失败')
  }
}

const handleBatchToggle = async () => {
  const newStatus = allSelectedEnabled.value ? '已禁用' : '已启用'
  if (!confirm(`确定要批量${newStatus}选中的 ${selectedTasks.value.length} 个任务吗？`)) return
  
  for (const task of selectedTasks.value) {
    try {
      await fetch(`/api/v1/tasks/${task.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status: newStatus })
      })
    } catch {}
  }
  
  alert(`成功批量${newStatus} ${selectedTasks.value.length} 个任务`)
  loadTasks()
}

const handleDelete = async (row) => {
  if (!confirm(`确定要删除任务「${row.name}」吗？`)) return
  
  try {
    const response = await fetch(`/api/v1/tasks/${row.id}`, {
      method: 'DELETE'
    })
    
    const data = await response.json()
    if (data.success) {
      alert(data.message)
      loadTasks()
    }
  } catch (error) {
    console.error('删除任务失败:', error)
    alert('删除失败')
  }
}

const handleBatchDelete = async () => {
  if (!confirm(`确定要删除选中的 ${selectedTasks.value.length} 个任务吗？此操作不可恢复。`)) return
  
  for (const task of selectedTasks.value) {
    try {
      await fetch(`/api/v1/tasks/${task.id}`, {
        method: 'DELETE'
      })
    } catch {}
  }
  
  alert(`成功删除 ${selectedTasks.value.length} 个任务`)
  loadTasks()
}

const handleSave = async () => {
  if (!taskForm.name || !taskForm.scenario_id || !taskForm.environment_id) {
    alert('任务名称、场景和环境不能为空')
    return
  }
  
  const scenario = scenarios.value.find(s => s.id === taskForm.scenario_id)
  const env = environments.value.find(e => e.id === taskForm.environment_id)
  
  taskForm.scenario_name = scenario ? scenario.name : ''
  taskForm.environment_name = env ? env.name : ''
  
  try {
    const url = isEdit.value ? `/api/v1/tasks/${editingTask.value.id}` : '/api/v1/tasks'
    const method = isEdit.value ? 'PUT' : 'POST'
    
    const response = await fetch(url, {
      method: method,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(taskForm)
    })
    
    const data = await response.json()
    if (data.success) {
      alert(data.message)
      dialogVisible.value = false
      loadTasks()
    }
  } catch (error) {
    console.error('保存任务失败:', error)
    alert('保存失败')
  }
}

const handleGitAdd = () => {
  isGitEdit.value = false
  editingGitTask.value = null
  resetGitForm()
  gitDialogVisible.value = true
}

const handleGitEdit = (row) => {
  isGitEdit.value = true
  editingGitTask.value = row
  gitTaskForm.name = row.name
  gitTaskForm.repo_url = row.repo_url
  gitTaskForm.branch = row.branch
  gitTaskForm.auth_type = row.auth_type
  gitTaskForm.username = row.username
  gitTaskForm.password = row.password
  gitTaskForm.ssh_key = row.ssh_key
  gitTaskForm.script_path = row.script_path
  gitTaskForm.run_command = row.run_command
  gitTaskForm.environment_id = row.environment_id
  gitTaskForm.environment_name = row.environment_name
  gitTaskForm.cron_expression = row.cron_expression
  gitTaskForm.status = row.status
  gitDialogVisible.value = true
}

const handleGitPull = async (row) => {
  try {
    const response = await fetch(`/api/v1/git-tasks/${row.id}/pull`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' }
    })
    
    const data = await response.json()
    alert(data.message)
    if (data.success) {
      loadGitTasks()
    }
  } catch (error) {
    console.error('拉取代码失败:', error)
    alert('拉取代码失败')
  }
}

const handleGitExecute = async (row) => {
  if (!confirm(`确定要执行Git任务「${row.name}」吗？\n将先拉取最新代码，然后运行脚本。`)) return
  
  try {
    const response = await fetch(`/api/v1/git-tasks/${row.id}/execute`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' }
    })
    
    const data = await response.json()
    gitExecuteResult.value = data
    gitResultDialogVisible.value = true
    loadGitTasks()
  } catch (error) {
    console.error('执行Git任务失败:', error)
    alert('执行Git任务失败')
  }
}

const handleGitDelete = async (row) => {
  if (!confirm(`确定要删除Git任务「${row.name}」吗？`)) return
  
  try {
    const response = await fetch(`/api/v1/git-tasks/${row.id}`, {
      method: 'DELETE'
    })
    
    const data = await response.json()
    if (data.success) {
      alert(data.message)
      loadGitTasks()
    }
  } catch (error) {
    console.error('删除Git任务失败:', error)
    alert('删除失败')
  }
}

const handleGitSave = async () => {
  if (!gitTaskForm.name || !gitTaskForm.repo_url || !gitTaskForm.run_command) {
    alert('任务名称、仓库地址和运行命令不能为空')
    return
  }
  
  try {
    const url = isGitEdit.value ? `/api/v1/git-tasks/${editingGitTask.value.id}` : '/api/v1/git-tasks'
    const method = isGitEdit.value ? 'PUT' : 'POST'
    
    const response = await fetch(url, {
      method: method,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(gitTaskForm)
    })
    
    const data = await response.json()
    if (data.success) {
      alert(data.message)
      gitDialogVisible.value = false
      loadGitTasks()
    }
  } catch (error) {
    console.error('保存Git任务失败:', error)
    alert('保存失败')
  }
}

const viewGitReport = () => {
  gitResultDialogVisible.value = false
  window.location.href = '/#/interface-reports'
}

loadTasks()
loadGitTasks()
loadScenarios()
loadEnvironments()
</script>

<style scoped>
.api-tasks { padding: 20px; }

.page-header { margin-bottom: 24px; }
.page-header h2 { font-size: 24px; font-weight: 600; color: #1f2937; margin-bottom: 4px; }
.page-desc { font-size: 14px; color: #6b7280; }

.tab-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.header-actions { display: flex; gap: 8px; }

.filter-bar { display: flex; gap: 12px; margin-bottom: 16px; }
.search-input { width: 250px; }

.text-gray { color: #9ca3af; }

.empty-state {
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  padding: 60px; color: #9ca3af; gap: 12px;
}
.empty-icon { color: #c0c4cc; }

.cron-help { display: flex; align-items: center; gap: 4px; margin-top: 8px; font-size: 12px; color: #6b7280; }
.cron-examples { display: flex; gap: 8px; margin-top: 8px; }
.cron-examples .el-tag { cursor: pointer; }

.repo-url {
  display: inline-block;
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.git-result { padding: 16px; }
.result-summary { display: flex; align-items: center; gap: 16px; margin-bottom: 20px; }
.summary-item { font-size: 14px; color: #6b7280; }

.result-detail { margin-bottom: 20px; }
.detail-item { display: flex; align-items: center; gap: 8px; margin-bottom: 8px; }
.detail-item .label { font-weight: 500; color: #374151; min-width: 80px; }

.output-section, .error-section { margin-top: 16px; }
.section-title { font-weight: 600; color: #374151; margin-bottom: 8px; }
.output-log, .error-log {
  background: #1f2937;
  color: #10b981;
  padding: 12px;
  border-radius: 4px;
  font-size: 12px;
  max-height: 300px;
  overflow-y: auto;
  white-space: pre-wrap;
  word-break: break-all;
}
.error-log { color: #ef4444; }

.pagination { display: flex; justify-content: flex-end; margin-top: 16px; }
</style>