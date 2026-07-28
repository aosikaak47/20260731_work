<template>
  <div class="empty-state">
    <div class="empty-icon">
      <el-icon :size="iconSize"><component :is="icon" /></el-icon>
    </div>
    <div class="empty-text">{{ text }}</div>
    <div class="empty-action" v-if="showAction">
      <slot name="action">
        <el-button type="primary" @click="$emit('refresh')">刷新</el-button>
      </slot>
    </div>
  </div>
</template>

<script setup>
import * as icons from '@element-plus/icons-vue'

defineProps({
  text: {
    type: String,
    default: '暂无数据'
  },
  icon: {
    type: Object,
    default: icons.Box
  },
  iconSize: {
    type: Number,
    default: 48
  },
  showAction: {
    type: Boolean,
    default: true
  }
})

defineEmits(['refresh'])
</script>

<style scoped>
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  color: #909399;
}

.empty-icon {
  width: 80px;
  height: 80px;
  line-height: 80px;
  text-align: center;
  background-color: #f5f7fa;
  border-radius: 50%;
  margin-bottom: 16px;
  color: #c0c4cc;
}

.empty-text {
  font-size: 14px;
  margin-bottom: 20px;
}

.empty-action {
  display: flex;
  gap: 12px;
}
</style>