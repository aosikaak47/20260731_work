<template>
  <div class="ai-config-page">
    <el-dialog 
      v-model="authDialogVisible" 
      title="AI配置中心 - 身份验证" 
      width="420px" 
      :close-on-click-modal="false"
      :close-on-press-escape="false"
      :show-close="false"
      class="auth-dialog"
    >
      <div class="auth-content">
        <div class="auth-icon">
          <el-icon :size="48"><Key /></el-icon>
        </div>
        <h3 class="auth-title">请输入访问密码</h3>
        <p class="auth-desc">AI配置中心需要验证身份才能访问</p>
        
        <el-form label-width="0" class="auth-form">
          <el-form-item>
            <el-input 
              v-model="authPassword" 
              type="password" 
              placeholder="请输入访问密码"
              show-password
              @keyup.enter="handleAuth"
              class="auth-input"
            >
              <template #prefix>
                <el-icon><Lock /></el-icon>
              </template>
            </el-input>
          </el-form-item>
        </el-form>
        
        <div class="auth-error" v-if="authError">
          <el-icon><Warning /></el-icon>
          <span>{{ authError }}</span>
        </div>
        
        <div class="auth-actions">
          <el-button type="primary" @click="handleAuth" :loading="authLoading" class="auth-btn">
            {{ authLoading ? '验证中...' : '验证并进入' }}
          </el-button>
        </div>
        
        <p class="auth-hint">默认密码: <code>admin123</code></p>
      </div>
    </el-dialog>

    <div v-if="isAuthenticated" class="config-content">
      <div class="page-header-wrapper">
        <div class="page-header">
          <div class="header-icon">
            <el-icon :size="32"><Cpu /></el-icon>
          </div>
          <div class="header-content">
            <h1>AI配置中心</h1>
            <p class="header-desc">配置AI模型参数，启用智能测试用例生成功能</p>
          </div>
          <div class="header-status">
            <el-tag :type="config.enabled ? 'success' : 'warning'" size="large">
              <el-icon><component :is="config.enabled ? Check : Warning" /></el-icon>
              {{ config.enabled ? 'AI已启用' : 'AI未配置' }}
            </el-tag>
          </div>
        </div>
      </div>

      <div class="config-grid">
        <div class="config-main">
          <el-card class="config-card">
            <template #header>
              <div class="card-header">
                <el-icon :size="20"><Setting /></el-icon>
                <span class="card-title">AI服务配置</span>
              </div>
            </template>

            <el-form ref="configForm" :model="config" label-width="130px" class="config-form">
              <div class="form-section">
                <h3 class="section-title">
                  <el-icon><Share /></el-icon>
                  服务提供商
                </h3>
                
                <el-form-item label="选择提供商">
                  <el-select 
                    v-model="config.provider" 
                    @change="onProviderChange"
                    class="provider-select"
                  >
                    <el-option label="OpenAI" value="openai">
                      <span class="option-icon">
                        <svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor">
                          <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z"/>
                        </svg>
                      </span>
                      OpenAI
                    </el-option>
                    <el-option label="DeepSeek" value="deepseek">
                      <span class="option-icon">🌊</span>
                      DeepSeek
                    </el-option>
                    <el-option label="Moonshot" value="moonshot">
                      <span class="option-icon">🌙</span>
                      Moonshot
                    </el-option>
                    <el-option label="Anthropic" value="anthropic">
                      <span class="option-icon">🦜</span>
                      Anthropic
                    </el-option>
                    <el-option label="自定义" value="custom">
                      <span class="option-icon">⚙️</span>
                      自定义
                    </el-option>
                  </el-select>
                </el-form-item>

                <el-form-item label="API Base URL">
                  <el-input 
                    v-model="config.api_base" 
                    placeholder="https://api.example.com/v1"
                    :disabled="config.provider !== 'custom'"
                    class="api-base-input"
                  >
                    <template #prefix>
                      <el-icon><Link /></el-icon>
                    </template>
                  </el-input>
                </el-form-item>
              </div>

              <el-divider class="form-divider" />

              <div class="form-section">
                <h3 class="section-title">
                  <el-icon><Key /></el-icon>
                  认证配置
                </h3>

                <el-form-item label="API Key" required>
                  <el-input 
                    v-model="config.api_key" 
                    type="password" 
                    placeholder="sk-xxxxxxxxxxxxxxxx"
                    show-password
                    class="api-key-input"
                    @input="onApiKeyChange"
                  >
                    <template #prefix>
                      <el-icon><Key /></el-icon>
                    </template>
                    <template #append>
                      <el-tag :type="config.api_key ? 'success' : 'info'" size="small">
                        {{ config.api_key ? '已填写' : '未填写' }}
                      </el-tag>
                    </template>
                  </el-input>
                </el-form-item>
              </div>

              <el-divider class="form-divider" />

              <div class="form-section">
                <h3 class="section-title">
                  <el-icon><Cpu /></el-icon>
                  模型配置
                </h3>

                <el-form-item label="选择模型">
                  <el-select v-model="config.model" class="model-select">
                    <el-option 
                      v-for="model in currentModels" 
                      :key="model" 
                      :label="model" 
                      :value="model" 
                    />
                  </el-select>
                </el-form-item>

                <el-form-item label="生成策略">
                  <el-select v-model="config.default_strategy" class="strategy-select">
                    <el-option label="🚀 混合模式（推荐）" value="hybrid" />
                    <el-option label="🤖 AI优先" value="ai_first" />
                    <el-option label="📋 规则优先" value="rule_first" />
                    <el-option label="💯 纯AI" value="ai_only" />
                    <el-option label="📝 纯规则" value="rule_only" />
                  </el-select>
                </el-form-item>
              </div>

              <el-divider class="form-divider" />

              <div class="form-section">
                <h3 class="section-title">
                  <el-icon><CircleCheck /></el-icon>
                  高级参数
                </h3>

                <el-form-item label="温度参数">
                  <el-slider 
                    v-model="config.temperature" 
                    :min="0" 
                    :max="1" 
                    :step="0.1"
                    show-input
                    class="temp-slider"
                  />
                  <div class="slider-info">
                    <span>低（精确）</span>
                    <span>高（创意）</span>
                  </div>
                </el-form-item>

                <div class="form-row">
                  <el-form-item label="最大Token数" class="row-item">
                    <el-input-number 
                      v-model="config.max_tokens" 
                      :min="1000" 
                      :max="65536" 
                      :step="1000"
                      class="token-input"
                    />
                  </el-form-item>
                  <el-form-item label="超时时间(秒)" class="row-item">
                    <el-input-number 
                      v-model="config.timeout" 
                      :min="30" 
                      :max="600" 
                      :step="30"
                      class="timeout-input"
                    />
                  </el-form-item>
                </div>
              </div>
            </el-form>

            <div class="config-actions">
              <el-button type="primary" @click="saveConfig" :disabled="!config.api_key" class="btn-save">
                <el-icon><Download /></el-icon>
                保存配置
              </el-button>
              <el-button @click="testConnection" :loading="testing" :disabled="!config.api_key" class="btn-test">
                <el-icon><Connection /></el-icon>
                {{ testing ? '测试中...' : '测试连接' }}
              </el-button>
              <el-button @click="resetConfig" class="btn-reset">
                <el-icon><RefreshLeft /></el-icon>
                重置
              </el-button>
            </div>
          </el-card>

          <el-card v-if="testResult" class="result-card" :class="testResult.success ? 'result-success' : 'result-error'">
            <template #header>
              <div class="result-header">
                <el-icon :size="20"><component :is="testResult.success ? CircleCheck : CircleClose" /></el-icon>
                <span>连接测试结果</span>
              </div>
            </template>
            <div class="result-content">
              <div class="result-icon">
                <el-icon :size="48"><component :is="testResult.success ? CircleCheck : CircleClose" /></el-icon>
              </div>
              <div class="result-details">
                <h4 class="result-title">{{ testResult.success ? '🎉 连接成功' : '❌ 连接失败' }}</h4>
                <p class="result-message">{{ testResult.message }}</p>
                <p class="result-code" v-if="testResult.status_code">
                  HTTP状态码: <span>{{ testResult.status_code }}</span>
                </p>
              </div>
            </div>
          </el-card>
        </div>

        <div class="config-sidebar">
          <el-card class="info-card">
            <template #header>
              <el-icon><InfoFilled /></el-icon>
              <span>配置指南</span>
            </template>
            <div class="guide-content">
              <div class="guide-step">
                <div class="step-number">1</div>
                <div class="step-content">
                  <h5>选择提供商</h5>
                  <p>根据您的API Key选择对应的服务提供商</p>
                </div>
              </div>
              <div class="guide-step">
                <div class="step-number">2</div>
                <div class="step-content">
                  <h5>输入API Key</h5>
                  <p>在API Key输入框中填写您的密钥</p>
                </div>
              </div>
              <div class="guide-step">
                <div class="step-number">3</div>
                <div class="step-content">
                  <h5>选择模型</h5>
                  <p>从下拉列表中选择合适的模型</p>
                </div>
              </div>
              <div class="guide-step">
                <div class="step-number">4</div>
                <div class="step-content">
                  <h5>测试连接</h5>
                  <p>点击测试连接验证配置是否正确</p>
                </div>
              </div>
              <div class="guide-step">
                <div class="step-number">5</div>
                <div class="step-content">
                  <h5>保存配置</h5>
                  <p>点击保存配置应用更改</p>
                </div>
              </div>
            </div>
          </el-card>

          <el-card class="providers-card">
            <template #header>
              <el-icon><OfficeBuilding /></el-icon>
              <span>支持的服务商</span>
            </template>
            <div class="providers-list">
              <div class="provider-item" v-for="(provider, key) in providers" :key="key">
                <div class="provider-name">{{ provider.name }}</div>
                <div class="provider-models">{{ provider.models.length }}个模型</div>
              </div>
            </div>
          </el-card>

          <el-card class="tips-card">
            <template #header>
              <el-icon><Lightning /></el-icon>
              <span>温馨提示</span>
            </template>
            <ul class="tips-list">
              <li>💡 API Key仅保存在服务器端，不会上传到第三方</li>
              <li>🔒 建议定期更换API Key以保证安全</li>
              <li>⚡ 国内用户推荐使用DeepSeek或Moonshot</li>
              <li>🌡️ 温度参数推荐值：0.5-0.7</li>
            </ul>
          </el-card>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { 
  Cpu, Check, Warning, Setting, Share, Key, Download, CircleCheck, 
  CircleClose, Connection, RefreshLeft, Link, InfoFilled, OfficeBuilding, Lightning, Lock
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const authDialogVisible = ref(true)
const isAuthenticated = ref(false)
const authLoading = ref(false)
const authError = ref('')
const authPassword = ref('')

const config = reactive({
  api_key: '',
  api_base: 'https://api.openai.com/v1',
  model: 'gpt-4o-mini',
  timeout: 300,
  max_tokens: 8000,
  temperature: 0.7,
  provider: 'openai',
  default_strategy: 'hybrid',
  enabled: false
})

const providers = ref({})
const testResult = ref(null)
const testing = ref(false)
const configForm = ref(null)
const currentModels = ref([])

const handleAuth = async () => {
  if (!authPassword.value.trim()) {
    authError.value = '请输入密码'
    return
  }
  
  authLoading.value = true
  authError.value = ''
  
  try {
    const res = await fetch('/api/v1/config/auth', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ password: authPassword.value })
    })
    
    const data = await res.json()
    
    if (data.success) {
      isAuthenticated.value = true
      authDialogVisible.value = false
      localStorage.setItem('ai_config_auth', 'true')
      ElMessage.success('身份验证成功')
      
      fetchConfig()
      fetchProviders()
    } else {
      authError.value = '密码错误，请重试'
      authPassword.value = ''
    }
  } catch (e) {
    authError.value = '网络错误，请稍后重试'
  } finally {
    authLoading.value = false
  }
}

const onProviderChange = () => {
  if (providers.value[config.provider]) {
    config.api_base = providers.value[config.provider].base_url
    currentModels.value = providers.value[config.provider].models || []
    if (currentModels.value.length > 0 && !currentModels.value.includes(config.model)) {
      config.model = currentModels.value[0]
    }
  }
}

const onApiKeyChange = () => {
  config.enabled = !!config.api_key
}

const fetchConfig = async () => {
  try {
    const res = await fetch('/api/v1/config')
    const data = await res.json()
    
    const configData = data.config || data
    
    const validKeys = ['api_key', 'api_base', 'model', 'timeout', 'max_tokens', 'temperature', 'provider', 'default_strategy', 'enabled']
    validKeys.forEach(key => {
      if (configData.hasOwnProperty(key)) {
        config[key] = configData[key]
      }
    })
  } catch (e) {
    console.error('获取配置失败', e)
  }
}

const fetchProviders = async () => {
  try {
    const res = await fetch('/api/v1/config/providers')
    providers.value = await res.json()
    currentModels.value = providers.value[config.provider]?.models || []
  } catch (e) {
    console.error('获取提供商列表失败', e)
  }
}

const saveConfig = async () => {
  if (!config.api_key.trim()) {
    ElMessage.warning('请输入API Key')
    return
  }
  
  const configData = {
    api_key: config.api_key,
    api_base: config.api_base,
    model: config.model,
    timeout: config.timeout,
    max_tokens: config.max_tokens,
    temperature: config.temperature,
    provider: config.provider,
    default_strategy: config.default_strategy
  }
  
  try {
    const res = await fetch('/api/v1/config', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ config: configData })
    })
    
    const data = await res.json()
    if (res.ok) {
      ElMessage.success(data.message)
      await fetchConfig()
    } else {
      ElMessage.error(data.detail || '保存失败')
    }
  } catch (e) {
    ElMessage.error('保存失败，请检查网络连接')
  }
}

const testConnection = async () => {
  if (!config.api_key.trim()) {
    ElMessage.warning('请先输入API Key')
    return
  }
  
  const configData = {
    api_key: config.api_key,
    api_base: config.api_base,
    model: config.model
  }
  
  testing.value = true
  testResult.value = null
  
  try {
    const res = await fetch('/api/v1/config/test', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ config: configData })
    })
    
    testResult.value = await res.json()
    
    if (testResult.value.success) {
      ElMessage.success('🎉 连接测试成功！AI功能已就绪')
    } else {
      ElMessage.error('连接测试失败: ' + testResult.value.message)
    }
  } catch (e) {
    testResult.value = { success: false, message: '网络错误: ' + e.message }
    ElMessage.error('网络错误，请检查服务器连接')
  } finally {
    testing.value = false
  }
}

const resetConfig = () => {
  config.api_key = ''
  config.api_base = 'https://api.openai.com/v1'
  config.model = 'gpt-4o-mini'
  config.timeout = 300
  config.max_tokens = 8000
  config.temperature = 0.7
  config.provider = 'openai'
  config.default_strategy = 'hybrid'
  config.enabled = false
  testResult.value = null
  ElMessage.info('配置已重置')
}

onMounted(() => {
  const auth = localStorage.getItem('ai_config_auth')
  if (auth === 'true') {
    isAuthenticated.value = true
    authDialogVisible.value = false
    fetchConfig()
    fetchProviders()
  }
})
</script>

<style scoped>
.ai-config-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e8ec 100%);
  padding: 24px;
}

.auth-dialog {
  .el-dialog__header {
    text-align: center;
    padding: 24px 24px 0;
    border-bottom: none;
  }
  
  .el-dialog__title {
    font-size: 18px;
    font-weight: 600;
    color: #333;
  }
  
  .el-dialog__body {
    padding: 24px;
  }
}

.auth-content {
  text-align: center;
}

.auth-icon {
  width: 80px;
  height: 80px;
  margin: 0 auto 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
}

.auth-title {
  font-size: 20px;
  font-weight: 600;
  color: #333;
  margin: 0 0 8px 0;
}

.auth-desc {
  font-size: 14px;
  color: #999;
  margin: 0 0 24px 0;
}

.auth-form {
  margin-bottom: 16px;
}

.auth-input {
  height: 48px;
  font-size: 16px;
}

.auth-error {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  color: #f56c6c;
  font-size: 13px;
  margin-bottom: 16px;
  padding: 10px;
  background: #fef0f0;
  border-radius: 8px;
}

.auth-actions {
  margin-bottom: 16px;
}

.auth-btn {
  width: 100%;
  height: 44px;
  font-size: 16px;
  font-weight: 600;
}

.auth-hint {
  font-size: 12px;
  color: #999;
  margin: 0;
}

.auth-hint code {
  background: #f5f5f5;
  padding: 2px 6px;
  border-radius: 4px;
  font-family: monospace;
}

.config-content {
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.page-header-wrapper {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 16px;
  padding: 24px 32px;
  margin-bottom: 24px;
  box-shadow: 0 4px 20px rgba(102, 126, 234, 0.3);
}

.page-header {
  display: flex;
  align-items: center;
  gap: 20px;
}

.header-icon {
  background: rgba(255, 255, 255, 0.2);
  padding: 12px;
  border-radius: 12px;
  color: #fff;
}

.header-content h1 {
  color: #fff;
  font-size: 28px;
  font-weight: 700;
  margin: 0 0 8px 0;
}

.header-desc {
  color: rgba(255, 255, 255, 0.85);
  font-size: 14px;
  margin: 0;
}

.header-status {
  margin-left: auto;
}

.config-grid {
  display: grid;
  grid-template-columns: 1fr 360px;
  gap: 24px;
}

.config-card {
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  font-size: 16px;
}

.config-form {
  padding: 8px 0;
}

.form-section {
  margin-bottom: 20px;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 600;
  color: #333;
  margin-bottom: 16px;
  padding-bottom: 8px;
  border-bottom: 2px solid #e8e8e8;
}

.provider-select {
  width: 100%;
}

.option-icon {
  margin-right: 8px;
}

.api-base-input {
  width: 100%;
}

.api-key-input {
  width: 100%;
}

.model-select {
  width: 100%;
}

.strategy-select {
  width: 100%;
}

.temp-slider {
  width: 100%;
}

.slider-info {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: #999;
  margin-top: 4px;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.row-item {
  margin-bottom: 0;
}

.token-input, .timeout-input {
  width: 100%;
}

.form-divider {
  margin: 16px 0;
}

.config-actions {
  display: flex;
  gap: 12px;
  margin-top: 24px;
  padding-top: 20px;
  border-top: 1px solid #e8e8e8;
}

.btn-save {
  flex: 1;
  padding: 12px;
  font-size: 15px;
  font-weight: 600;
}

.btn-test, .btn-reset {
  padding: 12px 24px;
  font-size: 14px;
}

.result-card {
  margin-top: 20px;
  border-radius: 12px;
  transition: all 0.3s ease;
}

.result-success {
  border-color: #67c23a;
  background: linear-gradient(135deg, #f0f9eb 0%, #e8f5e9 100%);
}

.result-error {
  border-color: #f56c6c;
  background: linear-gradient(135deg, #fef0f0 0%, #ffebee 100%);
}

.result-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
}

.result-content {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 16px 0;
}

.result-icon {
  flex-shrink: 0;
}

.result-success .result-icon {
  color: #67c23a;
}

.result-error .result-icon {
  color: #f56c6c;
}

.result-title {
  font-size: 18px;
  font-weight: 600;
  margin: 0 0 8px 0;
}

.result-success .result-title {
  color: #67c23a;
}

.result-error .result-title {
  color: #f56c6c;
}

.result-message {
  font-size: 14px;
  color: #666;
  margin: 0 0 4px 0;
}

.result-code {
  font-size: 13px;
  color: #999;
  margin: 0;
}

.result-code span {
  font-family: monospace;
  background: rgba(0, 0, 0, 0.05);
  padding: 2px 8px;
  border-radius: 4px;
}

.info-card, .providers-card, .tips-card {
  border-radius: 12px;
  margin-bottom: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.guide-content {
  padding: 8px 0;
}

.guide-step {
  display: flex;
  gap: 12px;
  padding: 12px 0;
  border-bottom: 1px solid #f0f0f0;
}

.guide-step:last-child {
  border-bottom: none;
}

.step-number {
  width: 28px;
  height: 28px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 600;
  flex-shrink: 0;
}

.step-content h5 {
  font-size: 14px;
  font-weight: 600;
  margin: 0 0 4px 0;
  color: #333;
}

.step-content p {
  font-size: 13px;
  color: #999;
  margin: 0;
}

.providers-list {
  padding: 8px 0;
}

.provider-item {
  padding: 10px 0;
  border-bottom: 1px solid #f5f5f5;
}

.provider-item:last-child {
  border-bottom: none;
}

.provider-name {
  font-size: 14px;
  font-weight: 600;
  color: #333;
}

.provider-models {
  font-size: 12px;
  color: #999;
  margin-top: 2px;
}

.tips-list {
  padding: 0;
  margin: 0;
  list-style: none;
}

.tips-list li {
  font-size: 13px;
  color: #666;
  padding: 8px 0;
  border-bottom: 1px solid #f5f5f5;
}

.tips-list li:last-child {
  border-bottom: none;
}

@media (max-width: 1200px) {
  .config-grid {
    grid-template-columns: 1fr;
  }
  
  .config-sidebar {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 16px;
  }
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .header-status {
    margin-left: 0;
    margin-top: 12px;
  }
  
  .config-sidebar {
    grid-template-columns: 1fr;
  }
  
  .form-row {
    grid-template-columns: 1fr;
  }
}
</style>