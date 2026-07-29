<template>
  <div class="platform-settings">
    <div class="page-header">
      <div class="header-icon">
        <el-icon :size="28"><Setting /></el-icon>
      </div>
      <div class="header-text">
        <h1>平台设置</h1>
        <p class="header-desc">配置平台参数、告警规则和集成</p>
      </div>
    </div>

    <el-card class="settings-card" v-loading="loading" element-loading-text="加载配置中...">
      <el-tabs v-model="activeTab" class="settings-tabs">
        <!-- 通用设置 -->
        <el-tab-pane name="general">
          <template #label>
            <span class="tab-label"><el-icon><Document /></el-icon> 通用设置</span>
          </template>
          <el-form :model="settings.general" label-width="120px" class="settings-form">
            <div class="form-section">
              <h3 class="section-title">基础信息</h3>
              <div class="form-row">
                <el-form-item label="平台名称">
                  <el-input v-model="settings.general.platform_name" placeholder="请输入平台名称" />
                </el-form-item>
                <el-form-item label="平台版本">
                  <el-input v-model="settings.general.version" placeholder="如 1.0.0" />
                </el-form-item>
              </div>
              <el-form-item label="平台描述">
                <el-input
                  v-model="settings.general.description"
                  type="textarea"
                  :rows="3"
                  placeholder="请输入平台描述"
                  maxlength="200"
                  show-word-limit
                />
              </el-form-item>
              <div class="form-row">
                <el-form-item label="语言">
                  <el-select v-model="settings.general.language" style="width: 100%">
                    <el-option label="简体中文" value="zh-CN" />
                    <el-option label="English" value="en-US" />
                    <el-option label="日本語" value="ja-JP" />
                  </el-select>
                </el-form-item>
                <el-form-item label="时区">
                  <el-select v-model="settings.general.timezone" filterable style="width: 100%">
                    <el-option label="(UTC+08:00) 北京/上海" value="Asia/Shanghai" />
                    <el-option label="(UTC+00:00) 伦敦" value="Europe/London" />
                    <el-option label="(UTC-08:00) 太平洋时间" value="America/Los_Angeles" />
                    <el-option label="(UTC+09:00) 东京" value="Asia/Tokyo" />
                    <el-option label="(UTC+01:00) 巴黎" value="Europe/Paris" />
                  </el-select>
                </el-form-item>
              </div>
            </div>
          </el-form>
        </el-tab-pane>

        <!-- 性能测试 -->
        <el-tab-pane name="performance">
          <template #label>
            <span class="tab-label"><el-icon><Odometer /></el-icon> 性能测试</span>
          </template>
          <el-form :model="settings.performance" label-width="140px" class="settings-form">
            <div class="form-section">
              <h3 class="section-title">测试引擎</h3>
              <el-form-item label="默认引擎">
                <el-select v-model="settings.performance.default_engine" style="width: 100%">
                  <el-option label="Locust" value="locust" />
                  <el-option label="JMeter" value="jmeter" />
                  <el-option label="Gatling" value="gatling" />
                </el-select>
              </el-form-item>
              <div class="form-row">
                <el-form-item label="最大并发测试数">
                  <el-input-number v-model="settings.performance.max_concurrent_tests" :min="1" :max="100" controls-position="right" style="width: 100%" />
                </el-form-item>
                <el-form-item label="默认超时(秒)">
                  <el-input-number v-model="settings.performance.default_timeout" :min="60" :max="86400" :step="60" controls-position="right" style="width: 100%" />
                </el-form-item>
              </div>
            </div>
            <div class="form-section">
              <h3 class="section-title">监控与存储</h3>
              <div class="form-row">
                <el-form-item label="监控间隔(秒)">
                  <el-input-number v-model="settings.performance.monitoring_interval" :min="1" :max="3600" controls-position="right" style="width: 100%" />
                </el-form-item>
                <el-form-item label="数据保留(天)">
                  <el-input-number v-model="settings.performance.data_retention_days" :min="1" :max="365" controls-position="right" style="width: 100%" />
                </el-form-item>
              </div>
              <el-form-item label="指标存储">
                <el-select v-model="settings.performance.metrics_storage" style="width: 100%">
                  <el-option label="InfluxDB" value="influxdb" />
                  <el-option label="Prometheus" value="prometheus" />
                  <el-option label="TimescaleDB" value="timescaledb" />
                  <el-option label="MySQL" value="mysql" />
                </el-select>
              </el-form-item>
              <el-form-item label="自动清理过期数据">
                <el-switch v-model="settings.performance.auto_cleanup" />
              </el-form-item>
            </div>
          </el-form>
        </el-tab-pane>

        <!-- AI配置 -->
        <el-tab-pane name="ai">
          <template #label>
            <span class="tab-label"><el-icon><Cpu /></el-icon> AI配置</span>
          </template>
          <el-form :model="settings.ai" label-width="160px" class="settings-form">
            <div class="form-section">
              <h3 class="section-title">AI 分析开关</h3>
              <el-form-item label="启用 AI 分析">
                <el-switch v-model="settings.ai.enabled" />
              </el-form-item>
              <el-form-item label="自动瓶颈检测">
                <el-switch v-model="settings.ai.auto_bottleneck_detection" />
              </el-form-item>
              <el-form-item label="自动异常检测">
                <el-switch v-model="settings.ai.auto_anomaly_detection" />
              </el-form-item>
              <el-form-item label="自动场景生成">
                <el-switch v-model="settings.ai.auto_scenario_generation" />
              </el-form-item>
            </div>
            <div class="form-section">
              <h3 class="section-title">高级参数</h3>
              <div class="form-row">
                <el-form-item label="模型更新间隔(小时)">
                  <el-input-number v-model="settings.ai.model_update_interval" :min="1" :max="168" controls-position="right" style="width: 100%" />
                </el-form-item>
                <el-form-item label="置信度阈值">
                  <el-input-number
                    v-model="settings.ai.confidence_threshold"
                    :min="0"
                    :max="1"
                    :step="0.05"
                    :precision="2"
                    controls-position="right"
                    style="width: 100%"
                  />
                </el-form-item>
              </div>
            </div>
          </el-form>
        </el-tab-pane>

        <!-- 告警规则 -->
        <el-tab-pane name="alerts">
          <template #label>
            <span class="tab-label"><el-icon><Bell /></el-icon> 告警规则</span>
          </template>
          <el-form :model="settings.alerts" label-width="140px" class="settings-form">
            <div class="form-section">
              <h3 class="section-title">告警通道</h3>
              <div class="form-row">
                <el-form-item label="启用邮件告警">
                  <el-switch v-model="settings.alerts.email_enabled" />
                </el-form-item>
                <el-form-item label="启用 Webhook 告警">
                  <el-switch v-model="settings.alerts.webhook_enabled" />
                </el-form-item>
              </div>
              <el-form-item label="告警接收人">
                <el-select
                  v-model="settings.alerts.recipients"
                  multiple
                  filterable
                  allow-create
                  default-first-option
                  :reserve-keyword="false"
                  placeholder="输入邮箱后按回车添加"
                  style="width: 100%"
                >
                  <el-option
                    v-for="r in settings.alerts.recipients"
                    :key="r"
                    :label="r"
                    :value="r"
                  />
                </el-select>
              </el-form-item>
              <el-form-item label="Webhook URL">
                <el-input v-model="settings.alerts.webhook_url" placeholder="https://hooks.example.com/..." />
              </el-form-item>
            </div>
            <div class="form-section">
              <div class="section-title-bar">
                <h3 class="section-title">告警规则列表</h3>
                <el-button type="primary" :icon="Plus" size="small" @click="addAlertRule">添加规则</el-button>
              </div>
              <el-table :data="settings.alerts.rules" border stripe class="rules-table">
                <el-table-column label="指标" min-width="160">
                  <template #default="{ row }">
                    <el-input v-model="row.metric" placeholder="如 response_time" size="small" />
                  </template>
                </el-table-column>
                <el-table-column label="阈值" width="150">
                  <template #default="{ row }">
                    <el-input-number v-model="row.threshold" :min="0" controls-position="right" size="small" style="width: 100%" />
                  </template>
                </el-table-column>
                <el-table-column label="操作符" width="120">
                  <template #default="{ row }">
                    <el-select v-model="row.operator" size="small">
                      <el-option label=">" value=">" />
                      <el-option label="<" value="<" />
                      <el-option label="=" value="=" />
                      <el-option label=">=" value=">=" />
                      <el-option label="<=" value="<=" />
                    </el-select>
                  </template>
                </el-table-column>
                <el-table-column label="严重级别" width="140">
                  <template #default="{ row }">
                    <el-select v-model="row.severity" size="small">
                      <el-option label="信息" value="info" />
                      <el-option label="警告" value="warning" />
                      <el-option label="错误" value="error" />
                      <el-option label="严重" value="critical" />
                    </el-select>
                  </template>
                </el-table-column>
                <el-table-column label="操作" width="80" align="center">
                  <template #default="{ $index }">
                    <el-button type="danger" :icon="Delete" circle size="small" @click="removeAlertRule($index)" />
                  </template>
                </el-table-column>
              </el-table>
              <el-empty v-if="settings.alerts.rules.length === 0" description="暂无告警规则，点击右上角添加" />
            </div>
          </el-form>
        </el-tab-pane>

        <!-- 集成配置 -->
        <el-tab-pane name="integrations">
          <template #label>
            <span class="tab-label"><el-icon><Connection /></el-icon> 集成配置</span>
          </template>
          <el-form label-width="120px" class="settings-form">
            <div class="form-section">
              <h3 class="section-title">
                <el-icon><Link /></el-icon> JIRA
                <el-switch v-model="settings.integrations.jira.enabled" class="section-switch" />
              </h3>
              <div class="form-row">
                <el-form-item label="服务地址">
                  <el-input v-model="settings.integrations.jira.url" placeholder="https://your-domain.atlassian.net" :disabled="!settings.integrations.jira.enabled" />
                </el-form-item>
                <el-form-item label="Access Token">
                  <el-input v-model="settings.integrations.jira.token" type="password" show-password placeholder="请输入 Token" :disabled="!settings.integrations.jira.enabled" />
                </el-form-item>
              </div>
            </div>
            <div class="form-section">
              <h3 class="section-title">
                <el-icon><ChatDotRound /></el-icon> Slack
                <el-switch v-model="settings.integrations.slack.enabled" class="section-switch" />
              </h3>
              <el-form-item label="Webhook">
                <el-input v-model="settings.integrations.slack.webhook" placeholder="https://hooks.slack.com/services/..." :disabled="!settings.integrations.slack.enabled" />
              </el-form-item>
            </div>
            <div class="form-section">
              <h3 class="section-title">
                <el-icon><DataLine /></el-icon> Grafana
                <el-switch v-model="settings.integrations.grafana.enabled" class="section-switch" />
              </h3>
              <div class="form-row">
                <el-form-item label="服务地址">
                  <el-input v-model="settings.integrations.grafana.url" placeholder="http://localhost:3000" :disabled="!settings.integrations.grafana.enabled" />
                </el-form-item>
                <el-form-item label="仪表盘 UID">
                  <el-input v-model="settings.integrations.grafana.dashboard" placeholder="请输入 Dashboard UID" :disabled="!settings.integrations.grafana.enabled" />
                </el-form-item>
              </div>
            </div>
            <div class="form-section">
              <h3 class="section-title">
                <el-icon><Monitor /></el-icon> Prometheus
                <el-switch v-model="settings.integrations.prometheus.enabled" class="section-switch" />
              </h3>
              <el-form-item label="服务地址">
                <el-input v-model="settings.integrations.prometheus.url" placeholder="http://localhost:9090" :disabled="!settings.integrations.prometheus.enabled" />
              </el-form-item>
            </div>
            <div class="form-section">
              <h3 class="section-title">
                <el-icon><Tickets /></el-icon> 禅道 (Zentao)
                <el-switch v-model="settings.integrations.zentao.enabled" class="section-switch" />
              </h3>
              <div class="form-row">
                <el-form-item label="服务地址">
                  <el-input v-model="settings.integrations.zentao.url" placeholder="http://zentao.example.com" :disabled="!settings.integrations.zentao.enabled" />
                </el-form-item>
                <el-form-item label="默认项目">
                  <el-input v-model="settings.integrations.zentao.project" placeholder="默认项目ID" :disabled="!settings.integrations.zentao.enabled" />
                </el-form-item>
              </div>
              <div class="form-row">
                <el-form-item label="账号">
                  <el-input v-model="settings.integrations.zentao.account" placeholder="禅道登录账号" :disabled="!settings.integrations.zentao.enabled" />
                </el-form-item>
                <el-form-item label="密码">
                  <el-input v-model="settings.integrations.zentao.password" type="password" show-password placeholder="禅道登录密码" :disabled="!settings.integrations.zentao.enabled" />
                </el-form-item>
              </div>
              <div class="form-row">
                <el-form-item label="默认严重程度">
                  <el-select v-model="settings.integrations.zentao.default_severity" :disabled="!settings.integrations.zentao.enabled" style="width: 100%">
                    <el-option label="1-致命" :value="1" />
                    <el-option label="2-严重" :value="2" />
                    <el-option label="3-一般" :value="3" />
                    <el-option label="4-轻微" :value="4" />
                  </el-select>
                </el-form-item>
                <el-form-item label="默认优先级">
                  <el-select v-model="settings.integrations.zentao.default_priority" :disabled="!settings.integrations.zentao.enabled" style="width: 100%">
                    <el-option label="1-紧急" :value="1" />
                    <el-option label="2-高" :value="2" />
                    <el-option label="3-中" :value="3" />
                    <el-option label="4-低" :value="4" />
                  </el-select>
                </el-form-item>
              </div>
              <el-form-item label="连接测试">
                <el-button type="primary" @click="testZentaoConnection" :disabled="!settings.integrations.zentao.enabled" :loading="zentaoTesting">
                  测试连接
                </el-button>
                <span v-if="zentaoTestResult" :style="{ color: zentaoTestResult.success ? '#67c23a' : '#f56c6c', marginLeft: '10px' }">
                  {{ zentaoTestResult.message }}
                </span>
              </el-form-item>
            </div>
          </el-form>
        </el-tab-pane>

        <!-- 安全设置 -->
        <el-tab-pane name="security">
          <template #label>
            <span class="tab-label"><el-icon><Lock /></el-icon> 安全设置</span>
          </template>
          <el-form :model="settings.security" label-width="140px" class="settings-form">
            <div class="form-section">
              <h3 class="section-title">会话与登录</h3>
              <div class="form-row">
                <el-form-item label="会话超时(分钟)">
                  <el-input-number v-model="settings.security.session_timeout" :min="5" :max="1440" controls-position="right" style="width: 100%" />
                </el-form-item>
                <el-form-item label="最大登录尝试次数">
                  <el-input-number v-model="settings.security.max_login_attempts" :min="3" :max="20" controls-position="right" style="width: 100%" />
                </el-form-item>
              </div>
            </div>
            <div class="form-section">
              <h3 class="section-title">密码策略</h3>
              <el-form-item label="最小密码长度">
                <el-input-number v-model="settings.security.password_policy.min_length" :min="6" :max="32" controls-position="right" style="width: 100%" />
              </el-form-item>
              <div class="form-row">
                <el-form-item label="需要大写字母">
                  <el-switch v-model="settings.security.password_policy.require_uppercase" />
                </el-form-item>
                <el-form-item label="需要小写字母">
                  <el-switch v-model="settings.security.password_policy.require_lowercase" />
                </el-form-item>
              </div>
              <div class="form-row">
                <el-form-item label="需要数字">
                  <el-switch v-model="settings.security.password_policy.require_digit" />
                </el-form-item>
                <el-form-item label="需要特殊字符">
                  <el-switch v-model="settings.security.password_policy.require_special" />
                </el-form-item>
              </div>
            </div>
            <div class="form-section">
              <h3 class="section-title">访问控制</h3>
              <el-form-item label="IP 白名单">
                <el-input
                  v-model="settings.security.ip_whitelist"
                  type="textarea"
                  :rows="3"
                  placeholder="每行一个 IP 或 CIDR，如 192.168.1.0/24"
                />
              </el-form-item>
              <el-form-item label="启用审计日志">
                <el-switch v-model="settings.security.audit_log" />
              </el-form-item>
            </div>
          </el-form>
        </el-tab-pane>

        <!-- 扩展性 -->
        <el-tab-pane name="scalability">
          <template #label>
            <span class="tab-label"><el-icon><Expand /></el-icon> 扩展性</span>
          </template>
          <el-form :model="settings.scalability" label-width="160px" class="settings-form">
            <div class="form-section">
              <h3 class="section-title">容量限制</h3>
              <div class="form-row">
                <el-form-item label="最大项目数">
                  <el-input-number v-model="settings.scalability.max_projects" :min="1" :max="10000" controls-position="right" style="width: 100%" />
                </el-form-item>
                <el-form-item label="每项目最大用户数">
                  <el-input-number v-model="settings.scalability.max_users_per_project" :min="1" :max="10000" controls-position="right" style="width: 100%" />
                </el-form-item>
              </div>
              <div class="form-row">
                <el-form-item label="最大测试用例数">
                  <el-input-number v-model="settings.scalability.max_test_cases" :min="100" :max="1000000" :step="100" controls-position="right" style="width: 100%" />
                </el-form-item>
                <el-form-item label="最大并发用户数">
                  <el-input-number v-model="settings.scalability.max_concurrent_users" :min="10" :max="100000" :step="10" controls-position="right" style="width: 100%" />
                </el-form-item>
              </div>
            </div>
          </el-form>
        </el-tab-pane>
      </el-tabs>

      <div class="settings-actions">
        <el-button @click="loadSettings" :icon="RefreshLeft">重载</el-button>
        <el-button type="primary" @click="saveSettings" :loading="saving" :icon="Check">
          {{ saving ? '保存中...' : '保存设置' }}
        </el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Setting, Document, Odometer, Cpu, Bell, Connection, Link, ChatDotRound,
  DataLine, Monitor, Lock, Expand, Plus, Delete, Check, RefreshLeft, Tickets
} from '@element-plus/icons-vue'

const activeTab = ref('general')
const loading = ref(false)
const saving = ref(false)
const zentaoTesting = ref(false)
const zentaoTestResult = ref(null)

const defaultSettings = () => ({
  general: {
    platform_name: '自动化测试平台',
    version: '1.0.0',
    description: '',
    language: 'zh-CN',
    timezone: 'Asia/Shanghai'
  },
  performance: {
    default_engine: 'locust',
    max_concurrent_tests: 10,
    default_timeout: 3600,
    monitoring_interval: 5,
    data_retention_days: 30,
    auto_cleanup: true,
    metrics_storage: 'influxdb'
  },
  ai: {
    enabled: false,
    auto_bottleneck_detection: false,
    auto_anomaly_detection: false,
    auto_scenario_generation: false,
    model_update_interval: 24,
    confidence_threshold: 0.8
  },
  alerts: {
    email_enabled: false,
    webhook_enabled: false,
    recipients: [],
    webhook_url: '',
    rules: [
      { metric: 'response_time', threshold: 2000, operator: '>', severity: 'warning' }
    ]
  },
  integrations: {
    jira: { enabled: false, url: '', token: '' },
    slack: { enabled: false, webhook: '' },
    grafana: { enabled: false, url: '', dashboard: '' },
    prometheus: { enabled: false, url: '' },
    zentao: { enabled: false, url: '', account: '', password: '', project: '', default_severity: 3, default_priority: 3 }
  },
  security: {
    session_timeout: 30,
    max_login_attempts: 5,
    password_policy: {
      min_length: 8,
      require_uppercase: true,
      require_lowercase: true,
      require_digit: true,
      require_special: false
    },
    ip_whitelist: '',
    audit_log: true
  },
  scalability: {
    max_projects: 100,
    max_users_per_project: 50,
    max_test_cases: 10000,
    max_concurrent_users: 500
  }
})

const settings = reactive(defaultSettings())

const addAlertRule = () => {
  settings.alerts.rules.push({ metric: '', threshold: 0, operator: '>', severity: 'warning' })
}

const removeAlertRule = (index) => {
  settings.alerts.rules.splice(index, 1)
}

const testZentaoConnection = async () => {
  zentaoTesting.value = true
  zentaoTestResult.value = null
  try {
    const zentao = settings.integrations.zentao
    const res = await fetch('/api/v1/bugs/test_connection', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        base_url: zentao.url,
        account: zentao.account,
        password: zentao.password
      })
    })
    const json = await res.json()
    zentaoTestResult.value = {
      success: json.success,
      message: json.message
    }
    if (json.success) {
      ElMessage.success('禅道连接成功')
    } else {
      ElMessage.error(json.message || '连接失败')
    }
  } catch (e) {
    console.error('测试禅道连接失败:', e)
    zentaoTestResult.value = {
      success: false,
      message: '网络错误或请求超时'
    }
    ElMessage.error('测试连接失败')
  } finally {
    zentaoTesting.value = false
  }
}

const loadSettings = async () => {
  loading.value = true
  try {
    const res = await fetch('/api/v1/platform/settings')
    const json = await res.json()
    const data = json.data || json
    const loaded = json.settings || data.settings || data
    if (loaded && typeof loaded === 'object') {
      mergeSettings(settings, loaded)
    }
  } catch (e) {
    console.error('加载平台设置失败:', e)
    ElMessage.error('加载平台设置失败')
  } finally {
    loading.value = false
  }
}

const mergeSettings = (target, source) => {
  Object.keys(target).forEach(key => {
    if (source && Object.prototype.hasOwnProperty.call(source, key)) {
      const srcVal = source[key]
      if (srcVal && typeof srcVal === 'object' && !Array.isArray(srcVal)) {
        mergeSettings(target[key], srcVal)
      } else {
        target[key] = srcVal
      }
    }
  })
}

const saveSettings = async () => {
  saving.value = true
  try {
    const res = await fetch('/api/v1/platform/settings', {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(settings)
    })
    const json = await res.json()
    const data = json.data || json
    if (json.success !== false && res.ok) {
      ElMessage.success(json.message || data.message || '保存成功')
    } else {
      ElMessage.error(json.detail || json.message || '保存失败')
    }
  } catch (e) {
    console.error('保存平台设置失败:', e)
    ElMessage.error('保存失败，请检查网络连接')
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  loadSettings()
})
</script>

<style scoped>
.platform-settings {
  padding: 24px;
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e8ec 100%);
}

.page-header {
  display: flex;
  align-items: center;
  gap: 18px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 22px 28px;
  border-radius: 14px;
  margin-bottom: 20px;
  box-shadow: 0 4px 20px rgba(102, 126, 234, 0.3);
}

.header-icon {
  width: 56px;
  height: 56px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  flex-shrink: 0;
}

.header-text h1 {
  color: #fff;
  font-size: 26px;
  font-weight: 700;
  margin: 0 0 6px 0;
}

.header-desc {
  color: rgba(255, 255, 255, 0.85);
  font-size: 14px;
  margin: 0;
}

.settings-card {
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
  min-height: 480px;
}

.settings-tabs :deep(.el-tabs__header) {
  margin-bottom: 20px;
}

.settings-tabs :deep(.el-tabs__nav-wrap)::after {
  height: 1px;
}

.settings-tabs :deep(.el-tabs__item) {
  font-size: 15px;
  height: 46px;
}

.tab-label {
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.settings-form {
  max-width: 860px;
  padding: 8px 4px;
}

.form-section {
  margin-bottom: 28px;
}

.form-section:last-child {
  margin-bottom: 0;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 15px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 18px;
  padding-bottom: 10px;
  border-bottom: 2px solid #ebeef5;
}

.section-switch {
  margin-left: auto;
}

.section-title-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 18px;
  padding-bottom: 10px;
  border-bottom: 2px solid #ebeef5;
}

.section-title-bar .section-title {
  margin-bottom: 0;
  padding-bottom: 0;
  border-bottom: none;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 18px;
}

.form-row .el-form-item {
  margin-bottom: 18px;
}

.rules-table {
  width: 100%;
}

.settings-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 24px;
  padding-top: 20px;
  border-top: 1px solid #ebeef5;
}

.settings-actions .el-button {
  min-width: 110px;
}

@media (max-width: 768px) {
  .platform-settings {
    padding: 16px;
  }
  .form-row {
    grid-template-columns: 1fr;
  }
  .settings-actions {
    flex-direction: column-reverse;
  }
  .settings-actions .el-button {
    width: 100%;
  }
}
</style>
