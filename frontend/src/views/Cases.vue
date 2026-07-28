<template>
  <div class="cases-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <h2>测试用例列表</h2>
          <div class="filter-section">
            <el-select v-model="filterType" placeholder="按类型筛选" clearable>
              <el-option label="功能" value="功能" />
              <el-option label="异常" value="异常" />
              <el-option label="边界" value="边界" />
              <el-option label="安全" value="安全" />
              <el-option label="性能" value="性能" />
            </el-select>
            <el-select v-model="filterPriority" placeholder="按优先级筛选" clearable>
              <el-option label="高" value="高" />
              <el-option label="中" value="中" />
              <el-option label="低" value="低" />
            </el-select>
          </div>
        </div>
      </template>
      
      <div v-if="testCases.length === 0" class="empty-state">
        <el-icon size="64" color="#c0c4cc"><component :is="icons.List" /></el-icon>
        <p>暂无测试用例</p>
        <el-button type="primary" @click="goToUpload">去上传文档</el-button>
      </div>
      
      <div v-else class="cases-list">
        <el-collapse v-model="activeNames" accordion>
          <el-collapse-item v-for="(caseItem, index) in filteredCases" :key="caseItem.id" :name="caseItem.id">
            <template #title>
              <div class="case-title">
                <span class="case-index">{{ index + 1 }}</span>
                <span class="case-name">{{ caseItem.name }}</span>
                <el-tag :type="getTagType(caseItem.type)">{{ caseItem.type }}</el-tag>
                <el-tag :type="getPriorityType(caseItem.priority)">{{ caseItem.priority }}</el-tag>
              </div>
            </template>
            
            <div class="case-details">
              <el-descriptions :column="1" border>
                <el-descriptions-item label="前置条件">{{ caseItem.preconditions }}</el-descriptions-item>
                <el-descriptions-item label="执行步骤">
                  <ol>
                    <li v-for="(step, idx) in caseItem.steps" :key="idx">{{ step }}</li>
                  </ol>
                </el-descriptions-item>
                <el-descriptions-item label="预期结果">{{ caseItem.expected_result }}</el-descriptions-item>
                <el-descriptions-item label="状态">
                  <el-tag :type="getStatusType(caseItem.status)">{{ caseItem.status }}</el-tag>
                </el-descriptions-item>
              </el-descriptions>
            </div>
          </el-collapse-item>
        </el-collapse>
      </div>
      
      <div v-if="testCases.length > 0" class="pagination-section">
        <el-pagination
          v-model:current-page="currentPage"
          :page-size="pageSize"
          :total="filteredCases.length"
          layout="total, prev, pager, next, jumper"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import * as icons from '@element-plus/icons-vue'

const router = useRouter()
const testCases = ref([])
const filterType = ref('')
const filterPriority = ref('')
const activeNames = ref([])
const currentPage = ref(1)
const pageSize = ref(10)

onMounted(() => {
  const savedCases = localStorage.getItem('test_cases')
  if (savedCases) {
    testCases.value = JSON.parse(savedCases)
  }
})

const filteredCases = computed(() => {
  return testCases.value.filter(item => {
    if (filterType.value && item.type !== filterType.value) return false
    if (filterPriority.value && item.priority !== filterPriority.value) return false
    return true
  })
})

const getTagType = (type) => {
  const types = {
    '功能': 'primary',
    '异常': 'danger',
    '边界': 'warning',
    '安全': 'success',
    '性能': 'info'
  }
  return types[type] || 'info'
}

const getPriorityType = (priority) => {
  const types = {
    '高': 'danger',
    '中': 'warning',
    '低': 'info'
  }
  return types[priority] || 'info'
}

const getStatusType = (status) => {
  const types = {
    '已执行': 'success',
    '通过': 'success',
    '失败': 'danger',
    '未执行': 'warning'
  }
  return types[status] || 'info'
}

const goToUpload = () => {
  router.push('/')
}
</script>

<style scoped>
.cases-container {
  max-width: 1200px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h2 {
  font-size: 20px;
  color: #303133;
}

.filter-section {
  display: flex;
  gap: 10px;
}

.empty-state {
  text-align: center;
  padding: 60px 0;
}

.empty-state p {
  color: #909399;
  margin-top: 10px;
}

.cases-list {
  margin-top: 20px;
}

.case-title {
  display: flex;
  align-items: center;
  gap: 12px;
}

.case-index {
  width: 30px;
  height: 30px;
  background-color: #667eea;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: bold;
}

.case-name {
  flex: 1;
  font-weight: 500;
}

.case-details {
  margin-top: 10px;
}

.pagination-section {
  margin-top: 30px;
  display: flex;
  justify-content: center;
}
</style>