<template>
  <div class="data-backup">
    <div class="page-header">
      <h2>数据备份配置</h2>
      <p class="page-desc">管理数据备份和恢复</p>
    </div>
    
    <el-card>
      <template #header>
        <div class="card-header">
          <span class="card-title">备份配置</span>
        </div>
      </template>
      
      <el-form label-width="150px">
        <el-form-item label="自动备份">
          <el-switch v-model="autoBackup" />
        </el-form-item>
        <el-form-item label="备份周期">
          <el-select v-model="backupPeriod" :disabled="!autoBackup">
            <el-option label="每日" value="daily" />
            <el-option label="每周" value="weekly" />
            <el-option label="每月" value="monthly" />
          </el-select>
        </el-form-item>
        <el-form-item label="备份时间">
          <el-time-select v-model="backupTime" :disabled="!autoBackup" :start="'00:00'" :end="'23:00'" :step="'01:00'" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSaveConfig">保存配置</el-button>
          <el-button @click="handleManualBackup">手动备份</el-button>
        </el-form-item>
      </el-form>
    </el-card>
    
    <el-card style="margin-top: 20px;">
      <template #header>
        <div class="card-header">
          <span class="card-title">备份记录</span>
        </div>
      </template>
      
      <el-table :data="backups" stripe border>
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="name" label="备份名称" width="150" />
        <el-table-column prop="type" label="备份类型" width="100">
          <template #default="scope">
            <el-tag :type="scope.row.type === '自动' ? 'info' : 'success'">{{ scope.row.type }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="size" label="备份大小" width="100" />
        <el-table-column prop="time" label="备份时间" width="150" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="scope">
            <el-tag :type="scope.row.status === '成功' ? 'success' : 'danger'">{{ scope.row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" class-name="action-cell">
          <template #default="scope">
            <div class="action-btns">
              <el-button size="small" @click="handleRestore(scope.row)">恢复</el-button>
              <el-button size="small" type="danger" @click="handleDelete(scope.row)">删除</el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>
      
      <el-pagination
        class="pagination"
        layout="total, prev, pager, next"
        :total="backups.length"
        :page-size="10"
      />
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import * as icons from '@element-plus/icons-vue'

const autoBackup = ref(true)
const backupPeriod = ref('daily')
const backupTime = ref('02:00')

const backups = ref([
  { id: 1, name: 'auto_backup_20260721', type: '自动', size: '256MB', time: '2026-07-21 02:00:00', status: '成功' },
  { id: 2, name: 'manual_backup_20260720', type: '手动', size: '245MB', time: '2026-07-20 14:30:00', status: '成功' },
  { id: 3, name: 'auto_backup_20260720', type: '自动', size: '240MB', time: '2026-07-20 02:00:00', status: '成功' },
  { id: 4, name: 'auto_backup_20260719', type: '自动', size: '235MB', time: '2026-07-19 02:00:00', status: '成功' },
  { id: 5, name: 'auto_backup_20260718', type: '自动', size: '230MB', time: '2026-07-18 02:00:00', status: '失败' }
])

const handleSaveConfig = () => {
  alert('保存配置成功')
}

const handleManualBackup = () => {
  alert('手动备份')
}

const handleRestore = (row) => {
  alert(`恢复备份: ${row.name}`)
}

const handleDelete = (row) => {
  backups.value = backups.value.filter(item => item.id !== row.id)
}
</script>

<style scoped>
.data-backup {
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

.card-title {
  font-size: 16px;
  font-weight: 600;
}

.pagination {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}
</style>