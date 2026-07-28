<template>
  <div class="header-wrapper">
    <div class="header-left">
      <el-breadcrumb separator="/">
        <el-breadcrumb-item v-for="(item, index) in breadcrumbList" :key="index">
          <router-link v-if="item.path" :to="item.path">{{ item.name }}</router-link>
          <span v-else>{{ item.name }}</span>
        </el-breadcrumb-item>
      </el-breadcrumb>
    </div>
    
    <div class="header-right">
      <el-dropdown class="project-selector">
        <span class="project-trigger">
          <el-icon :size="18"><component :is="icons.Folder" /></el-icon>
          <span>{{ currentProject }}</span>
          <el-icon :size="14"><component :is="icons.ArrowDown" /></el-icon>
        </span>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item v-for="project in projects" :key="project.id">
              {{ project.name }}
            </el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
      
      <div class="search-box">
        <el-input 
          v-model="searchKeyword" 
          placeholder="全局搜索" 
          prefix-icon="Search"
          size="small"
          class="search-input"
        />
      </div>
      
      <el-badge :value="3" class="notification-badge">
        <el-button :icon="icons.Bell" :circle="true" />
      </el-badge>
      
      <el-dropdown class="user-dropdown" trigger="click">
        <span class="user-trigger">
          <el-avatar :size="32" icon="User" />
          <span>{{ currentUser.name }}</span>
          <el-icon :size="14"><component :is="icons.ArrowDown" /></el-icon>
        </span>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item :icon="icons.User" @click="navigateTo('/dashboard')">个人中心</el-dropdown-item>
            <el-dropdown-item :icon="icons.Setting">
              系统设置
              <el-dropdown-menu>
                <el-dropdown-item 
                  v-for="item in systemMenuItems" 
                  :key="item.path" 
                  @click="navigateTo(item.path)"
                >
                  <el-icon :size="16"><component :is="item.icon" /></el-icon>
                  <span>{{ item.name }}</span>
                </el-dropdown-item>
              </el-dropdown-menu>
            </el-dropdown-item>
            <el-dropdown-item :icon="icons.Brush">
              主题设置
              <el-dropdown-menu>
                <div class="theme-panel">
                  <div class="theme-section">
                    <span class="theme-label">背景颜色</span>
                    <div class="color-palette">
                      <div 
                        v-for="color in themeColors" 
                        :key="color.value"
                        class="color-swatch"
                        :class="{ active: currentTheme === color.value }"
                        :style="{ backgroundColor: color.value }"
                        @click="applyTheme(color.value)"
                        :title="color.name"
                      >
                        <el-icon v-if="currentTheme === color.value" :size="12" color="#fff"><component :is="icons.Check" /></el-icon>
                      </div>
                    </div>
                  </div>
                  <div class="theme-section">
                    <span class="theme-label">主题模式</span>
                    <div class="theme-mode-row">
                      <el-radio-group v-model="themeMode" size="small" @change="applyThemeMode">
                        <el-radio-button value="light">浅色</el-radio-button>
                        <el-radio-button value="dark">深色</el-radio-button>
                      </el-radio-group>
                    </div>
                  </div>
                </div>
              </el-dropdown-menu>
            </el-dropdown-item>
            <el-dropdown-item :icon="icons.SwitchButton" divided>退出登录</el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import * as icons from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()

const searchKeyword = ref('')
const currentProject = ref('智能测试平台项目')
const currentUser = ref({ name: '管理员', role: '超级管理员' })

const projects = [
  { id: 1, name: '智能测试平台项目' },
  { id: 2, name: '党建系统项目' },
  { id: 3, name: '电商平台项目' }
]

const systemMenuItems = [
  { path: '/project-management', name: '项目管理', icon: icons.Folder },
  { path: '/user-management', name: '用户管理', icon: icons.User },
  { path: '/role-permission', name: '角色权限管理', icon: icons.Lock },
  { path: '/log-management', name: '日志管理', icon: icons.Document },
  { path: '/data-backup', name: '数据备份配置', icon: icons.FolderChecked },
  { path: '/ai-config', name: 'AI配置', icon: icons.Cpu }
]

const themeColors = [
  { name: '靛紫', value: '#6366f1' },
  { name: '蓝', value: '#3b82f6' },
  { name: '翠绿', value: '#10b981' },
  { name: '橙', value: '#f59e0b' },
  { name: '玫红', value: '#ec4899' },
  { name: '青色', value: '#06b6d4' },
  { name: '紫', value: '#8b5cf6' },
  { name: '灰', value: '#6b7280' }
]

const currentTheme = ref('#6366f1')
const themeMode = ref('light')

const applyTheme = (color) => {
  currentTheme.value = color
  document.documentElement.style.setProperty('--theme-primary', color)
  
  const lighterColor = color + '20'
  const darkerColor = color + 'cc'
  document.documentElement.style.setProperty('--theme-primary-light', lighterColor)
  document.documentElement.style.setProperty('--theme-primary-dark', darkerColor)
  
  localStorage.setItem('theme-color', color)
}

const applyThemeMode = () => {
  if (themeMode.value === 'dark') {
    document.documentElement.classList.add('dark-mode')
  } else {
    document.documentElement.classList.remove('dark-mode')
  }
  localStorage.setItem('theme-mode', themeMode.value)
}

onMounted(() => {
  const savedTheme = localStorage.getItem('theme-color')
  if (savedTheme) {
    currentTheme.value = savedTheme
    applyTheme(savedTheme)
  }
  
  const savedMode = localStorage.getItem('theme-mode')
  if (savedMode) {
    themeMode.value = savedMode
    applyThemeMode()
  }
})

const navigateTo = (path) => {
  router.push(path)
}

const breadcrumbList = computed(() => {
  const pathMap = {
    '/dashboard': { name: '首页工作台' },
    '/ai-generate': { name: 'AI用例生成' },
    '/case-list': { name: '测试用例集管理' },
    '/case-archive': { name: '用例版本归档' },
    '/interface-environment': { name: '接口环境管理' },
    '/interface-cases': { name: '接口用例管理' },
    '/interface-scenarios': { name: '业务场景编排' },
    '/interface-tasks': { name: '接口任务管理' },
    '/interface-reports': { name: '接口执行报告' },
    '/ui-elements': { name: '页面元素管理' },
    '/ui-cases': { name: 'UI用例编排' },
    '/ui-tasks': { name: 'UI场景任务' },
    '/ui-reports': { name: 'UI执行报告' },
    '/ui-screenshots': { name: '失败截图记录' },
    '/manual-tasks': { name: '手动任务' },
    '/scheduled-tasks': { name: '定时任务' },
    '/ci-tasks': { name: 'CI触发任务' },
    '/task-logs': { name: '任务日志' },
    '/quality-stats': { name: '用例数据统计' },
    '/pass-rate': { name: '自动化通过率' },
    '/iteration-analysis': { name: '迭代质量分析' },
    '/report-export': { name: '报表导出' },
    '/project-management': { name: '项目管理' },
    '/user-management': { name: '用户管理' },
    '/role-permission': { name: '角色权限管理' },
    '/log-management': { name: '日志管理' },
    '/data-backup': { name: '数据备份配置' },
    '/ai-config': { name: 'AI配置' }
  }
  
  const currentPath = route.path
  const currentItem = pathMap[currentPath]
  
  if (!currentItem) {
    return [{ name: '首页', path: '/dashboard' }]
  }
  
  return [
    { name: '首页', path: '/dashboard' },
    currentItem
  ]
})
</script>

<style scoped>
.header-wrapper {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  height: 100%;
  background-color: var(--color-bg-card);
}

.header-left {
  flex: 1;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.project-selector {
  margin-right: 4px;
}

.project-trigger {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background-color: var(--color-bg-hover);
  border-radius: var(--radius-md);
  cursor: pointer;
  font-size: var(--font-size-sm);
  color: var(--color-text-primary);
  transition: background-color 0.2s;
}

.project-trigger:hover {
  background-color: var(--color-divider);
}

.search-box {
  width: 200px;
}

.search-input {
  border-radius: var(--radius-xl);
}

.notification-badge {
  margin-right: 4px;
}

.user-dropdown {
  margin-left: 4px;
}

.user-trigger {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 4px 12px 4px 4px;
  border-radius: var(--radius-xl);
  transition: background-color 0.2s;
}

.user-trigger:hover {
  background-color: var(--color-bg-hover);
}

.theme-panel {
  padding: 16px;
  min-width: 200px;
}

.theme-section {
  margin-bottom: 12px;
}

.theme-section:last-child {
  margin-bottom: 0;
}

.theme-label {
  font-size: var(--font-size-xs);
  color: var(--color-text-tertiary);
  display: block;
  margin-bottom: 8px;
  font-weight: var(--font-weight-medium);
}

.color-palette {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.color-swatch {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: transform 0.2s, box-shadow 0.2s;
  border: 2px solid transparent;
}

.color-swatch:hover {
  transform: scale(1.1);
}

.color-swatch.active {
  box-shadow: 0 0 0 2px var(--color-text-inverse), 0 0 0 4px var(--color-text-primary);
}

.theme-mode-row {
  display: flex;
  align-items: center;
}
</style>