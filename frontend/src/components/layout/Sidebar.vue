<template>
  <div class="sidebar-wrapper">
    <div class="logo-section" :class="{ collapsed: collapsed }">
      <div class="logo-icon-wrapper">
        <el-icon class="logo-icon" size="24"><component :is="icons.Box" /></el-icon>
      </div>
      <span v-if="!collapsed" class="logo-text">智能测试平台</span>
    </div>
    
    <div class="menu-container">
      <el-menu 
        :active="activeMenu" 
        class="sidebar-menu" 
        :collapse="collapsed"
        :collapse-transition="false"
        background-color="#1f2937"
        text-color="#9ca3af"
        active-text-color="#6366f1"
        router
        :default-openeds="openedMenus"
      >
        <template v-for="menu in menuItems" :key="menu.id">
          <el-menu-item v-if="!menu.children" :index="menu.path">
            <el-icon :size="18"><component :is="menu.icon" /></el-icon>
            <template #title>{{ menu.name }}</template>
          </el-menu-item>
          
          <el-sub-menu v-else :index="menu.id">
            <template #title>
              <el-icon :size="18"><component :is="menu.icon" /></el-icon>
              <span class="menu-title">{{ menu.name }}</span>
            </template>
            <el-menu-item 
              v-for="child in menu.children" 
              :key="child.id" 
              :index="child.path"
              class="sub-menu-item"
            >
              <el-icon v-if="child.icon" :size="14" class="child-icon"><component :is="child.icon" /></el-icon>
              <span class="child-name">{{ child.name }}</span>
            </el-menu-item>
          </el-sub-menu>
        </template>
      </el-menu>
    </div>
    
    <div class="collapse-btn" @click="$emit('toggle')">
      <el-icon :size="20"><component :is="collapsed ? icons.ArrowRight : icons.ArrowLeft" /></el-icon>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import * as icons from '@element-plus/icons-vue'

const props = defineProps({
  collapsed: {
    type: Boolean,
    default: false
  }
})

defineEmits(['toggle'])

const route = useRoute()

const activeMenu = computed(() => {
  return route.path
})

const openedMenus = computed(() => {
  const path = route.path
  const result = []
  
  menuItems.forEach(menu => {
    if (menu.children) {
      const hasActiveChild = menu.children.some(child => child.path === path)
      if (hasActiveChild) {
        result.push(menu.id)
      }
    }
  })
  
  return result
})

const menuItems = [
  {
    id: 'dashboard',
    name: '首页工作台',
    path: '/dashboard',
    icon: icons.DataBoard
  },
  {
    id: 'ai-cases',
    name: 'AI智能用例管理',
    icon: icons.MagicStick,
    children: [
      { id: 'ai-generate', name: 'AI用例生成', path: '/ai-generate', icon: icons.MagicStick },
      { id: 'case-list', name: '测试用例集管理', path: '/case-list', icon: icons.Document },
      { id: 'case-archive', name: '用例版本归档', path: '/case-archive', icon: icons.CollectionTag }
    ]
  },
  {
    id: 'api-automation',
    name: '接口自动化测试',
    icon: icons.Connection,
    children: [
      { id: 'api-environment', name: '接口环境管理', path: '/interface-environment', icon: icons.Connection },
      { id: 'api-cases', name: '接口用例管理', path: '/interface-cases', icon: icons.Document },
      { id: 'api-scenarios', name: '业务场景编排', path: '/interface-scenarios', icon: icons.Share },
      { id: 'api-tasks', name: '接口任务管理', path: '/interface-tasks', icon: icons.List },
      { id: 'api-reports', name: '接口执行报告', path: '/interface-reports', icon: icons.DataLine }
    ]
  },
  {
    id: 'ui-automation',
    name: 'UI自动化测试',
    icon: icons.Monitor,
    children: [
      { id: 'ui-elements', name: '页面元素管理', path: '/ui-elements', icon: icons.Grid },
      { id: 'ui-cases', name: 'UI用例编排', path: '/ui-cases', icon: icons.Document },
      { id: 'ui-tasks', name: 'UI场景任务', path: '/ui-tasks', icon: icons.List },
      { id: 'ui-reports', name: 'UI执行报告', path: '/ui-reports', icon: icons.DataLine },
      { id: 'ui-screenshots', name: '失败截图记录', path: '/ui-screenshots', icon: icons.Picture }
    ]
  },
  {
    id: 'task-center',
    name: '测试任务中心',
    icon: icons.Clock,
    children: [
      { id: 'manual-tasks', name: '手动任务', path: '/manual-tasks', icon: icons.Pointer },
      { id: 'scheduled-tasks', name: '定时任务', path: '/scheduled-tasks', icon: icons.Timer },
      { id: 'ci-tasks', name: 'CI触发任务', path: '/ci-tasks', icon: icons.Refresh },
      { id: 'task-logs', name: '任务日志', path: '/task-logs', icon: icons.Notebook }
    ]
  },
  {
    id: 'quality-dashboard',
    name: '质量统计大盘',
    icon: icons.TrendCharts,
    children: [
      { id: 'quality-stats', name: '用例数据统计', path: '/quality-stats', icon: icons.DataAnalysis },
      { id: 'pass-rate', name: '自动化通过率', path: '/pass-rate', icon: icons.CircleCheck },
      { id: 'iteration-analysis', name: '迭代质量分析', path: '/iteration-analysis', icon: icons.Files },
      { id: 'report-export', name: '报表导出', path: '/report-export', icon: icons.Download }
    ]
  },
  {
    id: 'perf-center',
    name: '性能测试中心',
    icon: icons.Odometer,
    children: [
      { id: 'perf-tests', name: '性能测试管理', path: '/perf-tests', icon: icons.Cpu },
      { id: 'perf-monitor', name: '实时监控', path: '/perf-monitor', icon: icons.Monitor },
      { id: 'perf-reports', name: '性能报告', path: '/perf-reports', icon: icons.DataLine }
    ]
  },
  {
    id: 'ai-perf',
    name: 'AI性能分析',
    icon: icons.MagicStick,
    children: [
      { id: 'ai-bottleneck', name: 'AI瓶颈分析', path: '/ai-bottleneck', icon: icons.Aim },
      { id: 'anomaly-detection', name: '异常检测', path: '/anomaly-detection', icon: icons.Warning },
      { id: 'ai-scenario', name: '智能场景生成', path: '/ai-scenario', icon: icons.MagicStick },
      { id: 'predictive-analysis', name: '预测性分析', path: '/predictive-analysis', icon: icons.DataLine },
      { id: 'ai-models', name: 'AI模型管理', path: '/ai-models', icon: icons.Cpu }
    ]
  },
  {
    id: 'platform-config',
    name: '平台设置',
    icon: icons.SetUp,
    children: [
      { id: 'platform-settings', name: '平台配置', path: '/platform-settings', icon: icons.SetUp }
    ]
  }
]
</script>

<style scoped>
.sidebar-wrapper {
  height: 100%;
  display: flex;
  flex-direction: column;
  position: relative;
}

.logo-section {
  display: flex;
  align-items: center;
  padding: 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  gap: 12px;
  transition: all 0.3s ease;
  flex-shrink: 0;
}

.logo-section.collapsed {
  justify-content: center;
  padding: 16px 8px;
}

.logo-icon-wrapper {
  width: 36px;
  height: 36px;
  background: linear-gradient(135deg, var(--theme-primary) 0%, var(--theme-primary-dark) 100%);
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.logo-icon {
  color: #fff;
}

.logo-text {
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-semibold);
  color: #fff;
  white-space: nowrap;
  letter-spacing: 0.5px;
}

.menu-container {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  scrollbar-width: thin;
  scrollbar-color: rgba(255, 255, 255, 0.2) transparent;
}

.menu-container::-webkit-scrollbar {
  width: 4px;
}

.menu-container::-webkit-scrollbar-track {
  background: transparent;
}

.menu-container::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.15);
  border-radius: 2px;
}

.menu-container::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.25);
}

.sidebar-menu {
  border-right: none !important;
  padding-bottom: 56px;
  background: transparent !important;
}

.sidebar-menu:not(.el-menu--collapse) {
  width: 220px;
}

.sidebar-menu .el-menu-item {
  margin: 2px 8px;
  border-radius: var(--radius-md);
  height: 40px;
  line-height: 40px;
  transition: all 0.2s ease;
  color: rgba(255, 255, 255, 0.65) !important;
}

.sidebar-menu .el-menu-item:hover {
  background-color: rgba(255, 255, 255, 0.06);
  color: #fff !important;
}

.sidebar-menu .el-menu-item.is-active {
  background: linear-gradient(90deg, rgba(0, 136, 102, 0.25) 0%, rgba(0, 136, 102, 0.05) 100%);
  color: #fff !important;
  font-weight: var(--font-weight-medium);
  position: relative;
}

.sidebar-menu .el-menu-item.is-active::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 3px;
  height: 20px;
  background: var(--theme-primary);
  border-radius: 0 3px 3px 0;
}

.sidebar-menu .el-sub-menu__title {
  margin: 2px 8px;
  border-radius: var(--radius-md);
  height: 40px;
  line-height: 40px;
  transition: all 0.2s ease;
  color: rgba(255, 255, 255, 0.65) !important;
}

.sidebar-menu .el-sub-menu__title:hover {
  background-color: rgba(255, 255, 255, 0.06);
  color: #fff !important;
}

.sidebar-menu .el-sub-menu__title .menu-title {
  font-weight: var(--font-weight-medium);
}

.sidebar-menu .el-sub-menu.is-active > .el-sub-menu__title {
  color: #fff !important;
}

.sidebar-menu .el-sub-menu.is-opened > .el-sub-menu__title {
  background-color: rgba(255, 255, 255, 0.06);
  color: #fff !important;
}

.sidebar-menu .el-sub-menu .el-menu-item {
  padding-left: 44px !important;
  margin: 2px 8px;
  height: 36px;
  line-height: 36px;
  position: relative;
  color: rgba(255, 255, 255, 0.55) !important;
}

.sidebar-menu .el-sub-menu .el-menu-item.sub-menu-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.sidebar-menu .el-sub-menu .el-menu-item .child-icon {
  color: rgba(255, 255, 255, 0.5);
  flex-shrink: 0;
}

.sidebar-menu .el-sub-menu .el-menu-item:hover .child-icon {
  color: var(--theme-primary);
}

.sidebar-menu .el-sub-menu .el-menu-item.is-active .child-icon {
  color: var(--theme-primary);
}

.sidebar-menu .el-sub-menu .el-menu-item.is-active {
  background-color: rgba(0, 136, 102, 0.15) !important;
  color: #fff !important;
}

.sidebar-menu .el-menu--collapse .el-menu-item,
.sidebar-menu .el-menu--collapse .el-sub-menu__title {
  margin: 2px 4px;
}

.sidebar-menu .el-menu--collapse .el-sub-menu .el-menu-item {
  padding-left: 48px !important;
}

.sidebar-menu .el-menu--collapse .child-icon {
  display: none;
}

.collapse-btn {
  position: absolute;
  bottom: 12px;
  left: 50%;
  transform: translateX(-50%);
  width: 36px;
  height: 36px;
  border-radius: var(--radius-md);
  background-color: rgba(255, 255, 255, 0.08);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: rgba(255, 255, 255, 0.6);
  transition: all 0.2s ease;
  z-index: 10;
}

.collapse-btn:hover {
  background-color: var(--theme-primary);
  color: #fff;
}
</style>