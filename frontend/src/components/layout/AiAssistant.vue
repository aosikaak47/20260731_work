<template>
  <div class="ai-assistant">
    <div class="floating-btn" v-if="!dialogVisible" @click="openDialog">
      <el-icon :size="24"><component :is="icons.MagicStick" /></el-icon>
      <span class="btn-tooltip">AI测试助手</span>
      <span class="btn-pulse"></span>
    </div>

    <transition name="dialog-fade">
      <div v-if="dialogVisible" class="assistant-dialog">
        <div class="dialog-header">
          <div class="header-info">
            <div class="avatar">
              <el-icon :size="20"><component :is="icons.MagicStick" /></el-icon>
            </div>
            <div class="header-text">
              <h3>AI测试助手</h3>
              <span class="status-dot"></span>
              <span class="status-text">在线</span>
            </div>
          </div>
          <el-icon :size="20" class="close-btn" @click="closeDialog">
            <component :is="icons.Close" />
          </el-icon>
        </div>

        <div class="dialog-body" ref="bodyRef">
          <div v-if="messages.length === 0" class="welcome-section">
            <div class="welcome-icon">
              <el-icon :size="40"><component :is="icons.MagicStick" /></el-icon>
            </div>
            <h4>你好，我是 AI 测试助手</h4>
            <p>我可以帮你：</p>
            <div class="feature-list">
              <div class="feature-item" v-for="feature in features" :key="feature.title" @click="useFeature(feature)">
                <el-icon :size="18"><component :is="feature.icon" /></el-icon>
                <div class="feature-info">
                  <span class="feature-title">{{ feature.title }}</span>
                  <span class="feature-desc">{{ feature.desc }}</span>
                </div>
              </div>
            </div>
          </div>

          <div v-else class="messages-container">
            <div
              v-for="(msg, idx) in messages"
              :key="idx"
              class="message-item"
              :class="{ 'user-msg': msg.role === 'user', 'ai-msg': msg.role === 'assistant' }"
            >
              <div v-if="msg.role === 'assistant'" class="msg-avatar">
                <el-icon :size="16"><component :is="icons.MagicStick" /></el-icon>
              </div>
              <div class="msg-content">
                <div class="msg-text">{{ msg.content }}</div>
                <div v-if="msg.thinking" class="msg-thinking">
                  <el-icon class="is-loading"><component :is="icons.Loading" /></el-icon>
                  <span>思考中...</span>
                </div>
              </div>
              <div v-if="msg.role === 'user'" class="msg-avatar user-avatar">
                <el-icon :size="16"><component :is="icons.User" /></el-icon>
              </div>
            </div>
          </div>
        </div>

        <div class="dialog-footer">
          <div class="quick-actions" v-if="messages.length === 0">
            <el-tag
              v-for="suggestion in suggestions"
              :key="suggestion"
              class="suggestion-tag"
              @click="sendSuggestion(suggestion)"
            >
              {{ suggestion }}
            </el-tag>
          </div>
          <div class="input-area">
            <el-input
              v-model="inputText"
              type="textarea"
              :rows="2"
              placeholder="输入你的问题，如：帮我分析这个测试用例的覆盖度..."
              :autosize="{ minRows: 2, maxRows: 4 }"
              @keydown.enter.exact.prevent="handleSend"
              resize="none"
            />
            <el-button
              type="primary"
              circle
              :icon="icons.Promotion"
              @click="handleSend"
              :disabled="!inputText.trim() || isSending"
            />
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, nextTick } from 'vue'
import * as icons from '@element-plus/icons-vue'

const dialogVisible = ref(false)
const inputText = ref('')
const isSending = ref(false)
const messages = ref([])
const bodyRef = ref(null)

const features = [
  { title: '分析测试需求', desc: '理解需求文档，拆解测试点', icon: icons.Document },
  { title: '设计测试用例', desc: '根据需求自动生成测试用例', icon: icons.EditPen },
  { title: '分析测试结果', desc: '解析执行报告，定位缺陷', icon: icons.DataAnalysis },
  { title: '测试策略建议', desc: '提供测试方案与覆盖率建议', icon: icons.Setting }
]

const suggestions = [
  '帮我分析登录功能的测试点',
  '为支付流程设计测试用例',
  '分析这个接口的边界条件',
  '如何提高测试覆盖率？'
]

const openDialog = () => {
  dialogVisible.value = true
}

const closeDialog = () => {
  dialogVisible.value = false
}

const scrollToBottom = () => {
  nextTick(() => {
    if (bodyRef.value) {
      bodyRef.value.scrollTop = bodyRef.value.scrollHeight
    }
  })
}

const useFeature = (feature) => {
  const prompts = {
    '分析测试需求': '请帮我分析以下测试需求，拆解出关键测试点：\n\n请描述你的需求内容...',
    '设计测试用例': '请根据以下需求描述，设计完整的测试用例：\n\n请描述你的需求内容...',
    '分析测试结果': '请帮我分析以下测试执行结果，定位可能的缺陷：\n\n请粘贴测试报告或执行日志...',
    '测试策略建议': '请为以下场景提供测试策略建议：\n\n请描述你的测试场景...'
  }
  inputText.value = prompts[feature.title] || `请帮我${feature.title}...`
}

const sendSuggestion = (text) => {
  inputText.value = text
  handleSend()
}

const mockAIResponse = (userText) => {
  const responses = [
    `根据你提出的「${userText}」，我建议从以下几个方面进行分析：\n\n1. **功能完整性**：检查核心业务流程是否覆盖\n2. **边界条件**：关注异常输入、极限值等场景\n3. **交互体验**：验证用户操作流程的合理性\n4. **数据安全**：确认敏感数据的处理是否合规\n\n你可以告诉我具体的业务场景，我会提供更详细的分析和建议。`,
    `针对「${userText}」这个需求，我拆解出以下测试点：\n\n**核心功能测试点：**\n- 正常流程验证\n- 异常流程处理\n- 边界条件测试\n\n**非功能测试点：**\n- 性能响应时间\n- 并发处理能力\n- 安全性验证\n\n需要我为这些测试点生成详细的测试用例吗？`,
    `我收到你的问题：「${userText}」\n\n基于平台的测试数据分析，我发现以下关键指标：\n\n• 通过率趋势：近7天通过率稳步上升\n• 失败集中度：主要集中在接口异常处理模块\n• 执行效率：平均执行耗时下降15%\n\n建议重点关注失败用例的根本原因分析。`
  ]
  return responses[Math.floor(Math.random() * responses.length)]
}

const handleSend = async () => {
  const text = inputText.value.trim()
  if (!text || isSending.value) return

  messages.value.push({ role: 'user', content: text })
  inputText.value = ''
  isSending.value = true
  scrollToBottom()

  messages.value.push({ role: 'assistant', content: '', thinking: true })

  setTimeout(() => {
    const lastMsg = messages.value[messages.value.length - 1]
    lastMsg.content = mockAIResponse(text)
    lastMsg.thinking = false
    isSending.value = false
    scrollToBottom()
  }, 1500)
}
</script>

<style scoped>
.ai-assistant {
  position: fixed;
  right: 24px;
  bottom: 120px;
  z-index: 999;
}

.floating-btn {
  width: 52px;
  height: 52px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--theme-primary) 0%, var(--theme-primary-dark) 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  cursor: pointer;
  box-shadow: 0 4px 16px rgba(0, 136, 102, 0.35);
  transition: all 0.3s ease;
  position: relative;
}

.floating-btn:hover {
  transform: scale(1.08);
  box-shadow: 0 6px 24px rgba(0, 136, 102, 0.45);
}

.btn-tooltip {
  position: absolute;
  right: 60px;
  white-space: nowrap;
  background: var(--color-text-primary);
  color: #fff;
  padding: 6px 12px;
  border-radius: var(--radius-md);
  font-size: var(--font-size-xs);
  opacity: 0;
  pointer-events: none;
  transition: all 0.2s ease;
}

.floating-btn:hover .btn-tooltip {
  opacity: 1;
  right: 62px;
}

.btn-pulse {
  position: absolute;
  width: 100%;
  height: 100%;
  border-radius: 50%;
  background: var(--theme-primary);
  opacity: 0.4;
  animation: pulse 2s ease-out infinite;
}

@keyframes pulse {
  0% {
    transform: scale(1);
    opacity: 0.4;
  }
  100% {
    transform: scale(1.6);
    opacity: 0;
  }
}

.assistant-dialog {
  width: 380px;
  height: 560px;
  background: var(--color-bg-card);
  border-radius: var(--radius-xl);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.18);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  border: 1px solid var(--color-border);
}

.dialog-header {
  padding: 16px;
  background: linear-gradient(135deg, var(--theme-primary) 0%, var(--theme-primary-dark) 100%);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.header-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.avatar {
  width: 36px;
  height: 36px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.header-text {
  display: flex;
  align-items: center;
  gap: 6px;
}

.header-text h3 {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-semibold);
  margin: 0;
}

.status-dot {
  width: 6px;
  height: 6px;
  background: #10b981;
  border-radius: 50%;
  display: inline-block;
  animation: blink 1.5s ease-in-out infinite;
}

@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.status-text {
  font-size: var(--font-size-xs);
  opacity: 0.85;
}

.close-btn {
  cursor: pointer;
  opacity: 0.8;
  transition: opacity 0.2s;
}

.close-btn:hover {
  opacity: 1;
}

.dialog-body {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  background: var(--color-bg-page);
}

.welcome-section {
  text-align: center;
}

.welcome-icon {
  width: 56px;
  height: 56px;
  background: linear-gradient(135deg, var(--theme-primary-light) 0%, var(--color-bg-hover) 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 12px;
  color: var(--theme-primary);
}

.welcome-section h4 {
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  margin: 0 0 8px;
}

.welcome-section p {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  margin: 0 0 16px;
}

.feature-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  cursor: pointer;
  transition: all 0.2s;
  text-align: left;
}

.feature-item:hover {
  border-color: var(--theme-primary);
  background: var(--theme-primary-light);
  transform: translateY(-1px);
}

.feature-item .el-icon {
  color: var(--theme-primary);
  flex-shrink: 0;
}

.feature-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.feature-title {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-primary);
}

.feature-desc {
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
}

.messages-container {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.message-item {
  display: flex;
  gap: 8px;
  align-items: flex-start;
}

.user-msg {
  flex-direction: row-reverse;
}

.msg-avatar {
  width: 28px;
  height: 28px;
  background: var(--theme-primary-light);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--theme-primary);
  flex-shrink: 0;
}

.user-avatar {
  background: var(--color-border);
  color: var(--color-text-secondary);
}

.msg-content {
  max-width: 80%;
}

.user-msg .msg-content {
  align-items: flex-end;
}

.msg-text {
  padding: 10px 12px;
  border-radius: var(--radius-lg);
  font-size: var(--font-size-sm);
  line-height: 1.6;
  white-space: pre-wrap;
  word-break: break-word;
}

.ai-msg .msg-text {
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  color: var(--color-text-primary);
  border-top-left-radius: var(--radius-sm);
}

.user-msg .msg-text {
  background: var(--theme-primary);
  color: #fff;
  border-top-right-radius: var(--radius-sm);
}

.msg-thinking {
  display: flex;
  align-items: center;
  gap: 6px;
  color: var(--color-text-tertiary);
  font-size: var(--font-size-xs);
  padding: 8px 0;
}

.dialog-footer {
  padding: 12px 16px;
  background: var(--color-bg-card);
  border-top: 1px solid var(--color-border);
}

.quick-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-bottom: 10px;
}

.suggestion-tag {
  cursor: pointer;
  font-size: var(--font-size-xs);
  border-color: var(--theme-primary);
  color: var(--theme-primary);
  background: var(--theme-primary-light);
  margin: 0;
}

.suggestion-tag:hover {
  background: var(--theme-primary);
  color: #fff;
}

.input-area {
  display: flex;
  gap: 8px;
  align-items: flex-end;
}

.input-area :deep(.el-textarea__inner) {
  border-radius: var(--radius-md);
  padding: 8px 12px;
  font-size: var(--font-size-sm);
  border-color: var(--color-border);
}

.input-area :deep(.el-textarea__inner:focus) {
  border-color: var(--theme-primary);
}

.input-area .el-button--primary {
  width: 36px;
  height: 36px;
  flex-shrink: 0;
}

.input-area .el-button--primary :deep(.el-icon) {
  font-size: 18px;
}

.dialog-fade-enter-active,
.dialog-fade-leave-active {
  transition: all 0.25s ease;
}

.dialog-fade-enter-from,
.dialog-fade-leave-to {
  opacity: 0;
  transform: translateY(10px) scale(0.95);
}
</style>
