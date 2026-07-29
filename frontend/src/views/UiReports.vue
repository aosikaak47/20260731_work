<template>
  <div class="ui-reports">
    <div class="page-header">
      <h2>UI执行报告</h2>
      <p class="page-desc">查看UI自动化测试执行报告</p>
    </div>

    <el-row :gutter="16" class="stats-row">
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-icon total">
              <el-icon :size="24"><component :is="icons.Document" /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ reports.length }}</div>
              <div class="stat-label">总报告数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-icon success">
              <el-icon :size="24"><component :is="icons.CircleCheck" /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ totalPassed }}</div>
              <div class="stat-label">通过步骤</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-icon danger">
              <el-icon :size="24"><component :is="icons.CircleClose" /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ totalFailed }}</div>
              <div class="stat-label">失败步骤</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-icon rate">
              <el-icon :size="24"><component :is="icons.TrendCharts" /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ passRate }}%</div>
              <div class="stat-label">通过率</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-card>
      <template #header>
        <div class="card-header">
          <span class="card-title">报告列表</span>
          <div class="header-actions">
            <el-select v-model="filterProject" size="small" placeholder="全部项目" clearable class="filter-select">
              <el-option v-for="p in projectOptions" :key="p" :label="p" :value="p" />
            </el-select>
            <el-select v-model="filterStatus" size="small" placeholder="执行结果" clearable class="filter-select">
              <el-option label="成功" value="success" />
              <el-option label="失败" value="failed" />
            </el-select>
            <el-input
              v-model="searchKeyword"
              placeholder="搜索报告名称..."
              size="small"
              class="search-input"
              @keyup.enter="loadReports"
            >
              <template #prefix>
                <el-icon><component :is="icons.Search" /></el-icon>
              </template>
            </el-input>
            <el-button size="small" type="primary" @click="loadReports">
              <el-icon><component :is="icons.Refresh" /></el-icon>
              <span class="btn-text">刷新</span>
            </el-button>
          </div>
        </div>
      </template>

      <div v-if="loading" class="loading-state">
        <el-icon :size="32" class="is-loading"><component :is="icons.Loading" /></el-icon>
        <span>加载中...</span>
      </div>

      <div v-else-if="filteredReports.length === 0" class="empty-state">
        <el-icon :size="48" class="empty-icon"><component :is="icons.Box" /></el-icon>
        <span>暂无执行报告</span>
      </div>

      <el-table v-else :data="pagedReports" stripe border v-loading="loading">
        <el-table-column label="编号" width="60">
          <template #default="scope">{{ (currentPage - 1) * pageSize + scope.$index + 1 }}</template>
        </el-table-column>
        <el-table-column prop="name" label="报告名称" min-width="180" show-overflow-tooltip />
        <el-table-column prop="project" label="所属项目" width="140" />
        <el-table-column prop="case_name" label="用例名称" min-width="160" show-overflow-tooltip />
        <el-table-column prop="status" label="执行结果" width="100">
          <template #default="scope">
            <el-tag :type="scope.row.status === 'success' ? 'success' : 'danger'">
              {{ scope.row.status === 'success' ? '成功' : '失败' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="total_steps" label="总步骤" width="80" align="center" />
        <el-table-column prop="passed_steps" label="通过" width="80" align="center">
          <template #default="scope">
            <span class="passed-count">{{ scope.row.passed_steps }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="failed_steps" label="失败" width="80" align="center">
          <template #default="scope">
            <span class="failed-count">{{ scope.row.failed_steps }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="duration" label="耗时(ms)" width="100" align="center" />
        <el-table-column prop="created_at" label="执行时间" width="160" />
        <el-table-column label="操作" width="200" fixed="right" class-name="action-cell">
          <template #default="scope">
            <div class="action-btns">
              <el-button size="small" type="primary" @click="handleView(scope.row)">
                <el-icon><component :is="icons.View" /></el-icon>
                <span>查看</span>
              </el-button>
              <el-button size="small" type="danger" @click="handleDelete(scope.row)">
                <el-icon><component :is="icons.Delete" /></el-icon>
                <span>删除</span>
              </el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-if="filteredReports.length > 0"
        class="pagination"
        layout="total, sizes, prev, pager, next, jumper"
        :total="filteredReports.length"
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[10, 20, 50]"
      />
    </el-card>

    <el-dialog v-model="detailDialogVisible" title="报告详情" width="960px" destroy-on-close>
      <div class="report-detail" v-if="currentReport">
        <div class="detail-header">
          <div class="header-left">
            <h3>{{ currentReport.name || 'UI 测试报告' }}</h3>
            <el-tag type="info" size="small">{{ currentReport.project }}</el-tag>
            <el-tag :type="currentReport.status === 'success' ? 'success' : 'danger'" size="large">
              {{ currentReport.status === 'success' ? '成功' : '失败' }}
            </el-tag>
          </div>
        </div>

        <div class="summary-stats">
          <div class="stat-item">
            <span class="stat-value">{{ currentReport.total_steps || 0 }}</span>
            <span class="stat-label">总步骤</span>
          </div>
          <div class="stat-item success">
            <span class="stat-value">{{ currentReport.passed_steps || 0 }}</span>
            <span class="stat-label">通过</span>
          </div>
          <div class="stat-item danger">
            <span class="stat-value">{{ currentReport.failed_steps || 0 }}</span>
            <span class="stat-label">失败</span>
          </div>
          <div class="stat-item">
            <span class="stat-value">{{ currentReport.duration || 0 }}</span>
            <span class="stat-label">总耗时(ms)</span>
          </div>
          <div class="stat-item">
            <span class="stat-value">{{ currentReport.pass_rate || 0 }}%</span>
            <span class="stat-label">通过率</span>
          </div>
        </div>

        <div class="detail-info">
          <div class="info-row">
            <span class="info-label">用例名称:</span>
            <span>{{ currentReport.case_name || '-' }}</span>
          </div>
          <div class="info-row">
            <span class="info-label">执行时间:</span>
            <span>{{ currentReport.created_at || '-' }}</span>
          </div>
          <div class="info-row" v-if="currentReport.error_message">
            <span class="info-label">错误信息:</span>
            <span class="error-msg">{{ currentReport.error_message }}</span>
          </div>
        </div>

        <div class="steps-section" v-if="currentReport.steps && currentReport.steps.length">
          <h4>步骤执行详情</h4>
          <div v-for="(step, index) in currentReport.steps" :key="index" class="step-detail">
            <div class="step-header">
              <span class="step-number">{{ index + 1 }}</span>
              <span class="step-name">{{ step.name || step.action_name || '未命名步骤' }}</span>
              <el-tag :type="step.passed === false ? 'danger' : 'success'" size="small">
                {{ step.passed === false ? '失败' : '通过' }}
              </el-tag>
              <span class="step-time">{{ (step.duration || 0) }}ms</span>
            </div>
            <div v-if="step.error" class="step-error">
              <el-icon><component :is="icons.Warning" /></el-icon>
              <span>{{ step.error }}</span>
            </div>
            <div v-if="step.screenshot" class="step-screenshot">
              <img :src="step.screenshot" :alt="step.name" class="screenshot-thumb" @click="previewImage(step.screenshot)" />
            </div>
          </div>
        </div>
        <div v-else class="no-steps">暂无步骤详情</div>
      </div>

      <template #footer>
        <el-button @click="detailDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="previewVisible" title="截图预览" width="800px" align-center>
      <div class="image-preview">
        <img v-if="previewImageUrl" :src="previewImageUrl" alt="preview" class="preview-img" />
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import * as icons from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const loading = ref(false)
const reports = ref([])
const searchKeyword = ref('')
const filterProject = ref('')
const filterStatus = ref('')
const currentPage = ref(1)
const pageSize = ref(10)

const detailDialogVisible = ref(false)
const currentReport = ref(null)
const previewVisible = ref(false)
const previewImageUrl = ref('')

const projectOptions = computed(() => {
  const set = new Set()
  reports.value.forEach(r => r.project && set.add(r.project))
  return Array.from(set)
})

const filteredReports = computed(() => {
  let result = reports.value
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    result = result.filter(r =>
      (r.name || '').toLowerCase().includes(keyword) ||
      (r.case_name || '').toLowerCase().includes(keyword)
    )
  }
  if (filterProject.value) {
    result = result.filter(r => r.project === filterProject.value)
  }
  if (filterStatus.value) {
    result = result.filter(r => r.status === filterStatus.value)
  }
  return result
})

const pagedReports = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  return filteredReports.value.slice(start, start + pageSize.value)
})

const totalPassed = computed(() =>
  reports.value.reduce((sum, r) => sum + (r.passed_steps || 0), 0)
)
const totalFailed = computed(() =>
  reports.value.reduce((sum, r) => sum + (r.failed_steps || 0), 0)
)
const passRate = computed(() => {
  const total = totalPassed.value + totalFailed.value
  if (total === 0) return 0
  return ((totalPassed.value / total) * 100).toFixed(1)
})

const loadReports = async () => {
  loading.value = true
  try {
    const response = await fetch('/api/v1/ui/reports')
    const data = await response.json()
    reports.value = data.reports || data.data || data.items || []
  } catch (error) {
    console.error('加载UI报告列表失败:', error)
    ElMessage.error('加载报告列表失败')
  } finally {
    loading.value = false
  }
}

const handleView = async (report) => {
  currentReport.value = report
  detailDialogVisible.value = true

  if (!report.steps) {
    try {
      const response = await fetch(`/api/v1/ui/reports/${report.id}`)
      const data = await response.json()
      currentReport.value = data.report || data.data || data
    } catch (error) {
      console.error('加载报告详情失败:', error)
    }
  }
}

const handleDelete = async (report) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除报告「${report.name || report.case_name}」吗？删除后不可恢复。`,
      '删除确认',
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
  } catch {
    return
  }

  try {
    const response = await fetch(`/api/v1/ui/reports/${report.id}`, {
      method: 'DELETE'
    })
    const data = await response.json()
    if (response.ok && (data.success === undefined || data.success === true)) {
      ElMessage.success('删除成功')
      loadReports()
    } else {
      ElMessage.error(data.message || '删除失败')
    }
  } catch (error) {
    console.error('删除报告失败:', error)
    ElMessage.error('删除失败')
  }
}

const previewImage = (url) => {
  previewImageUrl.value = url
  previewVisible.value = true
}

onMounted(() => {
  loadReports()
})
</script>

<style scoped>
.ui-reports { padding: 20px; }

.page-header { margin-bottom: 24px; }
.page-header h2 { font-size: 24px; font-weight: 600; color: #1f2937; margin-bottom: 4px; }
.page-desc { font-size: 14px; color: #6b7280; }

.stats-row { margin-bottom: 16px; }
.stat-card { height: 100%; }
.stat-card :deep(.el-card__body) { padding: 20px; }
.stat-content { display: flex; align-items: center; gap: 16px; }
.stat-icon {
  width: 56px; height: 56px; border-radius: 12px;
  display: flex; align-items: center; justify-content: center;
  color: #fff;
}
.stat-icon.total { background: linear-gradient(135deg, #6366f1, #8b5cf6); }
.stat-icon.success { background: linear-gradient(135deg, #10b981, #34d399); }
.stat-icon.danger { background: linear-gradient(135deg, #ef4444, #f87171); }
.stat-icon.rate { background: linear-gradient(135deg, #f59e0b, #fbbf24); }
.stat-info .stat-value { font-size: 24px; font-weight: 700; color: #1f2937; line-height: 1.2; }
.stat-info .stat-label { font-size: 13px; color: #6b7280; margin-top: 4px; }

.card-header { display: flex; align-items: center; justify-content: space-between; }
.card-title { font-size: 16px; font-weight: 600; }
.header-actions { display: flex; gap: 12px; align-items: center; }
.filter-select { width: 140px; }
.search-input { width: 220px; }
.btn-text { margin-left: 4px; }

.loading-state {
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  padding: 60px; color: #9ca3af; gap: 12px;
}
.loading-state .is-loading { color: #6366f1; }

.empty-state {
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  padding: 60px; color: #9ca3af; gap: 12px;
}
.empty-icon { color: #c0c4cc; }

.passed-count { color: #10b981; font-weight: 600; }
.failed-count { color: #ef4444; font-weight: 600; }

.action-btns { display: flex; gap: 6px; }
.action-btns .el-button span { margin-left: 4px; }

.pagination { display: flex; justify-content: flex-end; margin-top: 16px; }

.report-detail { padding: 8px; }
.detail-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.header-left { display: flex; align-items: center; gap: 12px; }
.header-left h3 { font-size: 18px; font-weight: 600; margin: 0; }

.summary-stats {
  display: flex; gap: 24px; padding: 16px; background-color: #f9fafb; border-radius: 8px;
  margin-bottom: 16px;
}
.stat-item { display: flex; flex-direction: column; align-items: center; flex: 1; }
.stat-item .stat-value { font-size: 22px; font-weight: 700; color: #374151; }
.stat-item.success .stat-value { color: #10b981; }
.stat-item.danger .stat-value { color: #ef4444; }
.stat-item .stat-label { font-size: 12px; color: #6b7280; margin-top: 4px; }

.detail-info { margin-bottom: 16px; padding: 12px; background-color: #f9fafb; border-radius: 8px; }
.info-row { display: flex; gap: 8px; margin-bottom: 6px; font-size: 14px; }
.info-row:last-child { margin-bottom: 0; }
.info-label { color: #6b7280; min-width: 90px; }
.error-msg { color: #ef4444; word-break: break-all; }

.steps-section { margin-top: 16px; }
.steps-section h4 { font-size: 16px; font-weight: 600; margin-bottom: 12px; }

.step-detail {
  background-color: #fff; border-radius: 8px; padding: 12px; margin-bottom: 12px;
  border: 1px solid #e5e7eb;
}
.step-header { display: flex; align-items: center; gap: 8px; margin-bottom: 8px; }
.step-number {
  width: 24px; height: 24px; border-radius: 50%; background-color: #6366f1;
  color: white; font-size: 12px; display: flex; align-items: center; justify-content: center;
}
.step-name { flex: 1; font-weight: 500; }
.step-time { font-size: 12px; color: #6b7280; font-family: monospace; }

.step-error {
  display: flex; align-items: center; gap: 8px; padding: 10px;
  background-color: #fef2f2; border-radius: 4px; color: #ef4444; font-size: 13px;
}

.step-screenshot { margin-top: 8px; }
.screenshot-thumb {
  max-width: 200px; max-height: 120px; border-radius: 6px;
  cursor: pointer; border: 1px solid #e5e7eb;
  transition: transform 0.2s;
}
.screenshot-thumb:hover { transform: scale(1.03); }

.no-steps { text-align: center; padding: 24px; color: #9ca3af; }

.image-preview { display: flex; justify-content: center; }
.preview-img { max-width: 100%; max-height: 70vh; border-radius: 8px; }
</style>
