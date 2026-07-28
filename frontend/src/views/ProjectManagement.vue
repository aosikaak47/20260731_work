<template>
  <div class="project-management">
    <div class="page-header">
      <h2>项目管理</h2>
      <p class="page-desc">管理平台项目，配置项目成员和数据隔离</p>
    </div>
    
    <el-card>
      <template #header>
        <div class="card-header">
          <span class="card-title">项目列表</span>
          <el-button type="primary" @click="handleAdd">
            <el-icon><component :is="icons.Plus" /></el-icon>
            新建项目
          </el-button>
        </div>
      </template>
      
      <div class="filter-bar">
        <el-select v-model="filterStatus" size="small" placeholder="状态">
          <el-option label="全部" value="" />
          <el-option label="启用" value="启用" />
          <el-option label="禁用" value="禁用" />
        </el-select>
        <el-input 
          v-model="searchKeyword" 
          placeholder="搜索项目名称..." 
          prefix-icon="Search"
          size="small"
          class="search-input"
        />
      </div>
      
      <el-table :data="filteredProjects" stripe border v-loading="loading">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="name" label="项目名称" min-width="150" />
        <el-table-column prop="description" label="项目描述" min-width="200" />
        <el-table-column prop="status" label="状态" width="80">
          <template #default="scope">
            <el-tag :type="scope.row.status === '启用' ? 'success' : 'info'">{{ scope.row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="memberCount" label="成员数" width="80" />
        <el-table-column prop="caseCount" label="用例数" width="80" />
        <el-table-column prop="createdAt" label="创建时间" width="150" />
        <el-table-column label="操作" width="280" class-name="action-cell">
          <template #default="scope">
            <div class="action-btns">
              <el-button size="small" @click="handleEdit(scope.row)">编辑</el-button>
              <el-button size="small" @click="handleMembers(scope.row)">成员</el-button>
              <el-button size="small" type="success" v-if="scope.row.status === '禁用'" @click="handleToggle(scope.row)">启用</el-button>
              <el-button size="small" type="warning" v-else @click="handleToggle(scope.row)">禁用</el-button>
              <el-button size="small" type="danger" @click="handleDelete(scope.row)">删除</el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>
      
      <el-pagination
        class="pagination"
        layout="total, prev, pager, next"
        :total="filteredProjects.length"
        :page-size="10"
      />
    </el-card>

    <el-dialog v-model="dialogVisible" :title="editingProject ? '编辑项目' : '新建项目'" width="500px">
      <el-form :model="projectForm" label-width="100px">
        <el-form-item label="项目名称" required>
          <el-input v-model="projectForm.name" placeholder="请输入项目名称" />
        </el-form-item>
        <el-form-item label="项目描述">
          <el-input v-model="projectForm.description" type="textarea" :rows="3" placeholder="请输入项目描述" />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="projectForm.status">
            <el-option label="启用" value="启用" />
            <el-option label="禁用" value="禁用" />
          </el-select>
        </el-form-item>
        <el-form-item label="成员数">
          <el-input-number v-model="projectForm.memberCount" :min="0" :max="100" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSave">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, reactive } from 'vue'
import * as icons from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useProjects } from '../composables/useProjects'

const { projects, loading, loadProjects, addProject, updateProject, deleteProject } = useProjects()

const searchKeyword = ref('')
const filterStatus = ref('')
const dialogVisible = ref(false)
const editingProject = ref(null)

const projectForm = reactive({
  name: '',
  description: '',
  status: '启用',
  memberCount: 0
})

const filteredProjects = computed(() => {
  let result = projects.value
  if (filterStatus.value) {
    result = result.filter(p => p.status === filterStatus.value)
  }
  if (searchKeyword.value) {
    const kw = searchKeyword.value.toLowerCase()
    result = result.filter(p => p.name.toLowerCase().includes(kw) || p.description.toLowerCase().includes(kw))
  }
  return result
})

const handleAdd = () => {
  editingProject.value = null
  projectForm.name = ''
  projectForm.description = ''
  projectForm.status = '启用'
  projectForm.memberCount = 0
  dialogVisible.value = true
}

const handleEdit = (row) => {
  editingProject.value = row
  projectForm.name = row.name
  projectForm.description = row.description || ''
  projectForm.status = row.status
  projectForm.memberCount = row.memberCount || 0
  dialogVisible.value = true
}

const handleSave = async () => {
  if (!projectForm.name) {
    ElMessage.warning('请输入项目名称')
    return
  }
  
  const payload = {
    name: projectForm.name,
    description: projectForm.description,
    status: projectForm.status,
    memberCount: projectForm.memberCount
  }
  
  if (editingProject.value) {
    const result = await updateProject(editingProject.value.id, payload)
    if (result) {
      ElMessage.success('项目更新成功')
      dialogVisible.value = false
    }
  } else {
    const result = await addProject(payload)
    if (result) {
      ElMessage.success('项目创建成功')
      dialogVisible.value = false
    }
  }
}

const handleMembers = (row) => {
  ElMessage.info(`管理成员: ${row.name}`)
}

const handleToggle = async (row) => {
  const newStatus = row.status === '启用' ? '禁用' : '启用'
  await updateProject(row.id, { status: newStatus })
  ElMessage.success(`项目已${newStatus}`)
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(`确定要删除项目 "${row.name}" 吗？`, '确认删除', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    const success = await deleteProject(row.id)
    if (success) {
      ElMessage.success('项目删除成功')
    }
  } catch {
    // User cancelled
  }
}

onMounted(() => {
  loadProjects()
})
</script>

<style scoped>
.project-management {
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

.filter-bar {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
}

.search-input {
  width: 200px;
}

.pagination {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}
</style>
