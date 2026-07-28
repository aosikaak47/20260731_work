<template>
  <div class="case-import-export">
    <div class="page-header">
      <h2>用例导入导出</h2>
      <p class="page-desc">导入和导出测试用例</p>
    </div>
    
    <el-card>
      <template #header>
        <span class="card-title">用例导入</span>
      </template>
      
      <el-upload
        class="upload-demo"
        drag
        :action="uploadUrl"
        :on-change="handleFileChange"
      >
        <el-icon class="el-icon--upload"><component :is="icons.Upload" /></el-icon>
        <div class="el-upload__text">将文件拖到此处，或<em>点击上传</em></div>
        <template #tip>
          <div class="el-upload__tip">支持 .xlsx .json .txt .md 格式</div>
        </template>
      </el-upload>
    </el-card>
    
    <el-card style="margin-top: 20px;">
      <template #header>
        <div class="card-header">
          <span class="card-title">用例导出</span>
        </div>
      </template>
      
      <el-form label-width="100px">
        <el-form-item label="导出格式">
          <el-select v-model="exportFormat">
            <el-option label="Excel (.xlsx)" value="xlsx" />
            <el-option label="JSON" value="json" />
            <el-option label="CSV" value="csv" />
            <el-option label="Markdown" value="md" />
          </el-select>
        </el-form-item>
        <el-form-item label="导出范围">
          <el-radio-group v-model="exportScope">
            <el-radio label="全部用例" />
            <el-radio label="选中用例" />
            <el-radio label="按模块导出" />
          </el-radio-group>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleExport">
            <el-icon><component :is="icons.Download" /></el-icon>
            导出用例
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import * as icons from '@element-plus/icons-vue'

const exportFormat = ref('xlsx')
const exportScope = ref('全部用例')
const uploadUrl = 'http://localhost:8000/api/v1/upload'

const handleFileChange = (file) => {
  console.log('File selected:', file.name)
}

const handleExport = () => {
  alert('导出用例')
}
</script>

<style scoped>
.case-import-export { padding: 20px; }
.page-header { margin-bottom: 24px; }
.page-header h2 { font-size: 24px; font-weight: 600; color: #1f2937; margin-bottom: 4px; }
.page-desc { font-size: 14px; color: #6b7280; }
.card-title { font-size: 16px; font-weight: 600; }
.card-header { display: flex; align-items: center; justify-content: space-between; }
</style>