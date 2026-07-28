import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    redirect: '/dashboard'
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('../views/Dashboard.vue')
  },
  {
    path: '/ai-generate',
    name: 'AIGenerate',
    component: () => import('../views/AICaseGenerator.vue')
  },
  {
    path: '/case-list',
    name: 'CaseList',
    component: () => import('../views/CaseList.vue')
  },
  {
    path: '/case-import-export',
    name: 'CaseImportExport',
    component: () => import('../views/CaseImportExport.vue')
  },
  {
    path: '/case-archive',
    name: 'CaseArchive',
    component: () => import('../views/CaseArchive.vue')
  },
  {
    path: '/interface-environment',
    name: 'ApiEnvironment',
    component: () => import('../views/ApiEnvironment.vue')
  },
  {
    path: '/interface-cases',
    name: 'ApiCases',
    component: () => import('../views/ApiCases.vue')
  },
  {
    path: '/interface-scenarios',
    name: 'ApiScenarios',
    component: () => import('../views/ApiScenarios.vue')
  },
  {
    path: '/interface-tasks',
    name: 'ApiTasks',
    component: () => import('../views/ApiTasks.vue')
  },
  {
    path: '/interface-reports',
    name: 'ApiReports',
    component: () => import('../views/ApiReports.vue')
  },
  {
    path: '/ui-elements',
    name: 'UiElements',
    component: () => import('../views/UiElements.vue')
  },
  {
    path: '/ui-cases',
    name: 'UiCases',
    component: () => import('../views/UiCases.vue')
  },
  {
    path: '/ui-tasks',
    name: 'UiTasks',
    component: () => import('../views/UiTasks.vue')
  },
  {
    path: '/ui-reports',
    name: 'UiReports',
    component: () => import('../views/UiReports.vue')
  },
  {
    path: '/ui-screenshots',
    name: 'UiScreenshots',
    component: () => import('../views/UiScreenshots.vue')
  },
  {
    path: '/manual-tasks',
    name: 'ManualTasks',
    component: () => import('../views/ManualTasks.vue')
  },
  {
    path: '/scheduled-tasks',
    name: 'ScheduledTasks',
    component: () => import('../views/ScheduledTasks.vue')
  },
  {
    path: '/ci-tasks',
    name: 'CiTasks',
    component: () => import('../views/CiTasks.vue')
  },
  {
    path: '/task-logs',
    name: 'TaskLogs',
    component: () => import('../views/TaskLogs.vue')
  },
  {
    path: '/quality-stats',
    name: 'QualityStats',
    component: () => import('../views/QualityStats.vue')
  },
  {
    path: '/pass-rate',
    name: 'PassRate',
    component: () => import('../views/PassRate.vue')
  },
  {
    path: '/iteration-analysis',
    name: 'IterationAnalysis',
    component: () => import('../views/IterationAnalysis.vue')
  },
  {
    path: '/report-export',
    name: 'ReportExport',
    component: () => import('../views/ReportExport.vue')
  },
  {
    path: '/project-management',
    name: 'ProjectManagement',
    component: () => import('../views/ProjectManagement.vue')
  },
  {
    path: '/user-management',
    name: 'UserManagement',
    component: () => import('../views/UserManagement.vue')
  },
  {
    path: '/role-permission',
    name: 'RolePermission',
    component: () => import('../views/RolePermission.vue')
  },
  {
    path: '/log-management',
    name: 'LogManagement',
    component: () => import('../views/LogManagement.vue')
  },
  {
    path: '/data-backup',
    name: 'DataBackup',
    component: () => import('../views/DataBackup.vue')
  },
  {
    path: '/ai-config',
    name: 'AiConfig',
    component: () => import('../views/AiConfig.vue')
  },
  {
    path: '/perf-tests',
    name: 'PerfTests',
    component: () => import('../views/PerfTests.vue')
  },
  {
    path: '/perf-monitor',
    name: 'PerfMonitor',
    component: () => import('../views/PerfMonitor.vue')
  },
  {
    path: '/perf-reports',
    name: 'PerfReports',
    component: () => import('../views/PerfReports.vue')
  },
  {
    path: '/ai-bottleneck',
    name: 'AIBottleneck',
    component: () => import('../views/AIBottleneck.vue')
  },
  {
    path: '/anomaly-detection',
    name: 'AnomalyDetection',
    component: () => import('../views/AnomalyDetection.vue')
  },
  {
    path: '/ai-scenario',
    name: 'AIScenario',
    component: () => import('../views/AIScenario.vue')
  },
  {
    path: '/predictive-analysis',
    name: 'PredictiveAnalysis',
    component: () => import('../views/PredictiveAnalysis.vue')
  },
  {
    path: '/ai-models',
    name: 'AIModels',
    component: () => import('../views/AIModels.vue')
  },
  {
    path: '/platform-settings',
    name: 'PlatformSettings',
    component: () => import('../views/PlatformSettings.vue')
  },
  {
    path: '/cases',
    redirect: '/case-list'
  },
  {
    path: '/coverage',
    redirect: '/quality-stats'
  },
  {
    path: '/export',
    redirect: '/report-export'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router