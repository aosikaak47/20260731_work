<template>
  <div class="ui-tasks">
    <div class="page-header">
      <h2>UI场景任务</h2>
      <p class="page-desc">管理UI自动化测试任务</p>
    </div>
    <el-card>
      <template #header>
        <span class="card-title">任务列表</span>
      </template>
      <div class="empty-state">
        <el-icon :size="48" class="empty-icon"><component :is="icons.Box" /></el-icon>
        <span>功能开发中</span>
      </div>
    </el-card>
  </div>
</template>
<script setup>
import * as icons from '@element-plus/icons-vue'
</script>
<style scoped>
.ui-tasks { padding: 20px; }
.page-header { margin-bottom: 24px; }
.page-header h2 { font-size: 24px; font-weight: 600; color: #1f2937; margin-bottom: 4px; }
.page-desc { font-size: 14px; color: #6b7280; }
.card-title { font-size: 16px; font-weight: 600; }
.empty-state { display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 60px; color: #9ca3af; gap: 12px; }
.empty-icon { color: #c0c4cc; }
</style>