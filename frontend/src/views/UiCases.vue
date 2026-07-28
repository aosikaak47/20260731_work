<template>
  <div class="ui-cases">
    <div class="page-header">
      <h2>UI用例编排</h2>
      <p class="page-desc">拖拽式编排UI自动化测试场景</p>
    </div>
    
    <div class="ui-container">
      <div class="left-panel">
        <el-card class="component-library">
          <template #header>
            <span class="card-title">操作组件库</span>
          </template>
          
          <div class="component-grid">
            <div 
              v-for="component in components" 
              :key="component.id" 
              class="component-item"
              draggable="true"
              @dragstart="handleDragStart(component)"
            >
              <el-icon :size="20"><component :is="component.icon" /></el-icon>
              <span>{{ component.name }}</span>
            </div>
          </div>
        </el-card>
      </div>
      
      <div class="center-panel">
        <el-card class="flow-canvas">
          <template #header>
            <div class="card-header">
              <span class="card-title">流程画布</span>
              <div class="canvas-actions">
                <el-button size="small" @click="handleAddStep">
                  <el-icon><component :is="icons.Plus" /></el-icon>
                  添加步骤
                </el-button>
                <el-button size="small" @click="handleClear">
                  <el-icon><component :is="icons.Delete" /></el-icon>
                  清空
                </el-button>
              </div>
            </div>
          </template>
          
          <div class="canvas" @drop="handleDrop" @dragover.prevent>
            <div v-if="steps.length === 0" class="empty-canvas">
              <el-icon :size="48" class="empty-icon"><component :is="icons.Box" /></el-icon>
              <span>拖拽左侧组件到此处，或点击添加步骤</span>
            </div>
            
            <div v-else class="steps-list">
              <div 
                v-for="(step, index) in steps" 
                :key="step.id" 
                class="step-card"
              >
                <div class="step-header">
                  <span class="step-num">{{ index + 1 }}</span>
                  <el-icon :size="16"><component :is="step.icon" /></el-icon>
                  <span class="step-name">{{ step.name }}</span>
                  <el-icon class="step-delete" @click="handleRemoveStep(step.id)">
                    <component :is="icons.Close" />
                  </el-icon>
                </div>
                <div class="step-body">
                  <el-form label-width="80px" :model="step">
                    <el-form-item label="元素">
                      <el-select v-model="step.element">
                        <el-option label="用户名输入框" value="username" />
                        <el-option label="密码输入框" value="password" />
                        <el-option label="登录按钮" value="login-btn" />
                      </el-select>
                    </el-form-item>
                    <el-form-item label="参数">
                      <el-input v-model="step.params" placeholder="输入参数..." />
                    </el-form-item>
                    <el-form-item label="延时">
                      <el-input-number v-model="step.delay" :min="0" :max="10" />
                      <span style="margin-left: 8px;">秒</span>
                    </el-form-item>
                    <el-form-item label="重试">
                      <el-input-number v-model="step.retry" :min="0" :max="5" />
                      <span style="margin-left: 8px;">次</span>
                    </el-form-item>
                  </el-form>
                </div>
              </div>
            </div>
          </div>
        </el-card>
        
        <div class="run-actions">
          <el-button @click="handlePreview">
            <el-icon><component :is="icons.View" /></el-icon>
            预览执行
          </el-button>
          <el-button type="primary" @click="handleSave">
            <el-icon><component :is="icons.FolderChecked" /></el-icon>
            保存场景
          </el-button>
          <el-button type="success" @click="handleRun">
            <el-icon><component :is="icons.VideoPlay" /></el-icon>
            一键运行
          </el-button>
        </div>
      </div>
      
      <div class="right-panel">
        <el-card class="log-panel">
          <template #header>
            <span class="card-title">执行日志</span>
          </template>
          <div class="log-content">
            <div v-for="log in logs" :key="log.id" class="log-item" :class="log.type">
              <el-icon :size="14"><component :is="log.icon" /></el-icon>
              <span>{{ log.content }}</span>
              <span class="log-time">{{ log.time }}</span>
            </div>
          </div>
        </el-card>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, markRaw } from 'vue'
import * as icons from '@element-plus/icons-vue'

const components = ref([
  { id: 'click', name: '点击', icon: markRaw(icons.Mouse) },
  { id: 'input', name: '输入', icon: markRaw(icons.Operation) },
  { id: 'select', name: '选择', icon: markRaw(icons.CaretBottom) },
  { id: 'wait', name: '等待', icon: markRaw(icons.Clock) },
  { id: 'assert', name: '断言', icon: markRaw(icons.CircleCheck) },
  { id: 'screenshot', name: '截图', icon: markRaw(icons.Camera) },
  { id: 'scroll', name: '滚动', icon: markRaw(icons.ArrowDown) },
  { id: 'switch', name: '条件判断', icon: markRaw(icons.Share) }
])

const steps = ref([
  { id: 1, name: '点击', icon: markRaw(icons.Mouse), element: 'username', params: '', delay: 0, retry: 0 },
  { id: 2, name: '输入', icon: markRaw(icons.Operation), element: 'username', params: 'admin', delay: 0, retry: 0 },
  { id: 3, name: '输入', icon: markRaw(icons.Operation), element: 'password', params: '123456', delay: 0, retry: 0 },
  { id: 4, name: '点击', icon: markRaw(icons.Mouse), element: 'login-btn', params: '', delay: 1, retry: 2 }
])

const logs = ref([
  { id: 1, type: 'info', icon: markRaw(icons.InfoFilled), content: '场景执行开始', time: '10:00:00' },
  { id: 2, type: 'success', icon: markRaw(icons.CircleCheck), content: '步骤1: 点击用户名输入框 - 通过', time: '10:00:01' },
  { id: 3, type: 'success', icon: markRaw(icons.CircleCheck), content: '步骤2: 输入用户名 "admin" - 通过', time: '10:00:02' },
  { id: 4, type: 'success', icon: markRaw(icons.CircleCheck), content: '步骤3: 输入密码 "******" - 通过', time: '10:00:03' },
  { id: 5, type: 'success', icon: markRaw(icons.CircleCheck), content: '步骤4: 点击登录按钮 - 通过', time: '10:00:05' }
])

const draggedComponent = ref(null)

const handleDragStart = (component) => {
  draggedComponent.value = component
}

const handleDrop = () => {
  if (draggedComponent.value) {
    const newStep = {
      id: Date.now(),
      name: draggedComponent.value.name,
      icon: draggedComponent.value.icon,
      element: '',
      params: '',
      delay: 0,
      retry: 0
    }
    steps.value.push(newStep)
    draggedComponent.value = null
  }
}

const handleAddStep = () => {
  const newStep = {
    id: Date.now(),
    name: '点击',
    icon: icons.Mouse,
    element: '',
    params: '',
    delay: 0,
    retry: 0
  }
  steps.value.push(newStep)
}

const handleRemoveStep = (id) => {
  steps.value = steps.value.filter(step => step.id !== id)
}

const handleClear = () => {
  steps.value = []
}

const handlePreview = () => {
  alert('预览执行')
}

const handleSave = () => {
  alert('保存场景成功')
}

const handleRun = () => {
  alert('运行场景')
}
</script>

<style scoped>
.ui-cases {
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

.ui-container {
  display: grid;
  grid-template-columns: 200px 1fr 300px;
  gap: 16px;
}

.left-panel {
  height: fit-content;
}

.card-title {
  font-size: 16px;
  font-weight: 600;
}

.component-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 8px;
}

.component-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px;
  background-color: #f9fafb;
  border-radius: 8px;
  cursor: grab;
  transition: all 0.2s;
}

.component-item:hover {
  background-color: #f3f4f6;
  border: 1px solid #6366f1;
}

.center-panel {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.canvas-actions {
  display: flex;
  gap: 8px;
}

.canvas {
  min-height: 450px;
  border: 2px dashed #d1d5db;
  border-radius: 12px;
  padding: 20px;
}

.empty-canvas {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 400px;
  color: #9ca3af;
  gap: 12px;
}

.empty-icon {
  color: #c0c4cc;
}

.steps-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.step-card {
  background-color: #f9fafb;
  border-radius: 8px;
  border: 2px solid transparent;
}

.step-card:hover {
  border-color: #6366f1;
}

.step-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 12px;
  background-color: #fff;
  border-radius: 8px 8px 0 0;
  border-bottom: 1px solid #e5e7eb;
}

.step-num {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background-color: #6366f1;
  color: white;
  font-size: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.step-name {
  flex: 1;
  font-weight: 500;
}

.step-delete {
  opacity: 0;
  cursor: pointer;
}

.step-card:hover .step-delete {
  opacity: 1;
}

.step-body {
  padding: 12px;
}

.run-actions {
  display: flex;
  gap: 12px;
  padding: 16px;
  background-color: #fff;
  border-radius: 8px;
}

.right-panel {
  height: fit-content;
}

.log-content {
  max-height: 300px;
  overflow-y: auto;
}

.log-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 0;
  font-size: 13px;
}

.log-item.info {
  color: #6b7280;
}

.log-item.success {
  color: #10b981;
}

.log-item.error {
  color: #ef4444;
}

.log-time {
  margin-left: auto;
  font-size: 12px;
  color: #9ca3af;
}
</style>