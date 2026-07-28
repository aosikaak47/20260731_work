<template>
  <div class="home-container">
    <el-card class="upload-card">
      <div class="upload-header">
        <h2>上传文档或截图</h2>
        <p>支持系统截图、需求文档自动识别</p>
      </div>
      
      <el-upload
        class="upload-area"
        drag
        :auto-upload="false"
        :on-change="handleFileChange"
        :before-upload="beforeUpload"
        :limit="1"
        accept=".png,.jpg,.jpeg,.webp,.txt,.md,.pdf,.docx"
      >
        <el-icon class="upload-icon" size="48"><component :is="icons.Upload" /></el-icon>
        <div class="upload-text">拖拽文件到此处，或<em>点击选择</em></div>
        <div class="upload-hint">支持: 系统截图(PNG/JPG/WEBP), 需求文档(TXT/MD/PDF/DOCX)</div>
      </el-upload>
      
      <div v-if="selectedFile" class="file-info">
        <el-tag type="success" closable @close="clearFile">
          <el-icon><component :is="icons.Document" /></el-icon>
          {{ selectedFile.name }}
        </el-tag>
      </div>
      
      <div class="doc-type-section">
        <span class="label">文档类型:</span>
        <el-radio-group v-model="docType">
          <el-radio-button label="auto">自动识别</el-radio-button>
          <el-radio-button label="requirement">需求文档</el-radio-button>
          <el-radio-button label="api">接口文档</el-radio-button>
        </el-radio-group>
      </div>
      
      <div class="content-input-section">
        <span class="label">需求描述/补充文字:</span>
        <el-input
          type="textarea"
          v-model="contentText"
          :rows="4"
          placeholder="在此粘贴或编辑需求文字；上传的TXT/MD/PDF/DOCX文本会自动填充到这里。留空则仅依赖截图由模型识别。"
        />
      </div>
      
      <div class="action-buttons">
        <el-button type="primary" :loading="loading" @click="generateTestCases">
          <el-icon><component :is="icons.ZoomIn" /></el-icon>
          智能生成测试用例
        </el-button>
        <el-button @click="clearAll">
          <el-icon><component :is="icons.Delete" /></el-icon>
          清空
        </el-button>
      </div>
    </el-card>
    
    <el-card v-if="result" class="result-card">
      <template #header>
        <div class="result-header">
          <span>生成结果</span>
          <el-button type="text" @click="viewCases">查看测试用例</el-button>
        </div>
      </template>
      
      <div class="result-summary">
        <el-row :gutter="20">
          <el-col :span="6">
            <el-statistic title="测试用例总数" :value="result.coverage.total_cases" />
          </el-col>
          <el-col :span="6">
            <el-statistic title="覆盖率" :value="result.coverage.coverage_rate" suffix="%" />
          </el-col>
          <el-col :span="6">
            <el-statistic title="功能用例" :value="result.coverage.by_type['功能'] || 0" />
          </el-col>
          <el-col :span="6">
            <el-statistic title="异常用例" :value="result.coverage.by_type['异常'] || 0" />
          </el-col>
        </el-row>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { uploadFile, analyzeContent } from '../api'
import * as icons from '@element-plus/icons-vue'

const router = useRouter()
const selectedFile = ref(null)
const docType = ref('auto')
const contentText = ref('')
const loading = ref(false)
const result = ref(null)

const handleFileChange = (file) => {
  selectedFile.value = file.raw
}

const beforeUpload = (file) => {
  const isLt25M = file.size / 1024 / 1024 < 25
  if (!isLt25M) {
    alert('文件大小不能超过 25MB!')
  }
  return false
}

const generateTestCases = async () => {
  loading.value = true
  try {
    if (selectedFile.value) {
      const response = await uploadFile(selectedFile.value, docType.value)
      result.value = response.data
      contentText.value = response.data.content || ''
    } else if (contentText.value.trim()) {
      const response = await analyzeContent({
        text: contentText.value,
        doc_type: docType.value
      })
      result.value = response.data
    } else {
      alert('请上传文件或输入需求描述')
      loading.value = false
      return
    }
    
    localStorage.setItem('test_cases', JSON.stringify(result.value.test_cases))
    localStorage.setItem('coverage', JSON.stringify(result.value.coverage))
    
    router.push('/cases')
  } catch (error) {
    console.error('生成测试用例失败:', error)
    alert('生成测试用例失败，请重试')
  } finally {
    loading.value = false
  }
}

const clearFile = () => {
  selectedFile.value = null
}

const clearAll = () => {
  selectedFile.value = null
  contentText.value = ''
  result.value = null
}

const viewCases = () => {
  router.push('/cases')
}
</script>

<style scoped>
.home-container {
  max-width: 800px;
  margin: 0 auto;
}

.upload-card {
  margin-bottom: 20px;
}

.upload-header {
  text-align: center;
  margin-bottom: 30px;
}

.upload-header h2 {
  font-size: 24px;
  color: #303133;
  margin-bottom: 8px;
}

.upload-header p {
  color: #909399;
  font-size: 14px;
}

.upload-area {
  border: 2px dashed #d9d9d9;
  border-radius: 6px;
  padding: 40px;
  transition: all 0.3s;
}

.upload-area:hover {
  border-color: #667eea;
}

.upload-icon {
  color: #667eea;
}

.upload-text {
  color: #606266;
  font-size: 16px;
  margin-top: 10px;
}

.upload-hint {
  color: #909399;
  font-size: 12px;
  margin-top: 8px;
}

.file-info {
  margin-top: 20px;
}

.doc-type-section,
.content-input-section {
  margin-top: 20px;
}

.label {
  display: block;
  color: #606266;
  font-size: 14px;
  margin-bottom: 10px;
}

.action-buttons {
  margin-top: 30px;
  display: flex;
  gap: 15px;
  justify-content: center;
}

.result-card {
  margin-top: 30px;
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.result-summary {
  margin-top: 20px;
}
</style>