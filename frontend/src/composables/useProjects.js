import { ref, computed } from 'vue'

const projects = ref([])
const currentProjectId = ref(null)
const loading = ref(false)
const initialized = ref(false)

export function useProjects() {
  const loadProjects = async (force = false) => {
    if (initialized.value && !force) return
    loading.value = true
    try {
      const response = await fetch('/api/v1/projects')
      const data = await response.json()
      projects.value = data.projects || []
      if (projects.value.length > 0 && !currentProjectId.value) {
        currentProjectId.value = projects.value[0].id
      }
      initialized.value = true
    } catch (error) {
      console.error('加载项目列表失败:', error)
      // 只有在未初始化时才使用默认数据
      if (!initialized.value) {
        projects.value = [
          { id: '1', name: '智能测试平台项目', description: '平台核心项目', status: '启用', memberCount: 5, caseCount: 456, createdAt: '2026-07-01 10:00' },
          { id: '2', name: '党建系统项目', description: '党建管理系统测试项目', status: '启用', memberCount: 3, caseCount: 234, createdAt: '2026-07-05 14:30' },
          { id: '3', name: '电商平台项目', description: '电商平台接口与UI自动化测试', status: '启用', memberCount: 4, caseCount: 567, createdAt: '2026-07-10 09:00' },
          { id: '4', name: 'OA办公系统', description: '办公自动化系统测试', status: '禁用', memberCount: 2, caseCount: 128, createdAt: '2026-07-15 11:00' }
        ]
        if (!currentProjectId.value) {
          currentProjectId.value = '1'
        }
      }
    } finally {
      loading.value = false
    }
  }

  const setCurrentProject = (projectId) => {
    currentProjectId.value = projectId
  }

  const currentProject = computed(() => {
    return projects.value.find(p => p.id === currentProjectId.value) || null
  })

  const activeProjects = computed(() => {
    return projects.value.filter(p => p.status === '启用')
  })

  const getProjectById = (id) => {
    return projects.value.find(p => p.id === id) || null
  }

  const addProject = async (projectData) => {
    try {
      const response = await fetch('/api/v1/projects', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(projectData)
      })
      const data = await response.json()
      if (data.success) {
        await loadProjects()
        return data.project
      }
    } catch (error) {
      console.error('创建项目失败:', error)
    }
    return null
  }

  const updateProject = async (projectId, updates) => {
    try {
      const response = await fetch(`/api/v1/projects/${projectId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(updates)
      })
      const data = await response.json()
      if (data.success) {
        await loadProjects()
        return data.project
      }
    } catch (error) {
      console.error('更新项目失败:', error)
    }
    return null
  }

  const deleteProject = async (projectId) => {
    try {
      const response = await fetch(`/api/v1/projects/${projectId}`, {
        method: 'DELETE'
      })
      const data = await response.json()
      if (data.success) {
        if (currentProjectId.value === projectId && projects.value.length > 1) {
          currentProjectId.value = projects.value.find(p => p.id !== projectId)?.id || null
        }
        await loadProjects()
        return true
      }
    } catch (error) {
      console.error('删除项目失败:', error)
    }
    return false
  }

  return {
    projects,
    currentProjectId,
    currentProject,
    activeProjects,
    loading,
    loadProjects,
    setCurrentProject,
    getProjectById,
    addProject,
    updateProject,
    deleteProject
  }
}
