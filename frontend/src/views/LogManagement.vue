<template>
  <div class="log-management">
    <div class="page-header">
      <h2>日志管理</h2>
      <p class="page-desc">查看系统操作日志和执行日志</p>
    </div>
    
    <el-card>
      <template #header>
        <div class="card-header">
          <el-tabs v-model="activeTab">
            <el-tab-pane label="操作日志" name="operation" />
            <el-tab-pane label="执行日志" name="execution" />
          </el-tabs>
          <el-button size="small" type="success" @click="handleExport">
            <el-icon><component :is="icons.Download" /></el-icon>
            导出
          </el-button>
        </div>
      </template>
      
      <div class="filter-bar">
        <el-input 
          v-model="searchKeyword" 
          placeholder="搜索日志内容..." 
          prefix-icon="Search"
          size="small"
          class="search-input"
        />
        <el-date-picker 
          v-model="dateRange" 
          type="daterange" 
          range-separator="至" 
          start-placeholder="开始日期" 
          end-placeholder="结束日期"
          size="small"
        />
      </div>
      
      <el-table :data="logs" stripe border>
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="user" label="操作用户" width="120" />
        <el-table-column prop="action" label="操作类型" width="120">
          <template #default="scope">
            <el-tag>{{ scope.row.action }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="content" label="操作内容" min-width="200" />
        <el-table-column prop="module" label="所属模块" width="120" />
        <el-table-column prop="ip" label="IP地址" width="150" />
        <el-table-column prop="time" label="操作时间" width="150" />
      </el-table>
      
      <el-pagination
        class="pagination"
        layout="total, prev, pager, next"
        :total="logs.length"
        :page-size="10"
      />
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import * as icons from '@element-plus/icons-vue'

const activeTab = ref('operation')
const searchKeyword = ref('')
const dateRange = ref([])

const logs = ref([
  { id: 1, user: 'admin', action: '新增', content: '新增测试用例 "AI用例生成 - 需求文档导入生成"', module: '用例管理', ip: '192.168.1.100', time: '2026-07-21 10:30:00' },
  { id: 2, user: 'admin', action: '编辑', content: '编辑接口用例 "用户登录接口"', module: '接口自动化', ip: '192.168.1.100', time: '2026-07-21 10:25:00' },
  { id: 3, user: 'tester1', action: '执行', content: '执行任务 "回归测试任务"', module: '任务调度', ip: '192.168.1.101', time: '2026-07-21 10:00:00' },
  { id: 4, user: 'project_admin', action: '删除', content: '删除项目 "旧版项目"', module: '项目管理', ip: '192.168.1.102', time: '2026-07-21 09:30:00' },
  { id: 5, user: 'admin', action: '登录', content: '用户登录系统', module: '系统管理', ip: '192.168.1.100', time: '2026-07-21 09:00:00' }
])

const handleExport = () => {
  alert('导出日志')
}
</script>

<style scoped>
.log-management {
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

.filter-bar {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
}

.search-input {
  width: 250px;
}

.pagination {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}
</style>