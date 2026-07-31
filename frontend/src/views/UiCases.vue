<template>
  <div class="ui-cases">
    <div class="page-header">
      <h2>UI用例编排</h2>
      <p class="page-desc">拖拽式编排UI自动化测试场景</p>
    </div>

    <div class="main-toolbar">
      <div class="toolbar-left">
        <el-input
          v-model="searchKeyword"
          placeholder="搜索场景名称..."
          clearable
          style="width: 260px;"
        >
          <template #prefix>
            <el-icon><component :is="icons.Search" /></el-icon>
          </template>
        </el-input>
        <el-select
          v-model="filterProject"
          placeholder="选择项目"
          clearable
          filterable
          style="width: 200px;"
        >
          <el-option
            v-for="p in projectOptions"
            :key="p.id"
            :label="p.name"
            :value="p.name"
          />
        </el-select>
        <el-select
          v-model="filterModule"
          placeholder="选择模块"
          clearable
          filterable
          style="width: 180px;"
        >
          <el-option
            v-for="m in filterModuleOptions"
            :key="m.id"
            :label="m.name"
            :value="m.name"
          />
        </el-select>
      </div>
      <div class="toolbar-right">
        <el-button @click="loadCases">
          <el-icon><component :is="icons.Refresh" /></el-icon>
          刷新
        </el-button>
        <el-button type="danger" @click="openRecorder">
          <el-icon><component :is="icons.VideoCamera" /></el-icon>
          录制脚本
        </el-button>
      </div>
    </div>

    <el-table
      v-loading="loading"
      :data="filteredCases"
      stripe
      style="width: 100%;"
      @row-dblclick="handleEdit"
    >
      <el-table-column type="index" label="序号" width="60" />
      <el-table-column prop="name" label="场景名称" min-width="160">
        <template #default="{ row }">
          <span class="case-name">{{ row.name }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="project" label="所属项目" min-width="120">
        <template #default="{ row }">
          <el-tag size="small" type="info">{{ row.project || '-' }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="module" label="所属模块" min-width="120">
        <template #default="{ row }">
          <el-tag size="small" type="warning">{{ row.module || '-' }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="url" label="目标URL" min-width="200" show-overflow-tooltip>
        <template #default="{ row }">
          <span class="url-text">{{ row.url || '-' }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="description" label="描述" min-width="180" show-overflow-tooltip>
        <template #default="{ row }">
          {{ row.description || '-' }}
        </template>
      </el-table-column>
      <el-table-column label="步骤数" width="90" align="center">
        <template #default="{ row }">
          <el-badge :value="(row.steps || []).length" type="primary">
            <el-icon :size="16" color="#6366f1"><component :is="icons.List" /></el-icon>
          </el-badge>
        </template>
      </el-table-column>
      <el-table-column prop="updated_at" label="更新时间" width="170">
        <template #default="{ row }">
          <span class="time-text">{{ formatTime(row.updated_at) }}</span>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="280" fixed="right">
        <template #default="{ row }">
          <div class="table-actions">
            <el-button type="success" size="small" @click="handleRun(row)" class="action-btn">
              <el-icon><component :is="icons.VideoPlay" /></el-icon>
              执行
            </el-button>
            <el-button size="small" @click="handleEdit(row)" class="action-btn">
              <el-icon><component :is="icons.Edit" /></el-icon>
              编辑
            </el-button>
            <el-button type="danger" size="small" @click="handleDelete(row)" class="action-btn">
              <el-icon><component :is="icons.Delete" /></el-icon>
              删除
            </el-button>
          </div>
        </template>
      </el-table-column>
    </el-table>

    <div class="pagination-wrapper">
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.pageSize"
        :page-sizes="[10, 20, 50]"
        :total="paginationTotal"
        layout="total, sizes, prev, pager, next, jumper"
        background
      />
    </div>

    <el-dialog
      v-model="dialogVisible"
      :title="isEditing ? '编辑场景' : '新增场景'"
      width="900px"
      :close-on-click-modal="false"
      top="5vh"
      @open="handleDialogOpen"
    >
      <div class="dialog-content">
        <el-form
          ref="formRef"
          :model="form"
          :rules="formRules"
          label-width="100px"
          class="case-form"
        >
          <el-row :gutter="16">
            <el-col :span="12">
              <el-form-item label="场景名称" prop="name">
                <el-input v-model="form.name" placeholder="请输入场景名称" maxlength="50" show-word-limit />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="所属项目" prop="project">
                <el-select v-model="form.project" placeholder="请选择项目" filterable style="width: 100%" @change="onFormProjectChange">
                  <el-option
                    v-for="p in projectOptions"
                    :key="p.id"
                    :label="p.name"
                    :value="p.name"
                  />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>
          <el-row :gutter="16">
            <el-col :span="12">
              <el-form-item label="所属模块" prop="module">
                <el-select v-model="form.module" placeholder="请选择模块" filterable clearable style="width: 100%">
                  <el-option
                    v-for="m in formModuleOptions"
                    :key="m.id"
                    :label="m.name"
                    :value="m.name"
                  />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>
          <el-row :gutter="16">
            <el-col :span="24">
              <el-form-item label="目标URL" prop="url">
                <el-input v-model="form.url" placeholder="https://example.com" />
              </el-form-item>
            </el-col>
          </el-row>
          <el-row :gutter="16">
            <el-col :span="24">
              <el-form-item label="场景描述">
                <el-input
                  v-model="form.description"
                  type="textarea"
                  :rows="2"
                  placeholder="请输入场景描述..."
                  maxlength="200"
                  show-word-limit
                />
              </el-form-item>
            </el-col>
          </el-row>
        </el-form>

        <div class="orchestration-section">
          <div class="section-header">
            <span class="section-title">步骤编排</span>
            <div class="section-actions">
              <el-button size="small" @click="handleAddStep('navigate')">
                <el-icon><component :is="icons.Position" /></el-icon>
                导航
              </el-button>
              <el-button size="small" @click="handleAddStep('click')">
                <el-icon><component :is="icons.Mouse" /></el-icon>
                点击
              </el-button>
              <el-button size="small" @click="handleAddStep('input')">
                <el-icon><component :is="icons.Operation" /></el-icon>
                输入
              </el-button>
              <el-button size="small" @click="handleAddStep('select')">
                <el-icon><component :is="icons.CaretBottom" /></el-icon>
                选择
              </el-button>
              <el-button size="small" @click="handleAddStep('wait')">
                <el-icon><component :is="icons.Clock" /></el-icon>
                等待
              </el-button>
              <el-button size="small" @click="handleAddStep('assert')">
                <el-icon><component :is="icons.CircleCheck" /></el-icon>
                断言
              </el-button>
              <el-button size="small" @click="handleAddStep('screenshot')">
                <el-icon><component :is="icons.Camera" /></el-icon>
                截图
              </el-button>
              <el-button size="small" @click="handleAddStep('scroll')">
                <el-icon><component :is="icons.ArrowDown" /></el-icon>
                滚动
              </el-button>
              <el-button size="small" @click="handleAddStep('switch')">
                <el-icon><component :is="icons.Share" /></el-icon>
                条件
              </el-button>
            </div>
          </div>

          <div class="orchestration-body">
            <div class="component-library">
              <div class="library-title">操作组件库</div>
              <div class="component-grid">
                <div
                  v-for="component in componentTypes"
                  :key="component.type"
                  class="component-item"
                  draggable="true"
                  @dragstart="handleDragStart(component)"
                >
                  <el-icon :size="16"><component :is="component.icon" /></el-icon>
                  <span>{{ component.name }}</span>
                </div>
              </div>
            </div>

            <div class="flow-canvas" @drop="handleDrop" @dragover.prevent>
              <div v-if="form.steps.length === 0" class="empty-canvas">
                <el-icon :size="48" class="empty-icon"><component :is="icons.Box" /></el-icon>
                <span>拖拽左侧组件到此处，或点击上方按钮添加步骤</span>
              </div>

              <div v-else class="steps-list">
                <div
                  v-for="(step, index) in form.steps"
                  :key="step.id"
                  class="step-card"
                  :class="{ 'step-card-active': activeStepId === step.id }"
                  @click="activeStepId = step.id"
                >
                  <div class="step-header">
                    <span class="step-num">{{ index + 1 }}</span>
                    <el-icon :size="16"><component :is="getStepIcon(step.type)" /></el-icon>
                    <span class="step-name">{{ step.name }}</span>
                    <div class="step-actions">
                      <el-button
                        size="small"
                        text
                        :disabled="index === 0"
                        @click.stop="moveStep(index, -1)"
                      >
                        <el-icon><component :is="icons.ArrowUp" /></el-icon>
                      </el-button>
                      <el-button
                        size="small"
                        text
                        :disabled="index === form.steps.length - 1"
                        @click.stop="moveStep(index, 1)"
                      >
                        <el-icon><component :is="icons.ArrowDown" /></el-icon>
                      </el-button>
                      <el-button size="small" text @click.stop="handleDuplicateStep(step)">
                        <el-icon><component :is="icons.CopyDocument" /></el-icon>
                      </el-button>
                      <el-button size="small" text type="danger" @click.stop="handleRemoveStep(step.id)">
                        <el-icon><component :is="icons.Close" /></el-icon>
                      </el-button>
                    </div>
                  </div>
                  <div class="step-body">
                    <el-form label-width="80px" :model="step" size="small">
                      <el-row :gutter="12">
                        <el-col :span="12">
                          <el-form-item label="元素">
                            <el-input
                              v-model="step.element"
                              :placeholder="getElementPlaceholder(step.type)"
                            />
                          </el-form-item>
                        </el-col>
                        <el-col :span="12">
                          <el-form-item label="参数">
                            <el-input
                              v-model="step.params"
                              :placeholder="getParamsPlaceholder(step.type)"
                            />
                          </el-form-item>
                        </el-col>
                      </el-row>
                      <el-row :gutter="12">
                        <el-col :span="8">
                          <el-form-item label="延时">
                            <el-input-number v-model="step.delay" :min="0" :max="60" :step="0.5" style="width: 100%;" />
                          </el-form-item>
                        </el-col>
                        <el-col :span="8">
                          <el-form-item label="重试">
                            <el-input-number v-model="step.retry" :min="0" :max="5" style="width: 100%;" />
                          </el-form-item>
                        </el-col>
                        <el-col :span="8">
                          <el-form-item label="超时">
                            <el-input-number v-model="step.timeout" :min="1" :max="300" style="width: 100%;" />
                          </el-form-item>
                        </el-col>
                      </el-row>
                    </el-form>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" :loading="submitting" @click="handleSubmit">
            {{ isEditing ? '保存修改' : '创建场景' }}
          </el-button>
        </div>
      </template>
    </el-dialog>

    <el-dialog
      v-model="executeDialogVisible"
      title="执行场景"
      width="700px"
      :close-on-click-modal="false"
    >
      <div class="execute-content">
        <div v-if="executing" class="executing-state">
          <el-icon :size="32" class="is-loading" color="#6366f1"><component :is="icons.Loading" /></el-icon>
          <p>正在执行场景 "{{ currentCase?.name }}" ...</p>
          <p class="executing-tip">请稍候，执行过程中请勿关闭此窗口</p>
        </div>

        <div v-else-if="executeResult" class="execute-result">
          <div class="result-header">
            <el-alert
              :title="executeResult.success ? '执行成功' : '执行失败'"
              :type="executeResult.success ? 'success' : 'error'"
              :closable="false"
              show-icon
            />
            <div class="result-stats">
              <span>总步骤: {{ executeResult.total_steps || 0 }}</span>
              <span>通过: <span class="stat-success">{{ executeResult.passed || 0 }}</span></span>
              <span>失败: <span class="stat-fail">{{ executeResult.failed || 0 }}</span></span>
              <span>耗时: {{ executeResult.duration || 0 }}s</span>
            </div>
          </div>

          <div class="log-panel">
            <div class="log-title">执行日志</div>
            <div class="log-content">
              <div
                v-for="(log, idx) in executeResult.logs || []"
                :key="idx"
                class="log-item"
                :class="log.level"
              >
                <span class="log-step">[{{ log.step || idx + 1 }}]</span>
                <span class="log-message">{{ log.message }}</span>
                <span v-if="log.duration" class="log-duration">{{ log.duration }}s</span>
                <el-icon
                  v-if="log.level === 'success'"
                  :size="14"
                  class="log-icon"
                ><component :is="icons.CircleCheck" /></el-icon>
                <el-icon
                  v-else-if="log.level === 'error'"
                  :size="14"
                  class="log-icon"
                ><component :is="icons.CircleClose" /></el-icon>
                <el-icon
                  v-else
                  :size="14"
                  class="log-icon"
                ><component :is="icons.InfoFilled" /></el-icon>
              </div>
            </div>
          </div>

          <div v-if="executeResult.screenshot" class="screenshot-panel">
            <div class="log-title">截图预览</div>
            <img :src="executeResult.screenshot" alt="screenshot" class="screenshot-img" />
          </div>
        </div>
      </div>

      <template #footer>
        <el-button @click="executeDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>

    <!-- 录制脚本对话框 -->
    <el-dialog v-model="recorderVisible" title="自动录制脚本" width="1000px" top="5vh" :close-on-click-modal="false" class="recorder-dialog" @close="onRecorderClose">
      <div class="recorder-container">
        <!-- 顶部：URL输入和录制控制 -->
        <div class="recorder-input-section">
          <el-form :inline="true">
            <el-form-item label="所属项目">
              <el-select v-model="recordForm.project" placeholder="选择项目" filterable style="width: 180px" @change="onRecordProjectChange" :disabled="recording">
                <el-option v-for="p in projectOptions" :key="p.id" :label="p.name" :value="p.name" />
              </el-select>
            </el-form-item>
            <el-form-item label="所属模块">
              <el-select v-model="recordForm.module" placeholder="选择模块" filterable clearable style="width: 160px" :disabled="recording">
                <el-option v-for="m in recordModuleOptions" :key="m.id" :label="m.name" :value="m.name" />
              </el-select>
            </el-form-item>
            <el-form-item label="场景名称">
              <el-input v-model="recordForm.caseName" placeholder="请输入场景名称" style="width: 200px" :disabled="recording" />
            </el-form-item>
            <el-form-item label="目标URL">
              <el-input v-model="recordForm.url" placeholder="https://www.baidu.com" style="width: 300px;" @keyup.enter="startAutoRecording" :disabled="recording" />
            </el-form-item>
            <el-form-item v-if="!recording && recordedActions.length === 0">
              <el-button type="primary" @click="startAutoRecording" :disabled="!recordForm.url" :loading="recorderLoading">
                <el-icon><component :is="icons.VideoCamera" /></el-icon>
                开始自动录制
              </el-button>
            </el-form-item>
            <el-form-item v-if="recording">
              <el-button type="danger" @click="stopAutoRecording">
                <el-icon><component :is="icons.Stop" /></el-icon>
                停止录制并生成脚本
              </el-button>
            </el-form-item>
            <el-form-item v-if="!recording && recordedActions.length > 0 && !recorderResult">
              <el-button type="success" @click="generateScriptFromRecording">
                <el-icon><component :is="icons.Document" /></el-icon>
                生成脚本
              </el-button>
              <el-button @click="resetRecorder">
                重新录制
              </el-button>
            </el-form-item>
          </el-form>
        </div>

        <!-- 录制状态提示 -->
        <el-alert v-if="recording" type="warning" :closable="false" show-icon class="recording-alert">
          <template #title>
            <span>正在录制中... 已捕获 <strong style="color: #f56c6c; font-size: 16px;">{{ recordedActions.length }}</strong> 个操作</span>
          </template>
          <template #default>
            <span style="font-size: 13px;">请在弹出的浏览器窗口中进行操作（点击、输入、选择等），系统会自动记录您的操作。</span>
          </template>
        </el-alert>

        <el-alert v-if="recorderError" type="error" :closable="false" show-icon class="recording-alert">
          <template #title>{{ recorderError }}</template>
        </el-alert>

        <!-- 操作记录列表 -->
        <div class="recorder-actions-full">
          <div class="actions-header">
            <span class="actions-title">
              操作记录
              <el-badge :value="recordedActions.length" type="primary" style="margin-left: 8px;" />
            </span>
            <el-button
              size="small"
              type="danger"
              text
              @click="clearRecordedActions"
              :disabled="recordedActions.length === 0 || recording"
            >
              清空
            </el-button>
          </div>
          <div class="actions-body">
            <div v-if="recordedActions.length === 0" class="actions-empty">
              <el-icon :size="48" color="#c0c4cc"><component :is="icons.VideoCamera" /></el-icon>
              <p v-if="!recording" style="margin-top: 12px;">暂无录制操作</p>
              <p v-else style="margin-top: 12px;">等待操作中... 请在浏览器中进行操作</p>
              <p class="actions-hint" v-if="!recording">输入URL并点击"开始自动录制"</p>
              <p class="actions-hint" v-else>系统会自动捕获您的操作</p>
            </div>
            <div v-else class="actions-list">
              <div v-for="(action, index) in recordedActions" :key="index" class="action-item" :class="action.type">
                <div class="action-index">{{ index + 1 }}</div>
                <div class="action-content">
                  <div class="action-type">
                    <el-tag size="small" :type="getActionTagType(action.type)">{{ getActionTypeText(action.type) }}</el-tag>
                    <span v-if="action.text" class="action-text">{{ action.text }}</span>
                  </div>
                  <div class="action-detail">
                    <span v-if="action.selector" class="action-selector">{{ action.selector }}</span>
                    <span v-if="action.value" class="action-value">= "{{ action.value }}"</span>
                    <span v-if="action.url" class="action-value">{{ action.url }}</span>
                  </div>
                </div>
                <el-button
                  v-if="!recording"
                  size="small"
                  type="danger"
                  text
                  @click="removeAction(index)"
                >
                  <el-icon><component :is="icons.Close" /></el-icon>
                </el-button>
              </div>
            </div>
          </div>
        </div>

        <!-- 录制结果 -->
        <div v-if="recorderResult" class="recorder-result">
          <el-alert
            type="success"
            :closable="false"
            show-icon
            :title="'脚本生成成功！共录制 ' + recorderResult.actions_count + ' 个操作'"
          >
            <template #default>
              <div class="result-details">
                <p>脚本文件: <code>{{ recorderResult.script_file }}</code></p>
                <p>保存路径: <code>{{ recorderResult.script_path }}</code></p>
                <div class="result-actions">
                  <el-button size="small" @click="copyToClipboard(recorderResult.script)">复制脚本</el-button>
                  <el-button size="small" @click="copyToClipboard(recorderResult.execute_command)">复制执行命令</el-button>
                  <el-button
                    size="small"
                    type="primary"
                    @click="useGeneratedScript(recorderResult)"
                  >
                    使用此脚本
                  </el-button>
                  <el-button
                    size="small"
                    type="success"
                    @click="saveRecordingToCaseList"
                    :loading="savingToCaseList"
                  >
                    保存到用例列表
                  </el-button>
                </div>
              </div>
            </template>
          </el-alert>
          <div class="script-preview">
            <div class="preview-header-bar">
              <span>脚本预览</span>
              <el-button size="small" text @click="toggleScriptPreview">{{ showFullScript ? '收起' : '展开' }}</el-button>
            </div>
            <pre :class="{ 'script-preview-collapsed': !showFullScript }">{{ recorderResult.script }}</pre>
          </div>
        </div>
      </div>
    </el-dialog>

    <!-- 脚本生成对话框 -->
    <el-dialog v-model="scriptDialogVisible" title="Playwright 脚本生成与执行" width="900px" top="5vh">
      <div class="script-container">
        <div class="script-toolbar">
          <span>当前用例：{{ currentCase?.name || '未选择' }}</span>
          <el-button type="primary" @click="generateScript" :loading="generating">
            <el-icon><component :is="icons.MagicStick" /></el-icon>
            AI生成脚本
          </el-button>
          <el-button @click="copyScript" :disabled="!generatedScript">
            <el-icon><component :is="icons.CopyDocument" /></el-icon>
            复制
          </el-button>
          <el-button type="warning" @click="saveScript" :disabled="!generatedScript" :loading="savingScript">
            <el-icon><component :is="icons.FolderAdd" /></el-icon>
            保存脚本
          </el-button>
          <el-divider direction="vertical" />
          <el-switch v-model="headlessMode" active-text="无头模式" inactive-text="有头浏览器" />
          <el-tooltip content="有头模式会打开真实浏览器窗口，可以看到执行过程">
            <el-button type="success" @click="executeScript" :disabled="!generatedScript" :loading="executingScript">
              <el-icon><component :is="icons.VideoPlay" /></el-icon>
              执行脚本
            </el-button>
          </el-tooltip>
        </div>

        <div v-if="scriptError" class="script-error">
          <el-alert :title="scriptError" type="error" show-icon :closable="false" />
        </div>

        <div class="script-tabs">
          <el-tabs v-model="scriptTab">
            <el-tab-pane label="脚本代码" name="code">
              <div v-if="generatedScript" class="script-code-wrapper">
                <div class="script-header">
                  <span class="script-language">Python + Playwright</span>
                  <div class="script-header-actions">
                    <el-switch v-model="scriptEditMode" active-text="编辑模式" inactive-text="预览模式" />
                    <el-tooltip content="在编辑模式下可以直接修改脚本">
                      <span class="script-tip">支持编辑后保存</span>
                    </el-tooltip>
                  </div>
                </div>
                <textarea 
                  v-if="scriptEditMode"
                  v-model="generatedScript" 
                  class="script-code-editor"
                  spellcheck="false"
                  placeholder="在此编辑Python脚本..."
                ></textarea>
                <pre v-else class="script-code">{{ generatedScript }}</pre>
                <div class="script-footer">
                  <span class="script-footer-info">共 {{ generatedScript.split('\\n').length }} 行 | 修改后点击"保存脚本"按钮保存</span>
                </div>
              </div>
              <el-empty v-else description="点击AI生成脚本按钮生成Playwright代码" />
            </el-tab-pane>
            <el-tab-pane label="执行结果" name="result">
              <div v-if="scriptExecutionResult" class="execution-result">
                <el-alert 
                  :title="getExecutionTitle()"
                  :type="getExecutionAlertType()"
                  show-icon 
                  :description="getExecutionDescription()"
                />
                <div class="result-stats">
                  <div class="stat-item">
                    <span class="stat-label">耗时</span>
                    <span class="stat-value">{{ scriptExecutionResult.duration?.toFixed?.(1) || scriptExecutionResult.duration }}秒</span>
                  </div>
                  <div class="stat-item">
                    <span class="stat-label">状态</span>
                    <span class="stat-value" :class="scriptExecutionResult.status">{{ getStatusText() }}</span>
                  </div>
                  <div class="stat-item">
                    <span class="stat-label">模式</span>
                    <span class="stat-value">{{ scriptExecutionResult.headless ? '无头' : '有头' }}</span>
                  </div>
                  <div class="stat-item">
                    <span class="stat-label">截图</span>
                    <span class="stat-value">{{ scriptExecutionResult.screenshots?.length || 0 }}张</span>
                  </div>
                </div>
                
                <div v-if="scriptExecutionResult.status === 'browser_missing' && scriptExecutionResult.install_command" class="result-section install-section">
                  <div class="section-title">⚠️ Playwright浏览器未安装</div>
                  <div class="install-warning">
                    <p>执行脚本需要Playwright浏览器，请先安装：</p>
                    <div class="execute-command-box">
                      <code>{{ scriptExecutionResult.install_command }}</code>
                      <el-button size="small" type="warning" @click="copyInstallCommand">复制命令</el-button>
                    </div>
                  </div>
                </div>
                
                <div v-if="scriptExecutionResult.execute_command" class="result-section">
                  <div class="section-title">执行命令（复制到终端手动执行）</div>
                  <div class="execute-command-box">
                    <code>{{ scriptExecutionResult.execute_command }}</code>
                    <el-button size="small" @click="copyExecuteCommand">复制命令</el-button>
                  </div>
                  <div v-if="scriptExecutionResult.status !== 'browser_missing'" class="script-tip" style="margin-top: 8px;">
                    提示：若浏览器未安装，请先执行 <code>python -m playwright install chromium</code> 安装
                  </div>
                </div>
                
                <div v-if="scriptExecutionResult.script_path" class="result-section">
                  <div class="section-title">脚本路径</div>
                  <div class="script-path-box">{{ scriptExecutionResult.script_path }}</div>
                </div>

                <div class="result-section">
                  <div class="section-title">执行步骤</div>
                  <div class="result-steps">
                    <div v-for="(step, i) in scriptExecutionResult.steps" :key="i" class="result-step" :class="step.status">
                      <span class="step-icon">{{ step.status === 'passed' ? '✓' : step.status === 'failed' ? '✗' : step.status === 'timeout' ? '⏱' : step.status === 'warning' ? '⚠' : step.status === 'skipped' ? '⊘' : '○' }}</span>
                      <span class="step-name">{{ step.name }}</span>
                      <span v-if="step.detail" class="step-detail">{{ step.detail }}</span>
                      <span class="step-duration">{{ step.duration }}s</span>
                    </div>
                  </div>
                </div>

                <div v-if="scriptExecutionResult.logs?.length" class="result-section">
                  <div class="section-title">执行日志</div>
                  <div class="logs-panel">
                    <div v-for="(log, i) in scriptExecutionResult.logs" :key="i" class="log-line">
                      {{ log }}
                    </div>
                  </div>
                </div>
              </div>
              <el-empty v-else description="点击执行按钮运行脚本，结果将在此显示" />
            </el-tab-pane>
          </el-tabs>
        </div>
      </div>
    </el-dialog>

    <!-- 验证码输入对话框 -->
    <el-dialog v-model="captchaInputDialogVisible" title="验证码输入" width="450px" top="20vh" :close-on-click-modal="false" :close-on-press-escape="false">
      <div class="captcha-input-dialog">
        <el-alert 
          title="脚本已暂停" 
          type="warning" 
          :description="captchaInputStatus"
          show-icon 
          :closable="false"
          style="margin-bottom: 16px"
        />
        <el-form label-position="top">
          <el-form-item label="验证码">
            <el-input 
              v-model="captchaInput" 
              placeholder="请输入验证码"
              maxlength="10"
              show-word-limit
              @keyup.enter="submitCaptchaInput"
            />
          </el-form-item>
          <el-form-item>
            <el-button 
              type="primary" 
              @click="submitCaptchaInput" 
              :loading="submittingCaptcha"
              :disabled="!captchaInput"
            >
              提交验证码
            </el-button>
            <el-button @click="cancelCaptchaInput">取消</el-button>
          </el-form-item>
        </el-form>
        <div class="captcha-input-tip">
          <p>💡 提示：</p>
          <ul>
            <li>请在浏览器中查看验证码图片</li>
            <li>将识别到的验证码输入到上方输入框</li>
            <li>点击提交后脚本将继续执行</li>
          </ul>
        </div>
      </div>
    </el-dialog>

    <!-- 验证码识别对话框 -->
    <el-dialog v-model="captchaDialogVisible" title="验证码智能识别" width="600px" top="10vh">
      <div class="captcha-container">
        <div class="captcha-input-section">
          <h4>上传验证码图片</h4>
          <el-upload
            class="captcha-uploader"
            drag
            :auto-upload="false"
            :limit="1"
            accept="image/*"
            :on-change="handleCaptchaUpload"
          >
            <el-icon class="el-icon--upload"><component :is="icons.UploadFilled" /></el-icon>
            <div class="el-upload__text">拖拽图片到此，或<em>点击选择</em></div>
            <template #tip>
              <div class="el-upload__tip">支持JPG、PNG格式的验证码图片</div>
            </template>
          </el-upload>
          <div v-if="captchaImagePreview" class="captcha-preview">
            <img :src="captchaImagePreview" alt="captcha" />
          </div>
        </div>

        <div class="captcha-recognize-section">
          <el-select v-model="captchaType" placeholder="验证码类型" style="width: 100%; margin-bottom: 12px">
            <el-option label="文字验证码" value="text" />
            <el-option label="滑块验证码" value="slider" />
            <el-option label="行为验证码" value="behavior" />
          </el-select>
          <el-button type="primary" @click="recognizeCaptcha" :loading="recognizing" :disabled="!captchaImageData">
            <el-icon><component :is="icons.View" /></el-icon>
            AI识别验证码
          </el-button>
        </div>

        <div v-if="captchaResult" class="captcha-result">
          <el-divider />
          <h4>识别结果</h4>
          <el-descriptions :column="2" border>
            <el-descriptions-item label="识别结果">
              <span class="captcha-code">{{ captchaResult.code }}</span>
            </el-descriptions-item>
            <el-descriptions-item label="置信度">
              <el-progress :percentage="captchaResult.confidence * 100" />
            </el-descriptions-item>
            <el-descriptions-item label="识别方法">
              {{ captchaResult.method }}
            </el-descriptions-item>
            <el-descriptions-item label="处理时间">
              {{ captchaResult.processing_time }}秒
            </el-descriptions-item>
          </el-descriptions>
        </div>

        <div class="captcha-login-section">
          <el-divider />
          <h4>带验证码登录测试</h4>
          <el-form :model="loginForm" label-width="80px">
            <el-form-item label="用户名">
              <el-input v-model="loginForm.username" placeholder="请输入用户名" />
            </el-form-item>
            <el-form-item label="密码">
              <el-input v-model="loginForm.password" type="password" placeholder="请输入密码" show-password />
            </el-form-item>
            <el-button type="primary" @click="testCaptchaLogin" :loading="logining">
              <el-icon><component :is="icons.User" /></el-icon>
              模拟登录
            </el-button>
          </el-form>
          <div v-if="loginResult" class="login-result">
            <el-alert :title="loginResult.message" :type="loginResult.login_success ? 'success' : 'error'" show-icon />
            <div v-if="loginResult.flow" class="login-flow">
              <div v-for="(step, i) in loginResult.flow.steps" :key="i" class="flow-step" :class="step.status">
                <span>{{ step.step }}</span>
                <el-tag size="small">{{ step.status }}</el-tag>
              </div>
            </div>
          </div>
        </div>
      </div>
    </el-dialog>

  </div>
</template>

<script setup>
import { ref, computed, onMounted, reactive, markRaw, nextTick } from 'vue'
import * as icons from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const API_BASE = '/api/v1/ui/cases'

const loading = ref(false)
const submitting = ref(false)
const searchKeyword = ref('')
const filterProject = ref('')
const filterModule = ref('')
const projectOptions = ref([])
const allModules = ref([])
const cases = ref([])

// 过滤栏模块选项（根据选中的项目过滤）
const filterModuleOptions = computed(() => {
  if (!filterProject.value) return allModules.value
  const proj = projectOptions.value.find(p => p.name === filterProject.value)
  if (!proj) return []
  return allModules.value.filter(m => m.project_id === proj.id)
})

// 表单中模块选项
const formModuleOptions = computed(() => {
  if (!form.value.project) return []
  const proj = projectOptions.value.find(p => p.name === form.value.project)
  if (!proj) return []
  return allModules.value.filter(m => m.project_id === proj.id)
})

// 录制中模块选项
const recordModuleOptions = computed(() => {
  if (!recordForm.project) return []
  const proj = projectOptions.value.find(p => p.name === recordForm.project)
  if (!proj) return []
  return allModules.value.filter(m => m.project_id === proj.id)
})

const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0
})

const filteredAllCases = computed(() => {
  let result = cases.value
  if (filterProject.value) {
    result = result.filter(c => c.project === filterProject.value)
  }
  if (filterModule.value) {
    result = result.filter(c => c.module === filterModule.value)
  }
  if (searchKeyword.value) {
    const kw = searchKeyword.value.toLowerCase()
    result = result.filter(c =>
      (c.name || '').toLowerCase().includes(kw) ||
      (c.url || '').toLowerCase().includes(kw) ||
      (c.description || '').toLowerCase().includes(kw)
    )
  }
  return result
})

const paginationTotal = computed(() => filteredAllCases.value.length)

const filteredCases = computed(() => {
  const start = (pagination.page - 1) * pagination.pageSize
  return filteredAllCases.value.slice(start, start + pagination.pageSize)
})

const dialogVisible = ref(false)
const isEditing = ref(false)
const formRef = ref(null)
const activeStepId = ref(null)

const defaultForm = () => ({
  id: null,
  name: '',
  project: '',
  module: '',
  url: '',
  description: '',
  steps: []
})

const form = ref(defaultForm())

const formRules = {
  name: [{ required: true, message: '请输入场景名称', trigger: 'blur' }],
  project: [{ required: true, message: '请选择项目', trigger: 'change' }],
  url: [
    { required: true, message: '请输入目标URL', trigger: 'blur' },
    { type: 'url', message: '请输入合法的URL', trigger: 'blur' }
  ]
}

const executeDialogVisible = ref(false)
const executing = ref(false)
const executeResult = ref(null)
const currentCase = ref(null)

const componentTypes = [
  { type: 'navigate', name: '导航', icon: markRaw(icons.Position) },
  { type: 'click', name: '点击', icon: markRaw(icons.Mouse) },
  { type: 'input', name: '输入', icon: markRaw(icons.Operation) },
  { type: 'select', name: '选择', icon: markRaw(icons.CaretBottom) },
  { type: 'wait', name: '等待', icon: markRaw(icons.Clock) },
  { type: 'assert', name: '断言', icon: markRaw(icons.CircleCheck) },
  { type: 'screenshot', name: '截图', icon: markRaw(icons.Camera) },
  { type: 'scroll', name: '滚动', icon: markRaw(icons.ArrowDown) },
  { type: 'switch', name: '条件判断', icon: markRaw(icons.Share) }
]

const draggedComponent = ref(null)

const getStepIcon = (type) => {
  const c = componentTypes.value.find(c => c.type === type)
  return c ? c.icon : icons.CircleFilled
}

const getElementPlaceholder = (type) => {
  const map = {
    navigate: '页面URL',
    click: 'CSS选择器或元素ID',
    input: 'CSS选择器或元素ID',
    select: 'CSS选择器或元素ID',
    wait: '等待条件(元素/时间)',
    assert: '断言目标(元素/文本)',
    screenshot: '保存路径',
    scroll: '滚动目标元素',
    switch: '判断条件'
  }
  return map[type] || '元素选择器'
}

const getParamsPlaceholder = (type) => {
  const map = {
    navigate: 'https://example.com',
    click: '点击次数(默认1)',
    input: '输入的文本内容',
    select: '选择的值或索引',
    wait: '等待时长(秒)',
    assert: '预期值或文本',
    screenshot: '文件名(可选)',
    scroll: '滚动方向/像素',
    switch: '条件表达式'
  }
  return map[type] || '参数值'
}

const createStep = (type) => {
  const component = componentTypes.value.find(c => c.type === type)
  return {
    id: Date.now() + Math.random(),
    type,
    name: component ? component.name : '步骤',
    element: '',
    params: '',
    delay: 0,
    retry: 0,
    timeout: 30
  }
}

const loadCases = async () => {
  loading.value = true
  try {
    const res = await fetch(API_BASE)
    if (!res.ok) throw new Error('加载失败')
    const data = await res.json()
    const rawCases = data.cases || data.data || data || []
    cases.value = rawCases.map(c => ({
      ...c,
      project: c.project || c.project_id || '',
      module: c.module || ''
    }))
  } catch (e) {
    ElMessage.error('加载场景列表失败: ' + (e.message || e))
    cases.value = []
  } finally {
    loading.value = false
  }
}

const loadProjects = async () => {
  try {
    const res = await fetch('/api/v1/projects')
    if (!res.ok) return
    const data = await res.json()
    projectOptions.value = (data.projects || []).map(p => ({ id: p.id, name: p.name }))
  } catch (e) {
    // 静默失败
  }
}

const loadAllModules = async () => {
  try {
    const res = await fetch('/api/v1/modules')
    if (!res.ok) return
    const data = await res.json()
    allModules.value = data.modules || []
  } catch (e) {
    // 静默失败
  }
}

const onFormProjectChange = () => {
  form.value.module = ''
}

const onRecordProjectChange = () => {
  recordForm.module = ''
}

const handleAdd = () => {
  isEditing.value = false
  form.value = defaultForm()
  dialogVisible.value = true
}

const handleEdit = async (row) => {
  // 直接打开脚本对话框，生成脚本供用户编辑
  currentCase.value = row
  generatedScript.value = ''
  scriptError.value = ''
  scriptExecutionResult.value = null
  scriptTab.value = 'code'
  scriptDialogVisible.value = true
  
  // 自动生成脚本
  try {
    generating.value = true
    const res = await fetch('/api/v1/ui/playwright/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ case_id: row.id })
    })
    const data = await res.json()
    if (data.success) {
      generatedScript.value = data.script
      scriptEditMode.value = true
    } else {
      scriptError.value = data.detail || '脚本生成失败'
    }
  } catch (e) {
    scriptError.value = '脚本生成失败: ' + e.message
  } finally {
    generating.value = false
  }
}

const handleDialogOpen = () => {
  activeStepId.value = form.value.steps.length > 0 ? form.value.steps[0].id : null
}

const handleDelete = (row) => {
  ElMessageBox.confirm(
    `确定要删除场景「${row.name}」吗？此操作不可恢复。`,
    '删除确认',
    {
      confirmButtonText: '确定删除',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      const res = await fetch(`${API_BASE}/${row.id}`, { method: 'DELETE' })
      if (!res.ok) throw new Error('删除失败')
      ElMessage.success('删除成功')
      loadCases()
    } catch (e) {
      ElMessage.error('删除失败')
    }
  }).catch(() => {})
}

const handleRun = async (row) => {
  currentCase.value = row
  executeResult.value = null
  executing.value = true
  executeDialogVisible.value = true

  try {
    // 第一步：生成Playwright脚本
    const genRes = await fetch('/api/v1/ui/playwright/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ case_id: row.id })
    })
    if (!genRes.ok) throw new Error('脚本生成失败')
    const genData = await genRes.json()
    if (!genData.success) throw new Error(genData.detail || '脚本生成失败')

    const generatedScript = genData.script

    // 第二步：执行生成的脚本
    const execRes = await fetch('/api/v1/ui/playwright/execute', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        script: generatedScript,
        headless: headlessMode.value
      })
    })
    if (!execRes.ok) throw new Error('脚本执行失败')
    const execData = await execRes.json()
    if (execData.success) {
      // 将后端返回的日志字符串转换为前端期望的格式
      const rawLogs = execData.result?.logs || []
      const formattedLogs = rawLogs.map((log, idx) => {
        if (typeof log === 'string') {
          // 根据日志内容判断级别
          let level = 'info'
          if (log.includes('ERROR') || log.includes('Error') || log.includes('failed') || log.includes('失败')) {
            level = 'error'
          } else if (log.includes('SUCCESS') || log.includes('success') || log.includes('通过') || log.includes('passed')) {
            level = 'success'
          } else if (log.includes('WARN') || log.includes('warning') || log.includes('警告')) {
            level = 'warning'
          }
          return { level, message: log, step: idx + 1 }
        }
        return log
      })
      
      // 获取截图路径
      const screenshots = execData.result?.screenshots || []
      const screenshotUrl = screenshots.length > 0 ? screenshots[screenshots.length - 1] : null
      
      executeResult.value = {
        success: execData.result?.status === 'completed',
        total_steps: execData.result?.steps?.length || row.steps?.length || 0,
        passed: execData.result?.steps?.filter(s => s.status === 'passed').length || 0,
        failed: execData.result?.steps?.filter(s => s.status === 'failed').length || 0,
        duration: execData.result?.duration || 0,
        logs: formattedLogs,
        screenshot: screenshotUrl
      }
    } else {
      executeResult.value = {
        success: false,
        logs: [{ level: 'error', message: execData.detail || '执行失败', step: 0 }],
        total_steps: 0,
        passed: 0,
        failed: 0,
        duration: 0
      }
    }
  } catch (e) {
    executeResult.value = {
      success: false,
      logs: [
        { level: 'error', message: '执行请求失败：' + e.message, step: 0 }
      ],
      total_steps: 0,
      passed: 0,
      failed: 0,
      duration: 0
    }
  } finally {
    executing.value = false
  }
}

const handleDragStart = (component) => {
  draggedComponent.value = component
}

const handleDrop = () => {
  if (draggedComponent.value) {
    form.value.steps.push(createStep(draggedComponent.value.type))
    draggedComponent.value = null
  }
}

const handleAddStep = (type) => {
  form.value.steps.push(createStep(type))
}

const handleRemoveStep = (id) => {
  form.value.steps = form.value.steps.filter(s => s.id !== id)
  if (activeStepId.value === id) {
    activeStepId.value = form.value.steps.length > 0 ? form.value.steps[0].id : null
  }
}

const handleDuplicateStep = (step) => {
  const newStep = JSON.parse(JSON.stringify(step))
  newStep.id = Date.now() + Math.random()
  const idx = form.value.steps.findIndex(s => s.id === step.id)
  form.value.steps.splice(idx + 1, 0, newStep)
}

const moveStep = (index, direction) => {
  const newIndex = index + direction
  if (newIndex < 0 || newIndex >= form.value.steps.length) return
  const temp = form.value.steps[index]
  form.value.steps.splice(index, 1)
  form.value.steps.splice(newIndex, 0, temp)
}

const handleSubmit = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (!valid) {
      ElMessage.warning('请检查表单填写')
      return
    }

    submitting.value = true
    try {
      const payload = {
        name: form.value.name,
        project: form.value.project,
        project_id: form.value.project,
        module: form.value.module || '',
        url: form.value.url,
        description: form.value.description,
        steps: form.value.steps.map(s => ({
          type: s.type,
          name: s.name,
          element: s.element,
          params: s.params,
          delay: s.delay,
          retry: s.retry,
          timeout: s.timeout
        }))
      }

      if (isEditing.value) {
        const res = await fetch(`${API_BASE}/${form.value.id}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        })
        if (!res.ok) throw new Error('保存失败')
        ElMessage.success('更新成功')
      } else {
        const res = await fetch(API_BASE, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        })
        if (!res.ok) throw new Error('创建失败')
        ElMessage.success('创建成功')
      }

      dialogVisible.value = false
      loadCases()
    } catch (e) {
      ElMessage.error(isEditing.value ? '保存失败' : '创建失败')
    } finally {
      submitting.value = false
    }
  })
}

const formatTime = (t) => {
  if (!t) return '-'
  const d = new Date(t)
  if (isNaN(d.getTime())) return t
  const pad = (n) => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`
}

onMounted(() => {
  loadCases()
  loadProjects()
  loadAllModules()
})

// ===== 知识图谱功能 =====
const graphDialogVisible = ref(false)
const graphLoading = ref(false)
const analyzing = ref(false)
const graphData = ref(null)
const graphProjectId = ref('')
const graphSearchUrl = ref('')

const graphPages = computed(() => {
  if (!graphData.value) return []
  const pageMap = {}
  graphData.value.graph.nodes.forEach(node => {
    if (node.type === 'element') {
      const page = node.page || '其他'
      if (!pageMap[page]) {
        pageMap[page] = { name: page, elements: [] }
      }
      pageMap[page].elements.push(node)
    }
  })
  return Object.values(pageMap)
})

const graphCases = computed(() => {
  if (!graphData.value) return []
  return graphData.value.graph.nodes.filter(n => n.type === 'case')
})

const getLocatorTag = (type) => {
  const map = { xpath: 'danger', css: 'success', id: 'warning', name: 'info', link_text: '' }
  return map[type] || 'info'
}

const loadKnowledgeGraph = async () => {
  graphLoading.value = true
  try {
    const url = graphProjectId.value ? `/api/v1/ui/knowledge_graph?project_id=${graphProjectId.value}` : '/api/v1/ui/knowledge_graph'
    const res = await fetch(url)
    const data = await res.json()
    if (data.success) {
      graphData.value = data
      ElMessage.success('知识图谱生成成功')
    }
  } catch (e) {
    ElMessage.error('加载知识图谱失败')
  } finally {
    graphLoading.value = false
  }
}

const analyzePageStructure = async () => {
  if (!graphSearchUrl.value) {
    ElMessage.warning('请输入要分析的URL')
    return
  }
  analyzing.value = true
  try {
    const res = await fetch('/api/v1/ui/knowledge_graph/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url: graphSearchUrl.value, project_id: graphProjectId.value })
    })
    const data = await res.json()
    if (data.success) {
      ElMessage.success('页面分析完成')
      // 自动加载知识图谱
      await loadKnowledgeGraph()
    }
  } catch (e) {
    ElMessage.error('页面分析失败')
  } finally {
    analyzing.value = false
  }
}

// ===== Playwright脚本生成功能 =====
const scriptDialogVisible = ref(false)
const scriptTab = ref('code')
const generating = ref(false)
const executingScript = ref(false)
const generatedScript = ref('')
const scriptExecutionResult = ref(null)
const headlessMode = ref(false)
const scriptError = ref('')
const scriptEditMode = ref(false)
const savingScript = ref(false)

// ===== 验证码输入功能 =====
const captchaInputDialogVisible = ref(false)
const captchaInput = ref('')
const captchaInputStatus = ref('脚本在执行过程中遇到了验证码，请输入验证码以继续执行')
const submittingCaptcha = ref(false)
const currentCaptchaSessionId = ref('')
let captchaStatusPollingTimer = null

const handleGenerateScript = async (row) => {
  currentCase.value = row
  generatedScript.value = ''
  scriptExecutionResult.value = null
  scriptTab.value = 'code'
  scriptDialogVisible.value = true
  await generateScript()
}

const generateScript = async () => {
  if (!currentCase.value) {
    ElMessage.warning('请先选择用例')
    return
  }
  scriptError.value = ''
  generating.value = true
  try {
    const res = await fetch('/api/v1/ui/playwright/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ case_id: currentCase.value.id })
    })
    const data = await res.json()
    if (data.success) {
      generatedScript.value = data.script
      scriptTab.value = 'code'
      ElMessage.success('Python Playwright脚本生成成功')
    }
  } catch (e) {
    scriptError.value = '脚本生成失败'
    ElMessage.error('脚本生成失败')
  } finally {
    generating.value = false
  }
}

const copyScript = async () => {
  if (!generatedScript.value) return
  try {
    await navigator.clipboard.writeText(generatedScript.value)
    ElMessage.success('脚本已复制到剪贴板')
  } catch (e) {
    ElMessage.error('复制失败')
  }
}

const saveScript = async () => {
  if (!generatedScript.value) return
  savingScript.value = true
  try {
    // 保存脚本到文件系统
    const res = await fetch('/api/v1/ui/playwright/save', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        script: generatedScript.value,
        case_name: currentCase.value?.name || '未命名用例'
      })
    })
    const data = await res.json()
    if (data.success) {
      ElMessage.success(`脚本保存成功: ${data.filename}`)
      
      // 如果有当前用例，更新用例列表中的脚本
      if (currentCase.value?.id) {
        try {
          await fetch(`${API_BASE}/${currentCase.value.id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              script: generatedScript.value
            })
          })
          // 更新本地数据
          const caseIndex = cases.value.findIndex(c => c.id === currentCase.value.id)
          if (caseIndex !== -1) {
            cases.value[caseIndex].script = generatedScript.value
          }
        } catch (e) {
          console.warn('更新用例脚本失败:', e)
        }
      }
    } else {
      ElMessage.error(data.detail || '保存失败')
    }
  } catch (e) {
    ElMessage.error('保存脚本失败')
  } finally {
    savingScript.value = false
  }
}

const executeScript = async () => {
  if (!generatedScript.value) return
  scriptError.value = ''
  executingScript.value = true
  scriptTab.value = 'result'
  scriptExecutionResult.value = null
  
  ElMessageBox.confirm(
    headlessMode.value 
      ? '即将以无头模式执行脚本，后台将启动Playwright浏览器运行测试。' 
      : '即将以有头模式执行脚本，将会打开浏览器窗口展示执行过程。',
    '确认执行',
    { confirmButtonText: '执行', cancelButtonText: '取消', type: 'info' }
  ).then(async () => {
    try {
      const res = await fetch('/api/v1/ui/playwright/execute', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          script: generatedScript.value, 
          headless: headlessMode.value 
        })
      })
      const data = await res.json()
      if (data.success) {
        scriptExecutionResult.value = data.result
        ElMessage.success('脚本执行完成！')
      } else {
        scriptError.value = data.detail || '执行失败'
        ElMessage.error(scriptError.value)
      }
    } catch (e) {
      let errorMsg = '脚本执行失败'
      try {
        const errData = await e.json?.()
        if (errData?.detail) errorMsg = errData.detail
      } catch {}
      scriptError.value = errorMsg
      ElMessage.error(errorMsg)
    } finally {
      executingScript.value = false
    }
  }).catch(() => {
    executingScript.value = false
  })
}

// ===== 验证码输入相关方法 =====
const openCaptchaInputDialog = (sessionId) => {
  currentCaptchaSessionId.value = sessionId
  captchaInput.value = ''
  captchaInputDialogVisible.value = true
  startCaptchaStatusPolling()
}

const startCaptchaStatusPolling = () => {
  if (captchaStatusPollingTimer) {
    clearInterval(captchaStatusPollingTimer)
  }
  captchaStatusPollingTimer = setInterval(async () => {
    try {
      const res = await fetch(`/api/v1/ui/playwright/captcha/status/${currentCaptchaSessionId.value}`)
      const data = await res.json()
      if (data.status === 'submitted') {
        captchaInputStatus.value = '验证码已提交，脚本正在继续执行...'
        stopCaptchaStatusPolling()
        captchaInputDialogVisible.value = false
        ElMessage.success('验证码已提交，脚本继续执行')
      }
    } catch {}
  }, 2000)
}

const stopCaptchaStatusPolling = () => {
  if (captchaStatusPollingTimer) {
    clearInterval(captchaStatusPollingTimer)
    captchaStatusPollingTimer = null
  }
}

const submitCaptchaInput = async () => {
  if (!captchaInput.value) return
  submittingCaptcha.value = true
  try {
    const res = await fetch('/api/v1/ui/playwright/captcha/input', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        session_id: currentCaptchaSessionId.value,
        captcha_code: captchaInput.value.trim()
      })
    })
    const data = await res.json()
    if (data.success) {
      captchaInputStatus.value = '验证码已提交，脚本正在继续执行...'
      stopCaptchaStatusPolling()
      setTimeout(() => {
        captchaInputDialogVisible.value = false
        ElMessage.success('验证码已提交，脚本继续执行')
      }, 1000)
    }
  } catch (e) {
    ElMessage.error('提交验证码失败')
  } finally {
    submittingCaptcha.value = false
  }
}

const cancelCaptchaInput = () => {
  stopCaptchaStatusPolling()
  captchaInputDialogVisible.value = false
  ElMessage.warning('已取消验证码输入，脚本可能会继续等待')
}

const generatePlaywrightFromGraph = async () => {
  if (!currentCase.value) {
    ElMessage.warning('请先在列表中选择一个用例')
    return
  }
  await handleGenerateScript(currentCase.value)
}

// ===== 执行结果辅助函数 =====
const getExecutionTitle = () => {
  const status = scriptExecutionResult.value?.status
  if (status === 'completed') return '执行成功！'
  if (status === 'failed') return '执行失败'
  if (status === 'timeout') return '执行超时'
  if (status === 'ready') return '脚本已保存'
  if (status === 'browser_missing') return '浏览器未安装'
  return '执行状态'
}

const getExecutionAlertType = () => {
  const status = scriptExecutionResult.value?.status
  if (status === 'completed') return 'success'
  if (status === 'failed') return 'error'
  if (status === 'timeout') return 'warning'
  if (status === 'browser_missing') return 'warning'
  return 'info'
}

const getExecutionDescription = () => {
  const status = scriptExecutionResult.value?.status
  if (status === 'completed') return '浏览器已成功执行所有步骤'
  if (status === 'failed') return '脚本执行过程中出现错误，请查看日志'
  if (status === 'timeout') return '脚本执行超时，可能页面加载时间过长'
  if (status === 'ready') return '脚本已保存，可通过命令行手动执行'
  if (status === 'browser_missing') return 'Playwright浏览器未安装，需要先安装浏览器才能执行'
  return ''
}

const getStatusText = () => {
  const status = scriptExecutionResult.value?.status
  if (status === 'completed') return '成功'
  if (status === 'failed') return '失败'
  if (status === 'timeout') return '超时'
  if (status === 'ready') return '就绪'
  if (status === 'browser_missing') return '需安装浏览器'
  return status
}

const copyExecuteCommand = async () => {
  if (!scriptExecutionResult.value?.execute_command) return
  try {
    await navigator.clipboard.writeText(scriptExecutionResult.value.execute_command)
    ElMessage.success('执行命令已复制到剪贴板')
  } catch (e) {
    ElMessage.error('复制失败')
  }
}

const copyInstallCommand = async () => {
  if (!scriptExecutionResult.value?.install_command) return
  try {
    await navigator.clipboard.writeText(scriptExecutionResult.value.install_command)
    ElMessage.success('安装命令已复制到剪贴板')
  } catch (e) {
    ElMessage.error('复制失败')
  }
}

// ===== 验证码识别功能 =====
const captchaDialogVisible = ref(false)
const captchaImageData = ref('')
const captchaImagePreview = ref('')
const captchaType = ref('text')
const captchaResult = ref(null)
const recognizing = ref(false)
const logining = ref(false)
const loginResult = ref(null)

const loginForm = reactive({
  username: 'admin',
  password: '123456'
})

const handleCaptchaUpload = (file) => {
  const reader = new FileReader()
  reader.onload = (e) => {
    captchaImageData.value = e.target.result
    captchaImagePreview.value = e.target.result
  }
  reader.readAsDataURL(file.raw)
}

const recognizeCaptcha = async () => {
  if (!captchaImageData.value) {
    ElMessage.warning('请先上传验证码图片')
    return
  }
  recognizing.value = true
  try {
    const res = await fetch('/api/v1/ui/captcha/recognize', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ image: captchaImageData.value, type: captchaType.value })
    })
    const data = await res.json()
    if (data.success) {
      captchaResult.value = data.result
      ElMessage.success('验证码识别成功')
    }
  } catch (e) {
    ElMessage.error('验证码识别失败')
  } finally {
    recognizing.value = false
  }
}

const testCaptchaLogin = async () => {
  if (!loginForm.username || !loginForm.password) {
    ElMessage.warning('请输入用户名和密码')
    return
  }
  logining.value = true
  loginResult.value = null
  try {
    const res = await fetch('/api/v1/ui/captcha/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        username: loginForm.username,
        password: loginForm.password,
        captcha_type: captchaType.value
      })
    })
    const data = await res.json()
    if (data.success) {
      loginResult.value = {
        login_success: true,
        message: data.flow?.message || '登录成功',
        flow: data.flow
      }
      ElMessage.success('登录测试完成')
    }
  } catch (e) {
    ElMessage.error('登录测试失败')
  } finally {
    logining.value = false
  }
}

// ===== 自动录制脚本 =====
const recorderVisible = ref(false)
const recording = ref(false)
const recorderLoading = ref(false)
const recordedActions = ref([])
const recorderResult = ref(null)
const recorderError = ref('')
const showFullScript = ref(true)
const recordSessionId = ref('')
let pollTimer = null

const recordForm = reactive({
  url: '',
  project: '',
  module: '',
  caseName: ''
})
const savingToCaseList = ref(false)

const getActionTypeText = (type) => {
  const map = {
    click: '点击',
    input: '输入',
    select: '选择',
    hover: '悬停',
    navigate: '导航',
    scroll: '滚动',
    wait: '等待'
  }
  return map[type] || type
}

const getActionTagType = (type) => {
  const map = {
    click: 'primary',
    input: 'success',
    select: 'warning',
    hover: 'info',
    navigate: 'danger'
  }
  return map[type] || ''
}

const openRecorder = () => {
  recorderVisible.value = true
  recordedActions.value = []
  recorderResult.value = null
  recorderError.value = ''
  recording.value = false
  recordSessionId.value = ''
}

const resetRecorder = () => {
  recordedActions.value = []
  recorderResult.value = null
  recorderError.value = ''
  recording.value = false
  recordSessionId.value = ''
}

const startAutoRecording = async () => {
  if (!recordForm.url) {
    ElMessage.warning('请输入目标URL')
    return
  }

  recorderLoading.value = true
  recorderError.value = ''
  recordedActions.value = []
  recorderResult.value = null

  try {
    // 调用后端API启动Playwright浏览器进行自动录制
    const res = await fetch('/api/v1/ui/record/browser/start', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        url: recordForm.url,
        headless: false
      })
    })
    const data = await res.json()
    if (data.success) {
      recording.value = true
      recordSessionId.value = data.session_id
      ElMessage.success('浏览器已启动，请在新打开的浏览器窗口中进行操作')

      // 开始轮询获取录制操作
      startPollingActions()
    } else {
      recorderError.value = data.detail || data.message || '启动录制失败'
      ElMessage.error(recorderError.value)
    }
  } catch (e) {
    recorderError.value = '启动录制失败：' + e.message
    ElMessage.error('启动录制失败，请检查后端服务是否正常运行')
  } finally {
    recorderLoading.value = false
  }
}

const startPollingActions = () => {
  if (pollTimer) clearInterval(pollTimer)

  pollTimer = setInterval(async () => {
    if (!recordSessionId.value || !recording.value) {
      if (pollTimer) clearInterval(pollTimer)
      return
    }

    try {
      const res = await fetch(`/api/v1/ui/record/${recordSessionId.value}`)
      const data = await res.json()
      if (data.success) {
        const session = data.session
        recordedActions.value = session.actions || []

        // 检查录制状态
        if (session.status === 'stopped' || session.status === 'error') {
          recording.value = false
          if (pollTimer) clearInterval(pollTimer)

          if (session.status === 'error') {
            recorderError.value = session.message || '录制过程中出错'
          } else if (recordedActions.value.length > 0) {
            ElMessage.info(`浏览器已关闭，共录制 ${recordedActions.value.length} 个操作`)
          }
        }
      }
    } catch (e) {
      // 轮询失败，忽略
    }
  }, 1000) // 每秒轮询一次
}

const stopAutoRecording = async () => {
  recording.value = false
  if (pollTimer) {
    clearInterval(pollTimer)
    pollTimer = null
  }

  // 调用停止API生成脚本
  await generateScriptFromRecording()
}

const generateScriptFromRecording = async () => {
  if (recordedActions.value.length === 0) {
    ElMessage.warning('暂无录制操作，无法生成脚本')
    return
  }

  try {
    const res = await fetch('/api/v1/ui/record/stop', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        session_id: recordSessionId.value || 'manual_' + Date.now(),
        case_name: recordForm.caseName || '录制场景',
        url: recordForm.url,
        actions: recordedActions.value
      })
    })
    const data = await res.json()
    if (data.success) {
      recorderResult.value = data
      ElMessage.success('脚本生成成功')
    } else {
      ElMessage.error(data.detail || '脚本生成失败')
    }
  } catch (e) {
    ElMessage.error('脚本生成失败')
  }
}

const removeAction = (index) => {
  recordedActions.value = recordedActions.value.filter((_, i) => i !== index)
}

const clearRecordedActions = () => {
  ElMessageBox.confirm('确定要清空所有录制的操作吗？', '确认', {
    type: 'warning'
  }).then(() => {
    recordedActions.value = []
    ElMessage.success('已清空')
  }).catch(() => {})
}

const onRecorderClose = () => {
  // 关闭对话框时停止录制
  if (recording.value) {
    recording.value = false
    if (pollTimer) {
      clearInterval(pollTimer)
      pollTimer = null
    }
  }
}

const copyToClipboard = async (text) => {
  try {
    await navigator.clipboard.writeText(text)
    ElMessage.success('已复制到剪贴板')
  } catch (e) {
    ElMessage.error('复制失败')
  }
}

const useGeneratedScript = (result) => {
  generatedScript.value = result.script
  scriptError.value = ''
  scriptExecutionResult.value = null
  scriptTab.value = 'code'
  scriptDialogVisible.value = true
  recorderVisible.value = false
}

const saveRecordingToCaseList = async () => {
  // 如果未填写场景名称，提示用户输入
  if (!recordForm.caseName) {
    ElMessageBox.prompt('请输入场景名称', '保存到用例列表', {
      confirmButtonText: '保存',
      cancelButtonText: '取消',
      inputPlaceholder: '请输入场景名称',
      inputValidator: (val) => !!val && val.trim() !== '' || '场景名称不能为空'
    }).then(async ({ value }) => {
      recordForm.caseName = value.trim()
      await doSaveRecordingToCaseList()
    }).catch(() => {})
    return
  }
  await doSaveRecordingToCaseList()
}

const doSaveRecordingToCaseList = async () => {
  if (!recordForm.caseName) {
    ElMessage.warning('请输入场景名称')
    return
  }
  if (!recordForm.project) {
    ElMessage.warning('请选择所属项目')
    return
  }
  savingToCaseList.value = true
  try {
    // 获取项目ID
    const projectObj = projectOptions.value.find(p => p.name === recordForm.project)
    const projectId = projectObj ? projectObj.id : ''
    
    // 将录制的操作转换为步骤
    const steps = recordedActions.value.map((action, i) => {
      const step = {
        id: Date.now() + i,
        type: action.type || 'click',
        name: `步骤${i + 1}: ${getActionTypeText(action.type)}`,
        element: action.text || '',
        params: {}
      }
      if (action.type === 'navigate') {
        step.params.url = action.url || ''
      } else if (action.type === 'input') {
        step.params.value = action.value || ''
      }
      return step
    })

    const caseData = {
      name: recordForm.caseName,
      project: recordForm.project,
      project_id: projectId,
      module: recordForm.module || '',
      url: recordForm.url,
      description: `自动录制脚本，共${recordedActions.value.length}个操作`,
      steps: steps,
      script: recorderResult.value?.script || ''
    }

    const res = await fetch(API_BASE, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(caseData)
    })
    const data = await res.json()
    if (data.success !== false) {
      ElMessage.success('已保存到用例列表')
      recorderVisible.value = false
      loadCases()
    } else {
      ElMessage.error(data.detail || data.message || '保存失败')
    }
  } catch (e) {
    ElMessage.error('保存失败: ' + e.message)
  } finally {
    savingToCaseList.value = false
  }
}

const toggleScriptPreview = () => {
  showFullScript.value = !showFullScript.value
}
</script>

<style scoped>
.ui-cases {
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

.main-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  flex-wrap: wrap;
  gap: 12px;
}

.toolbar-left {
  display: flex;
  gap: 12px;
}

.toolbar-right {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.table-actions {
  display: flex;
  gap: 4px;
  flex-wrap: nowrap;
  white-space: nowrap;
}

.table-actions .action-btn {
  flex-shrink: 0;
}

.pagination-wrapper {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}

.case-name {
  font-weight: 500;
  color: #1f2937;
}

.url-text {
  font-family: 'Monaco', 'Menlo', monospace;
  font-size: 12px;
  color: #6366f1;
}

.time-text {
  color: #6b7280;
  font-size: 13px;
}

.dialog-content {
  max-height: 70vh;
  overflow-y: auto;
}

.case-form {
  margin-bottom: 16px;
}

.orchestration-section {
  border-top: 1px solid #e5e7eb;
  padding-top: 16px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  flex-wrap: wrap;
  gap: 8px;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
}

.section-actions {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.orchestration-body {
  display: grid;
  grid-template-columns: 160px 1fr;
  gap: 16px;
}

.component-library {
  background-color: #f9fafb;
  border-radius: 8px;
  padding: 12px;
}

.library-title {
  font-size: 13px;
  font-weight: 600;
  color: #374151;
  margin-bottom: 10px;
}

.component-grid {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.component-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 10px;
  background-color: #fff;
  border-radius: 6px;
  cursor: grab;
  font-size: 13px;
  transition: all 0.15s;
  border: 1px solid transparent;
}

.component-item:hover {
  border-color: #6366f1;
  background-color: #f5f3ff;
}

.flow-canvas {
  min-height: 300px;
  border: 2px dashed #d1d5db;
  border-radius: 8px;
  padding: 12px;
  background-color: #fafafa;
}

.empty-canvas {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 240px;
  color: #9ca3af;
  gap: 12px;
}

.empty-icon {
  color: #c0c4cc;
}

.steps-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.step-card {
  background-color: #fff;
  border-radius: 8px;
  border: 2px solid #e5e7eb;
  transition: border-color 0.2s;
}

.step-card:hover {
  border-color: #a5b4fc;
}

.step-card-active {
  border-color: #6366f1;
}

.step-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background-color: #f9fafb;
  border-radius: 6px 6px 0 0;
  border-bottom: 1px solid #e5e7eb;
}

.step-num {
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background-color: #6366f1;
  color: white;
  font-size: 11px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.step-name {
  flex: 1;
  font-weight: 500;
  font-size: 14px;
}

.step-actions {
  display: flex;
  gap: 2px;
}

.step-body {
  padding: 10px 12px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}

.execute-content {
  min-height: 200px;
}

.executing-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 0;
  color: #6b7280;
  gap: 12px;
}

.executing-state p {
  margin: 0;
}

.executing-tip {
  font-size: 13px;
  color: #9ca3af;
}

.execute-result {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.result-header {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.result-stats {
  display: flex;
  gap: 16px;
  font-size: 13px;
  color: #6b7280;
}

.stat-success {
  color: #10b981;
  font-weight: 600;
}

.stat-fail {
  color: #ef4444;
  font-weight: 600;
}

.log-panel {
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  overflow: hidden;
}

.log-title {
  padding: 8px 12px;
  background-color: #f3f4f6;
  font-size: 13px;
  font-weight: 600;
  color: #374151;
}

.log-content {
  max-height: 260px;
  overflow-y: auto;
  padding: 8px 12px;
  background-color: #1e1e2e;
  font-family: 'Monaco', 'Menlo', monospace;
  font-size: 12px;
}

.log-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 4px 0;
  color: #d1d5db;
  word-break: break-all;
}

.log-item.info {
  color: #93c5fd;
}

.log-item.success {
  color: #6ee7b7;
}

.log-item.error {
  color: #fca5a5;
}

.log-step {
  color: #9ca3af;
}

.log-duration {
  margin-left: auto;
  color: #9ca3af;
  font-size: 11px;
}

.log-icon {
  flex-shrink: 0;
}

.screenshot-panel {
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  overflow: hidden;
}

.screenshot-img {
  width: 100%;
  max-height: 300px;
  object-fit: contain;
  background-color: #f9fafb;
}

/* ===== 知识图谱样式 ===== */
.graph-container {
  max-height: 60vh;
  overflow-y: auto;
}

.graph-toolbar {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
  align-items: center;
}

.graph-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.graph-stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
}

.stat-card {
  padding: 12px;
  background-color: #f9fafb;
  border-radius: 8px;
  text-align: center;
}

.stat-card .stat-value {
  font-size: 24px;
  font-weight: 700;
  color: #6366f1;
}

.stat-card .stat-label {
  font-size: 12px;
  color: #6b7280;
  margin-top: 4px;
}

.graph-pages {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.page-section {
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  overflow: hidden;
}

.page-header-bar {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 14px;
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  color: white;
}

.page-name {
  font-weight: 600;
  font-size: 14px;
}

.page-element-count {
  margin-left: auto;
  background-color: rgba(255, 255, 255, 0.2);
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 12px;
}

.page-elements {
  padding: 10px 14px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.element-row {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 6px 10px;
  background-color: #f9fafb;
  border-radius: 6px;
  font-size: 13px;
}

.element-name {
  font-weight: 500;
  color: #1f2937;
  flex: 1;
}

.element-locator {
  font-family: 'Monaco', 'Menlo', monospace;
  font-size: 11px;
  color: #6b7280;
  max-width: 300px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* ===== 脚本生成样式 ===== */
.script-container {
  max-height: 60vh;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.script-toolbar {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px;
  background-color: #f9fafb;
  border-radius: 8px;
}

.script-toolbar span {
  font-weight: 500;
  color: #374151;
  margin-right: auto;
}

.script-tabs {
  flex: 1;
}

.script-code {
  background-color: #1e1e2e;
  color: #d1d5db;
  padding: 16px;
  border-radius: 8px;
  font-family: 'Monaco', 'Menlo', monospace;
  font-size: 12px;
  line-height: 1.6;
  max-height: 400px;
  overflow-y: auto;
  white-space: pre-wrap;
  word-break: break-all;
}

.script-code-editor {
  width: 100%;
  min-height: 400px;
  background-color: #1e1e2e;
  color: #d1d5db;
  padding: 16px;
  border-radius: 8px;
  font-family: 'Monaco', 'Menlo', monospace;
  font-size: 12px;
  line-height: 1.6;
  border: 2px solid #3b3b4f;
  resize: vertical;
  outline: none;
  tab-size: 4;
}

.script-code-editor:focus {
  border-color: #6366f1;
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
}

.script-code-wrapper {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.script-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background-color: #f5f5f5;
  border-radius: 6px 6px 0 0;
}

.script-header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.script-language {
  font-weight: 600;
  color: #374151;
}

.script-tip {
  color: #9ca3af;
  font-size: 12px;
}

.script-footer {
  display: flex;
  justify-content: flex-end;
  padding: 4px 12px;
  background-color: #f9fafb;
  border-radius: 0 0 6px 6px;
}

.script-footer-info {
  color: #9ca3af;
  font-size: 12px;
}

.execution-result {
  display: flex;
  flex-direction: column;
  gap: 12px;
  max-height: 60vh;
  overflow-y: auto;
  padding-right: 8px;
}

.execution-result::-webkit-scrollbar {
  width: 8px;
}

.execution-result::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

.execution-result::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 4px;
}

.execution-result::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

.result-stats {
  display: flex;
  gap: 16px;
}

.result-stats .el-tag {
  font-size: 14px;
  padding: 4px 12px;
}

/* ===== 验证码识别样式 ===== */
.captcha-container {
  max-height: 60vh;
  overflow-y: auto;
}

.captcha-section {
  margin-bottom: 20px;
}

.captcha-section-title {
  font-size: 14px;
  font-weight: 600;
  color: #374151;
  margin-bottom: 10px;
}

.captcha-upload {
  display: flex;
  gap: 16px;
  align-items: flex-start;
}

.captcha-upload-result {
  flex: 1;
}

.captcha-preview {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.captcha-preview img {
  max-width: 200px;
  max-height: 100px;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
}

.captcha-result-box {
  background-color: #f9fafb;
  border-radius: 8px;
  padding: 16px;
  text-align: center;
}

.recognized-code {
  font-size: 32px;
  font-weight: 700;
  font-family: 'Monaco', 'Menlo', monospace;
  color: #6366f1;
  margin: 8px 0;
  letter-spacing: 4px;
}

.captcha-confidence {
  font-size: 13px;
  color: #6b7280;
}

.captcha-method {
  margin-top: 8px;
}

.login-section {
  border-top: 1px solid #e5e7eb;
  padding-top: 20px;
}

.login-result {
  margin-top: 16px;
}

.login-success {
  color: #10b981;
}

.login-failed {
  color: #ef4444;
}

.login-flow {
  margin-top: 12px;
  padding: 12px;
  background-color: #f9fafb;
  border-radius: 6px;
}

.login-flow-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 4px 0;
  font-size: 13px;
}

.flow-step-icon {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 11px;
  flex-shrink: 0;
}

.flow-step-icon.success {
  background-color: #10b981;
}

.flow-step-icon.error {
  background-color: #ef4444;
}

.flow-step-icon.processing {
  background-color: #f59e0b;
}

/* ===== 脚本生成对话框新样式 ===== */
.script-error {
  margin-bottom: 12px;
}

.script-code-wrapper {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.script-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 6px 12px;
  background-color: #374151;
  border-radius: 6px 6px 0 0;
  color: white;
}

.script-language {
  font-weight: 600;
  font-size: 13px;
}

.script-tip {
  font-size: 12px;
  color: #9ca3af;
}

.result-section {
  margin-top: 16px;
}

.section-title {
  font-size: 14px;
  font-weight: 600;
  color: #374151;
  margin-bottom: 8px;
}

.result-steps {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.result-step {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 12px;
  background-color: #f9fafb;
  border-radius: 6px;
  border-left: 3px solid #9ca3af;
}

.result-step.passed {
  border-left-color: #10b981;
  background-color: #f0fdf4;
}

.result-step.failed {
  border-left-color: #ef4444;
  background-color: #fef2f2;
}

.result-step.running {
  border-left-color: #f59e0b;
  background-color: #fffbeb;
}

.step-icon {
  width: 22px;
  height: 22px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  color: white;
  flex-shrink: 0;
  background-color: #9ca3af;
}

.passed .step-icon {
  background-color: #10b981;
}

.failed .step-icon {
  background-color: #ef4444;
}

.running .step-icon {
  background-color: #f59e0b;
}

.step-name {
  flex: 1;
  font-size: 13px;
}

.step-detail {
  font-size: 12px;
  color: #6b7280;
  font-family: 'Monaco', 'Menlo', monospace;
}

.step-duration {
  font-size: 12px;
  color: #6b7280;
  font-family: 'Monaco', 'Menlo', monospace;
}

.screenshots-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 12px;
}

.screenshot-item {
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  overflow: hidden;
}

.screenshot-item img {
  width: 100%;
  height: 120px;
  object-fit: cover;
  display: block;
}

.logs-panel {
  background-color: #1e1e2e;
  border-radius: 6px;
  padding: 12px;
  max-height: 300px;
  overflow-y: auto;
  font-family: 'Monaco', 'Menlo', monospace;
  font-size: 12px;
}

.logs-panel::-webkit-scrollbar {
  width: 6px;
}

.logs-panel::-webkit-scrollbar-track {
  background: #2d2d3f;
  border-radius: 3px;
}

.logs-panel::-webkit-scrollbar-thumb {
  background: #4b5563;
  border-radius: 3px;
}

.logs-panel::-webkit-scrollbar-thumb:hover {
  background: #6b7280;
}

.log-line {
  color: #d1d5db;
  padding: 2px 0;
  word-break: break-all;
}

.log-line:nth-child(odd) {
  color: #9ca3af;
}

.stat-value.completed {
  color: #10b981;
  font-weight: 600;
}

.stat-value.failed {
  color: #ef4444;
  font-weight: 600;
}

.stat-value.timeout {
  color: #f59e0b;
  font-weight: 600;
}

.stat-value.ready {
  color: #3b82f6;
  font-weight: 600;
}

.stat-value.browser_missing {
  color: #f59e0b;
  font-weight: 600;
}

.install-section {
  background: #fdf6ec;
  border: 1px solid #faecd8;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 16px;
}

.install-warning p {
  margin: 0 0 12px 0;
  color: #8a6d3b;
  font-size: 14px;
}

.execute-command-box {
  background: #f5f7fa;
  border: 1px solid #e4e7ed;
  border-radius: 6px;
  padding: 12px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.execute-command-box code {
  flex: 1;
  font-family: Consolas, Monaco, monospace;
  font-size: 13px;
  color: #303133;
  word-break: break-all;
  white-space: pre-wrap;
}

.script-path-box {
  background: #f5f7fa;
  border: 1px solid #e4e7ed;
  border-radius: 6px;
  padding: 8px 12px;
  font-family: Consolas, Monaco, monospace;
  font-size: 13px;
  color: #606266;
}

/* ===== 录制对话框样式 ===== */
.recorder-dialog {
  --el-dialog-width: 1000px;
}

.recorder-container {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.recorder-input-section {
  background: #f5f7fa;
  padding: 12px 16px;
  border-radius: 8px;
}

.recorder-input-section .el-form-item {
  margin-bottom: 0;
}

.recording-alert {
  margin-bottom: 0;
}

.recorder-actions-full {
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  background: #fff;
  min-height: 300px;
  max-height: 400px;
}

.recorder-actions-full .actions-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 16px;
  background: #f5f7fa;
  border-bottom: 1px solid #e4e7ed;
}

.recorder-actions-full .actions-title {
  font-weight: 600;
  color: #303133;
  font-size: 15px;
}

.recorder-actions-full .actions-body {
  flex: 1;
  overflow-y: auto;
  padding: 12px;
}

.recorder-actions-full .actions-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  min-height: 200px;
  color: #909399;
  gap: 4px;
}

.action-text {
  margin-left: 8px;
  font-size: 12px;
  color: #606266;
}

.actions-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.action-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px;
  background: #f9f9fb;
  border-radius: 6px;
  border-left: 3px solid #909399;
}

.action-item.click {
  border-left-color: #409eff;
}

.action-item.input {
  border-left-color: #67c23a;
}

.action-item.select {
  border-left-color: #e6a23c;
}

.action-item.hover {
  border-left-color: #9b59b6;
}

.action-item.navigate {
  border-left-color: #f56c6c;
}

.action-index {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: #409eff;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  flex-shrink: 0;
}

.action-content {
  flex: 1;
  min-width: 0;
}

.action-type {
  font-size: 12px;
  font-weight: 500;
  color: #606266;
  margin-bottom: 4px;
  display: flex;
  align-items: center;
}

.action-detail {
  display: flex;
  gap: 8px;
  font-size: 12px;
  color: #909399;
  overflow: hidden;
}

.action-selector {
  font-family: Consolas, Monaco, monospace;
  background: #fff;
  padding: 2px 6px;
  border-radius: 3px;
  border: 1px solid #e4e7ed;
  max-width: 300px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.action-value {
  color: #67c23a;
  font-family: Consolas, Monaco, monospace;
}

.recorder-result {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.result-details {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.result-details p {
  margin: 0;
  font-size: 13px;
}

.result-details code {
  background: #f0f2f5;
  padding: 2px 6px;
  border-radius: 3px;
  font-size: 12px;
}

.result-actions {
  display: flex;
  gap: 8px;
  margin-top: 8px;
}

.script-preview {
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  overflow: hidden;
}

.preview-header-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background: #f5f7fa;
  border-bottom: 1px solid #e4e7ed;
  font-weight: 500;
}

.script-preview pre {
  margin: 0;
  padding: 12px;
  background: #1e1e1e;
  color: #d4d4d4;
  font-family: Consolas, Monaco, monospace;
  font-size: 13px;
  line-height: 1.6;
  overflow-x: auto;
  max-height: 400px;
  overflow-y: auto;
}

.script-preview pre.script-preview-collapsed {
  max-height: 150px;
}

/* ===== 验证码输入对话框样式 ===== */
.captcha-input-dialog {
  padding: 10px 0;
}

.captcha-input-dialog .el-form-item {
  margin-bottom: 16px;
}

.captcha-input-tip {
  background: #f4f4f5;
  border-radius: 6px;
  padding: 12px 16px;
  margin-top: 16px;
}

.captcha-input-tip p {
  margin: 0 0 8px 0;
  font-weight: 500;
  color: #606266;
}

.captcha-input-tip ul {
  margin: 0;
  padding-left: 20px;
  color: #909399;
  font-size: 13px;
  line-height: 1.8;
}

.captcha-input-tip li {
  list-style-type: disc;
}
</style>
