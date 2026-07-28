<template>
  <div class="task-center">
    <div class="page-header">
      <h2>测试任务中心</h2>
      <p class="page-desc">管理所有自动化测试任务</p>
    </div>
    
    <el-card>
      <template #header>
        <div class="card-header">
          <el-tabs v-model="activeTab" class="task-tabs">
            <el-tab-pane label="手动任务" name="manual" />
            <el-tab-pane label="定时任务" name="scheduled" />
            <el-tab-pane label="CI触发" name="ci" />
            <el-tab-pane label="历史记录" name="history" />
          </el-tabs>
          <el-button type="primary" @click="handleAddTask">
            <el-icon><component :is="icons.Plus" /></el-icon>
            新建任务
          </el-button>
        </div>
      </template>
      
      <div v-if="activeTab === 'manual'">
        <el-table :data="manualTasks" stripe border>
          <el-table-column prop="id" label="ID" width="60" />
          <el-table-column prop="name" label="任务名称" min-width="150" />
          <el-table-column prop="type" label="任务类型" width="120">
            <template #default="scope">
              <el-tag>{{ scope.row.type }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="status" label="状态" width="100">
            <template #default="scope">
              <el-tag :type="getStatusType(scope.row.status)">{{ scope.row.status }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="progress" label="进度" width="100">
            <template #default="scope">
              <el-progress :percentage="scope.row.progress" :stroke-width="8" />
            </template>
          </el-table-column>
          <el-table-column prop="startTime" label="开始时间" width="150" />
          <el-table-column prop="duration" label="耗时" width="100" />
          <el-table-column label="操作" width="260" class-name="action-cell">
            <template #default="scope">
              <div class="action-btns">
                <el-button size="small" @click="handleViewLog(scope.row)">日志</el-button>
                <el-button size="small" @click="handleRetry(scope.row)">重试</el-button>
                <el-button size="small" type="danger" @click="handleStop(scope.row)">终止</el-button>
                <el-button size="small" @click="handleViewReport(scope.row)">报告</el-button>
              </div>
            </template>
          </el-table-column>
        </el-table>
      </div>
      
      <div v-else>
        <div class="empty-tab">
          <el-icon :size="48" class="empty-icon"><component :is="icons.Box" /></el-icon>
          <span>暂无{{ activeTab === 'scheduled' ? '定时' : activeTab === 'ci' ? 'CI触发' : '历史' }}任务</span>
        </div>
      </div>
      
      <el-pagination
        class="pagination"
        layout="total, prev, pager, next"
        :total="manualTasks.length"
        :page-size="10"
      />
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import * as icons from '@element-plus/icons-vue'

const activeTab = ref('manual')

const manualTasks = ref([
  { id: 1, name: '回归测试任务', type: '接口自动化', status: '运行中', progress: 65, startTime: '2026-07-21 14:00', duration: '5m 30s' },
  { id: 2, name: 'UI自动化回归', type: 'UI自动化', status: '已完成', progress: 100, startTime: '2026-07-21 13:30', duration: '15m 20s' },
  { id: 3, name: '登录功能测试', type: 'UI自动化', status: '已完成', progress: 100, startTime: '2026-07-21 13:00', duration: '3m 45s' },
  { id: 4, name: '用户管理接口测试', type: '接口自动化', status: '失败', progress: 80, startTime: '2026-07-21 12:30', duration: '8m 10s' },
  { id: 5, name: '项目管理接口测试', type: '接口自动化', status: '已完成', progress: 100, startTime: '2026-07-21 12:00', duration: '6m 05s' }
])

const handleAddTask = () => {
  alert('新建任务')
}

const handleViewLog = (row) => {
  alert(`查看日志: ${row.name}`)
}

const handleRetry = (row) => {
  alert(`重试任务: ${row.name}`)
}

const handleStop = (row) => {
  alert(`终止任务: ${row.name}`)
}

const handleViewReport = (row) => {
  alert(`查看报告: ${row.name}`)
}

const getStatusType = (status) => {
  const types = { '运行中': 'warning', '已完成': 'success', '失败': 'danger', '等待中': 'info' }
  return types[status] || 'info'
}
</script>

<style scoped>
.task-center {
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
}

.task-tabs {
  flex: 1;
}

.empty-tab {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px;
  color: #9ca3af;
  gap: 12px;
}

.empty-icon {
  color: #c0c4cc;
}

.pagination {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}
</style>