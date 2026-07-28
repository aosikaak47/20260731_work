<template>
  <div class="api-reports">
    <div class="page-header">
      <h2>接口执行报告</h2>
      <p class="page-desc">查看接口自动化测试执行报告</p>
    </div>
    
    <el-card>
      <template #header>
        <div class="card-header">
          <span class="card-title">报告列表</span>
          <div class="header-actions">
            <el-select v-model="filterStatus" size="small" placeholder="执行结果">
              <el-option label="全部" value="" />
              <el-option label="成功" value="成功" />
              <el-option label="失败" value="失败" />
            </el-select>
            <el-input 
              v-model="searchKeyword" 
              placeholder="搜索场景名称..." 
              size="small"
              class="search-input"
              @keyup.enter="loadReports"
            >
              <template #prefix>
                <el-icon><component :is="icons.Search" /></el-icon>
              </template>
            </el-input>
          </div>
        </div>
      </template>
      
      <div v-if="filteredReports.length === 0" class="empty-state">
        <el-icon :size="48" class="empty-icon"><component :is="icons.Box" /></el-icon>
        <span>暂无执行报告</span>
        <el-button size="small" type="primary" @click="goToExecute">去执行任务</el-button>
      </div>
      
      <el-table v-else :data="filteredReports" stripe border>
        <el-table-column type="selection" width="50" />
        <el-table-column label="编号" width="60">
          <template #default="scope">{{ scope.$index + 1 }}</template>
        </el-table-column>
        <el-table-column prop="scenario_name" label="场景名称" min-width="150" />
        <el-table-column prop="environment_name" label="测试环境" width="120" />
        <el-table-column prop="status" label="执行结果" width="100">
          <template #default="scope">
            <el-tag :type="scope.row.status === '成功' ? 'success' : 'danger'">{{ scope.row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="total_steps" label="总步骤" width="80" />
        <el-table-column prop="passed_steps" label="通过" width="80">
          <template #default="scope">
            <span class="passed-count">{{ scope.row.passed_steps }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="failed_steps" label="失败" width="80">
          <template #default="scope">
            <span class="failed-count">{{ scope.row.failed_steps }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="total_time" label="耗时(ms)" width="100" />
        <el-table-column prop="start_time" label="执行时间" width="160" />
        <el-table-column label="操作" width="200" class-name="action-cell">
          <template #default="scope">
            <div class="action-btns">
              <el-button size="small" @click="handleView(scope.row)">查看</el-button>
              <el-button size="small" @click="handleExport(scope.row)">导出</el-button>
              <el-button size="small" type="danger" @click="handleDelete(scope.row)">删除</el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>
      
      <el-pagination
        v-if="filteredReports.length > 0"
        class="pagination"
        layout="total, prev, pager, next"
        :total="filteredReports.length"
        :page-size="10"
        v-model:current-page="currentPage"
      />
    </el-card>

    <el-dialog v-model="detailDialogVisible" title="报告详情" width="900px">
      <div class="report-detail" v-if="currentReport">
        <div class="detail-header">
          <div class="header-left">
            <h3>{{ currentReport.scenario_name }}</h3>
            <span class="env-tag">{{ currentReport.environment_name }}</span>
          </div>
          <div class="header-right">
            <el-tag :type="currentReport.status === '成功' ? 'success' : 'danger'" size="large">
              {{ currentReport.status }}
            </el-tag>
          </div>
        </div>
        
        <div class="summary-stats">
          <div class="stat-item">
            <span class="stat-value">{{ currentReport.total_steps }}</span>
            <span class="stat-label">总步骤</span>
          </div>
          <div class="stat-item success">
            <span class="stat-value">{{ currentReport.passed_steps }}</span>
            <span class="stat-label">通过</span>
          </div>
          <div class="stat-item danger">
            <span class="stat-value">{{ currentReport.failed_steps }}</span>
            <span class="stat-label">失败</span>
          </div>
          <div class="stat-item">
            <span class="stat-value">{{ currentReport.total_time }}</span>
            <span class="stat-label">总耗时(ms)</span>
          </div>
        </div>
        
        <div class="detail-info">
          <div class="info-row">
            <span class="info-label">执行时间:</span>
            <span>{{ currentReport.start_time }}</span>
          </div>
          <div class="info-row">
            <span class="info-label">结束时间:</span>
            <span>{{ currentReport.end_time }}</span>
          </div>
        </div>
        
        <div class="steps-section">
          <h4>步骤执行详情</h4>
          <div v-for="(result, index) in currentReport.steps" :key="index" class="step-detail">
            <div class="step-header">
              <span class="step-number">{{ index + 1 }}</span>
              <span class="step-name">{{ result.step.name }}</span>
              <el-tag :type="result.skipped ? 'info' : (result.passed ? 'success' : 'danger')" size="small">
                {{ result.skipped ? '跳过' : (result.passed ? '通过' : '失败') }}
              </el-tag>
              <span class="step-time">{{ result.time }}ms</span>
            </div>
            
            <div v-if="result.error" class="step-error">
              <el-icon><component :is="icons.Warning" /></el-icon>
              <span>{{ result.error }}</span>
            </div>
            
            <div v-if="result.response" class="step-response">
              <div class="response-tabs">
                <el-tabs v-model="activeTab[index]">
                  <el-tab-pane label="请求" name="request">
                    <pre class="response-content">{{ JSON.stringify({ method: result.step.method, url: result.step.url }, null, 2) }}</pre>
                  </el-tab-pane>
                  <el-tab-pane label="响应" name="response">
                    <pre class="response-content">{{ typeof result.response.body === 'object' ? JSON.stringify(result.response.body, null, 2) : result.response.body }}</pre>
                  </el-tab-pane>
                  <el-tab-pane label="断言" name="assertions">
                    <el-table :data="result.assertions" border size="small">
                      <el-table-column prop="assertion.type" label="类型" width="100" />
                      <el-table-column prop="assertion.field" label="字段" min-width="150" />
                      <el-table-column prop="assertion.operator" label="操作符" width="80" />
                      <el-table-column prop="assertion.expected" label="期望值" width="100" />
                      <el-table-column prop="actual" label="实际值" width="100" />
                      <el-table-column label="结果" width="80">
                        <template #default="scope">
                          <el-tag :type="scope.row.passed ? 'success' : 'danger'" size="small">
                            {{ scope.row.passed ? '通过' : '失败' }}
                          </el-tag>
                        </template>
                      </el-table-column>
                    </el-table>
                    <div v-if="result.assertions.length === 0" class="no-assertions">
                      无断言配置
                    </div>
                  </el-tab-pane>
                </el-tabs>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <template #footer>
        <el-button @click="detailDialogVisible = false">关闭</el-button>
        <el-button type="primary" @click="handleExport(currentReport)">导出报告</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, reactive } from 'vue'
import * as icons from '@element-plus/icons-vue'

const searchKeyword = ref('')
const filterStatus = ref('')
const currentPage = ref(1)

const reports = ref([])
const detailDialogVisible = ref(false)
const currentReport = ref(null)
const activeTab = reactive({})

const filteredReports = computed(() => {
  let result = reports.value
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    result = result.filter(r => r.scenario_name.toLowerCase().includes(keyword))
  }
  if (filterStatus.value) {
    result = result.filter(r => r.status === filterStatus.value)
  }
  return result
})

const loadReports = async () => {
  try {
    const response = await fetch('/api/v1/reports')
    const data = await response.json()
    reports.value = data.reports || []
  } catch (error) {
    console.error('加载报告列表失败:', error)
  }
}

const handleView = (report) => {
  currentReport.value = report
  detailDialogVisible.value = true
  
  report.steps.forEach((_, index) => {
    activeTab[index] = 'request'
  })
}

const handleExport = async (report) => {
  try {
    const response = await fetch(`/api/v1/reports/${report.id}/export`, {
      method: 'POST'
    })
    
    if (response.ok) {
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `report_${report.id}.json`
      a.click()
      window.URL.revokeObjectURL(url)
      alert('报告导出成功')
    } else {
      alert('导出失败')
    }
  } catch (error) {
    console.error('导出报告失败:', error)
    alert('导出失败')
  }
}

const handleDelete = async (report) => {
  if (!confirm(`确定要删除报告「${report.scenario_name}」吗？`)) return
  
  try {
    const response = await fetch(`/api/v1/reports/${report.id}`, {
      method: 'DELETE'
    })
    
    const data = await response.json()
    if (data.success) {
      alert(data.message)
      loadReports()
    }
  } catch (error) {
    console.error('删除报告失败:', error)
    alert('删除失败')
  }
}

const goToExecute = () => {
  window.location.href = '/#/interface-tasks'
}

loadReports()
</script>

<style scoped>
.api-reports { padding: 20px; }

.page-header { margin-bottom: 24px; }
.page-header h2 { font-size: 24px; font-weight: 600; color: #1f2937; margin-bottom: 4px; }
.page-desc { font-size: 14px; color: #6b7280; }

.card-header { display: flex; align-items: center; justify-content: space-between; }
.card-title { font-size: 16px; font-weight: 600; }
.header-actions { display: flex; gap: 12px; }
.search-input { width: 200px; }

.empty-state {
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  padding: 60px; color: #9ca3af; gap: 12px;
}
.empty-icon { color: #c0c4cc; }

.passed-count { color: #10b981; font-weight: 600; }
.failed-count { color: #ef4444; font-weight: 600; }

.pagination { display: flex; justify-content: flex-end; margin-top: 16px; }

.report-detail { padding: 8px; }

.detail-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.header-left { display: flex; align-items: center; gap: 12px; }
.header-left h3 { font-size: 18px; font-weight: 600; }
.env-tag { background-color: #e0e7ff; color: #4338ca; padding: 4px 12px; border-radius: 4px; font-size: 13px; }

.summary-stats {
  display: flex; gap: 24px; padding: 16px; background-color: #f9fafb; border-radius: 8px;
  margin-bottom: 16px;
}
.stat-item { display: flex; flex-direction: column; align-items: center; }
.stat-item .stat-value { font-size: 24px; font-weight: 700; color: #374151; }
.stat-item.success .stat-value { color: #10b981; }
.stat-item.danger .stat-value { color: #ef4444; }
.stat-item .stat-label { font-size: 12px; color: #6b7280; margin-top: 4px; }

.detail-info { margin-bottom: 16px; padding: 12px; background-color: #f9fafb; border-radius: 8px; }
.info-row { display: flex; gap: 8px; margin-bottom: 4px; font-size: 14px; }
.info-label { color: #6b7280; }

.steps-section { margin-top: 20px; }
.steps-section h4 { font-size: 16px; font-weight: 600; margin-bottom: 12px; }

.step-detail {
  background-color: #f9fafb; border-radius: 8px; padding: 12px; margin-bottom: 12px;
  border: 1px solid #e5e7eb;
}
.step-header { display: flex; align-items: center; gap: 8px; margin-bottom: 12px; }
.step-number {
  width: 24px; height: 24px; border-radius: 50%; background-color: #6366f1;
  color: white; font-size: 12px; display: flex; align-items: center; justify-content: center;
}
.step-name { flex: 1; font-weight: 500; }
.step-time { font-size: 12px; color: #6b7280; font-family: monospace; }

.step-error {
  display: flex; align-items: center; gap: 8px; padding: 12px;
  background-color: #fef2f2; border-radius: 4px; color: #ef4444; font-size: 13px;
}

.response-tabs { margin-top: 8px; }
.response-content {
  background-color: #1f2937; color: #e5e7eb; padding: 12px; border-radius: 4px;
  font-family: monospace; font-size: 12px; max-height: 300px; overflow-y: auto;
  white-space: pre-wrap; word-break: break-all;
}

.no-assertions { text-align: center; padding: 20px; color: #9ca3af; font-size: 14px; }
</style>