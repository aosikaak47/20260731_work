<template>
  <div class="export-container">
    <el-card>
      <template #header>
        <h2>导出测试用例</h2>
      </template>
      
      <div v-if="!testCases.length" class="empty-state">
        <el-icon size="64" color="#c0c4cc"><component :is="icons.Download" /></el-icon>
        <p>暂无测试用例可导出</p>
        <el-button type="primary" @click="goToUpload">去生成测试用例</el-button>
      </div>
      
      <div v-else class="export-content">
        <el-form :model="exportForm" label-width="100px">
          <el-form-item label="导出格式">
            <el-radio-group v-model="exportForm.format">
              <el-radio-button label="markdown">Markdown</el-radio-button>
              <el-radio-button label="json">JSON</el-radio-button>
              <el-radio-button label="csv">CSV</el-radio-button>
              <el-radio-button label="excel">Excel</el-radio-button>
            </el-radio-group>
          </el-form-item>
          
          <el-form-item label="包含内容">
            <el-checkbox-group v-model="exportForm.include">
              <el-checkbox label="test_cases">测试用例</el-checkbox>
              <el-checkbox label="coverage">覆盖率统计</el-checkbox>
            </el-checkbox-group>
          </el-form-item>
        </el-form>
        
        <div class="preview-section">
          <h3>预览</h3>
          <pre class="preview-content">{{ previewText }}</pre>
        </div>
        
        <div class="action-buttons">
          <el-button type="primary" :loading="loading" @click="exportFile">
            <el-icon><component :is="icons.Download" /></el-icon>
            导出文件
          </el-button>
        </div>
        
        <el-divider />
        
        <div class="export-history">
          <h3>导出记录</h3>
          <el-timeline>
            <el-timeline-item
              v-for="(record, index) in exportHistory"
              :key="index"
              :timestamp="record.time"
              placement="top"
            >
              <el-card>
                <div class="history-item">
                  <el-icon><component :is="icons.Document" /></el-icon>
                  <span>{{ record.filename }}</span>
                  <el-button type="text" size="small" @click="downloadRecord(record)">下载</el-button>
                </div>
              </el-card>
            </el-timeline-item>
          </el-timeline>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { exportTestCases } from '../api'
import * as icons from '@element-plus/icons-vue'

const router = useRouter()
const testCases = ref([])
const coverage = ref(null)
const loading = ref(false)
const exportHistory = ref([])

const exportForm = ref({
  format: 'markdown',
  include: ['test_cases', 'coverage']
})

const savedCases = localStorage.getItem('test_cases')
const savedCoverage = localStorage.getItem('coverage')

if (savedCases) {
  testCases.value = JSON.parse(savedCases)
}
if (savedCoverage) {
  coverage.value = JSON.parse(savedCoverage)
}

const previewText = computed(() => {
  if (!testCases.value.length) return ''
  
  const format = exportForm.value.format
  
  if (format === 'markdown') {
    let content = '# 测试用例文档\n\n'
    content += `## 覆盖率统计\n\n`
    content += `- 测试用例总数: ${coverage.value?.total_cases || 0}\n`
    content += `- 覆盖率: ${coverage.value?.coverage_rate || 0}%\n\n`
    content += '## 测试用例列表\n\n'
    
    testCases.value.slice(0, 3).forEach((item, index) => {
      content += `### ${index + 1}. ${item.name}\n\n`
      content += `- **类型**: ${item.type}\n`
      content += `- **优先级**: ${item.priority}\n`
      content += `- **预期结果**: ${item.expected_result}\n\n`
    })
    
    return content
  } else if (format === 'json') {
    return JSON.stringify({
      coverage: coverage.value,
      test_cases: testCases.value.slice(0, 3)
    }, null, 2)
  } else {
    return `测试用例总数: ${testCases.value.length}\n覆盖率: ${coverage.value?.coverage_rate || 0}%`
  }
})

const exportFile = async () => {
  loading.value = true
  try {
    const data = {
      test_cases: testCases.value,
      coverage: coverage.value,
      format: exportForm.value.format
    }
    
    const response = await exportTestCases(data)
    
    const timestamp = new Date().toISOString().slice(0, 19).replace(/[:.]/g, '-')
    const ext = exportForm.value.format === 'excel' ? 'xlsx' : exportForm.value.format
    const filename = `test_cases_${timestamp}.${ext}`
    
    const url = URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.download = filename
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
    
    exportHistory.value.unshift({
      filename,
      time: new Date().toLocaleString('zh-CN')
    })
  } catch (error) {
    console.error('导出失败:', error)
    alert('导出失败，请重试')
  } finally {
    loading.value = false
  }
}

const downloadRecord = (record) => {
  alert(`下载: ${record.filename}`)
}

const goToUpload = () => {
  router.push('/')
}
</script>

<style scoped>
.export-container {
  max-width: 800px;
  margin: 0 auto;
}

.empty-state {
  text-align: center;
  padding: 60px 0;
}

.empty-state p {
  color: #909399;
  margin-top: 10px;
}

.export-content {
  margin-top: 20px;
}

.preview-section {
  margin-top: 30px;
}

.preview-section h3 {
  font-size: 16px;
  color: #606266;
  margin-bottom: 10px;
}

.preview-content {
  background-color: #f5f7fa;
  padding: 15px;
  border-radius: 6px;
  max-height: 300px;
  overflow-y: auto;
  font-size: 14px;
  color: #303133;
}

.action-buttons {
  margin-top: 30px;
  display: flex;
  gap: 15px;
}

.export-history {
  margin-top: 20px;
}

.export-history h3 {
  font-size: 16px;
  color: #606266;
  margin-bottom: 15px;
}

.history-item {
  display: flex;
  align-items: center;
  gap: 10px;
}
</style>