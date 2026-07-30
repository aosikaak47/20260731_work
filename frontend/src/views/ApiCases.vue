<template>
  <div class="api-cases">
    <div class="page-header">
      <div class="header-left">
        <div class="header-icon">
          <el-icon :size="22"><component :is="icons.Connection" /></el-icon>
        </div>
        <div class="header-text">
          <h2>接口用例管理</h2>
          <p class="page-desc">创建和管理接口测试用例，支持调试和断言</p>
        </div>
      </div>
      <div class="header-right">
        <el-select
          v-model="currentProjectId"
          placeholder="请选择项目"
          class="project-select"
          @change="handleProjectChange"
        >
          <el-option
            v-for="proj in projects"
            :key="proj.id"
            :label="proj.name"
            :value="proj.id"
          />
        </el-select>
      </div>
    </div>
    
    <el-card class="swagger-import-card">
      <template #header>
        <div class="card-header">
          <span class="card-title">Swagger/OpenAPI 文档导入</span>
          <el-button size="small" text @click="showSwaggerSection = !showSwaggerSection">
            {{ showSwaggerSection ? '收起' : '展开' }}
            <el-icon><component :is="showSwaggerSection ? icons.ArrowUp : icons.ArrowDown" /></el-icon>
          </el-button>
        </div>
      </template>
      <div v-show="showSwaggerSection" class="swagger-import-section">
        <div class="swagger-tabs">
          <el-radio-group v-model="swaggerInputType" size="small">
            <el-radio label="url">URL地址</el-radio>
            <el-radio label="content">粘贴内容</el-radio>
            <el-radio label="file">上传文件</el-radio>
          </el-radio-group>
        </div>
        
        <div v-if="swaggerInputType === 'url'" class="swagger-url">
          <el-input 
            v-model="swaggerUrl" 
            placeholder="输入Swagger/OpenAPI文档URL，如 http://localhost:8000/openapi.json"
          >
            <template #prepend>
              <el-icon><component :is="icons.Link" /></el-icon>
            </template>
          </el-input>
          <div class="swagger-url-tips">
            <el-tag v-for="example in swaggerUrlExamples" :key="example" size="small" @click="swaggerUrl = example" class="url-example">
              {{ example }}
            </el-tag>
          </div>
        </div>
        
        <div v-if="swaggerInputType === 'content'" class="swagger-content">
          <el-input 
            v-model="swaggerContent" 
            type="textarea" 
            :rows="4"
            placeholder="粘贴Swagger/OpenAPI JSON文档内容"
          />
        </div>
        
        <div v-if="swaggerInputType === 'file'" class="swagger-file">
          <div class="swagger-upload-area" @click="triggerSwaggerUpload" @dragover.prevent @drop="handleSwaggerDrop">
            <el-icon :size="32" class="upload-icon"><component :is="icons.FolderOpened" /></el-icon>
            <p class="upload-title">点击或拖拽上传Swagger文件</p>
            <p class="upload-hint">支持 JSON/YAML 格式</p>
          </div>
          <input type="file" ref="swaggerFileInput" class="file-input" accept=".json,.yaml,.yml" @change="handleSwaggerFileSelect" />
          <div v-if="swaggerFileInfo" class="swagger-file-info">
            <el-icon :size="16" color="#67C23A"><component :is="icons.Document" /></el-icon>
            <span>{{ swaggerFileInfo.name }}</span>
            <el-icon :size="16" @click="clearSwaggerFile" class="clear-icon"><component :is="icons.Close" /></el-icon>
          </div>
        </div>
        
        <div class="swagger-actions">
          <el-button 
            type="success" 
            @click="handleSwaggerGenerate" 
            :loading="isSwaggerGenerating"
          >
            <el-icon v-if="!isSwaggerGenerating"><component :is="icons.DocumentAdd" /></el-icon>
            {{ isSwaggerGenerating ? '正在解析...' : '解析Swagger生成接口用例' }}
          </el-button>
        </div>
        
        <div v-if="swaggerParseResult" class="swagger-result">
          <div class="result-header">
            <el-icon color="#67C23A"><component :is="icons.SuccessFilled" /></el-icon>
            <span>解析成功！共发现 {{ swaggerParseResult.total_apis }} 个API接口，分布在 {{ swaggerParseResult.modules }} 个模块</span>
          </div>
          <div class="result-info">
            <span>文档标题: {{ swaggerParseResult.title }}</span>
            <span>版本: {{ swaggerParseResult.version }}</span>
            <span>Base URL: {{ swaggerParseResult.base_url || '-' }}</span>
          </div>

          <div class="import-config-panel">
            <div class="config-title">
              <el-icon color="#6366f1"><component :is="icons.Setting" /></el-icon>
              <span>导入配置</span>
            </div>
            <el-row :gutter="16" class="config-row">
              <el-col :span="8">
                <div class="config-item">
                  <label>所属项目</label>
                  <el-select v-model="importConfig.project_id" placeholder="选择项目" clearable size="default" style="width: 100%">
                    <el-option label="不指定项目" value="" />
                    <el-option v-for="proj in projects" :key="proj.id" :label="proj.name" :value="proj.id" />
                  </el-select>
                </div>
              </el-col>
              <el-col :span="8">
                <div class="config-item">
                  <label>所属模块</label>
                  <div class="module-input-wrapper">
                    <el-input v-model="importConfig.module" placeholder="输入模块名称" :disabled="importConfig.useApiModule" size="default" />
                    <el-checkbox v-model="importConfig.useApiModule" class="module-checkbox">使用接口原模块</el-checkbox>
                  </div>
                </div>
              </el-col>
              <el-col :span="8">
                <div class="config-item">
                  <label>测试环境</label>
                  <el-select v-model="importConfig.environment_id" placeholder="选择测试环境" clearable size="default" style="width: 100%">
                    <el-option label="不指定环境" value="" />
                    <el-option v-for="env in environments" :key="env.id" :label="env.name" :value="env.id" />
                  </el-select>
                </div>
              </el-col>
            </el-row>
          </div>

          <div v-if="discoveredApis.length" class="discovered-apis">
            <div class="discovered-header">
              <span class="discovered-title">发现的 API 接口 ({{ discoveredApis.length }})</span>
              <div class="discovered-actions">
                <el-button size="small" @click="toggleSelectAllDiscovered">
                  {{ allDiscoveredSelected ? '取消全选' : '全选' }}
                </el-button>
                <el-button size="small" type="primary" :disabled="selectedDiscoveredIds.length === 0" @click="importSelectedApis">
                  导入选中 ({{ selectedDiscoveredIds.length }})
                </el-button>
                <el-button size="small" type="success" :disabled="discoveredApis.length === 0" @click="importAllDiscoveredApis">
                  全部导入
                </el-button>
              </div>
            </div>
            <el-table
              :data="discoveredApis"
              stripe
              border
              size="small"
              max-height="360"
              @selection-change="handleDiscoveredSelectionChange"
              ref="discoveredTableRef"
            >
              <el-table-column type="selection" width="45" :selectable="isDiscoveredSelectable" />
              <el-table-column prop="name" label="接口名称" min-width="180" show-overflow-tooltip />
              <el-table-column prop="method" label="请求方式" width="100" align="center">
                <template #default="scope">
                  <span class="method-tag" :class="'method-' + scope.row.method.toLowerCase()">{{ scope.row.method }}</span>
                </template>
              </el-table-column>
              <el-table-column prop="url" label="请求路径" min-width="200" show-overflow-tooltip>
                <template #default="scope">
                  <code class="url-code">{{ scope.row.url }}</code>
                </template>
              </el-table-column>
              <el-table-column prop="module" label="模块" width="120">
                <template #default="scope">
                  <el-tag size="small">{{ scope.row.module }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column label="参数" width="90" align="center">
                <template #default="scope">
                  <span>{{ (scope.row.params || []).length }}</span>
                </template>
              </el-table-column>
              <el-table-column label="请求体" width="90" align="center">
                <template #default="scope">
                  <el-tag v-if="scope.row.has_body" type="warning" size="small">有</el-tag>
                  <span v-else>-</span>
                </template>
              </el-table-column>
              <el-table-column prop="is_sensitive" label="敏感" width="70" align="center">
                <template #default="scope">
                  <el-tag v-if="scope.row.is_sensitive" type="danger" size="small">是</el-tag>
                  <span v-else>-</span>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </div>
      </div>
    </el-card>

    <el-card>
      <template #header>
        <div class="card-header">
          <span class="card-title">接口用例列表</span>
          <el-button type="primary" @click="handleAdd">
            <el-icon><component :is="icons.Plus" /></el-icon>
            新建用例
          </el-button>
        </div>
      </template>
      
      <div class="filter-bar">
        <el-select v-model="filterEnvironment" placeholder="环境" class="filter-select">
          <el-option label="全部" value="" />
          <el-option v-for="env in environments" :key="env.id" :label="env.name" :value="env.id" />
        </el-select>
        <el-select v-model="filterMethod" placeholder="请求方式" clearable class="filter-select">
          <el-option label="全部" value="" />
          <el-option label="GET" value="GET" />
          <el-option label="POST" value="POST" />
          <el-option label="PUT" value="PUT" />
          <el-option label="DELETE" value="DELETE" />
        </el-select>
        <el-select v-model="filterStatus" placeholder="状态" clearable class="filter-select">
          <el-option label="全部" value="" />
          <el-option label="已启用" value="已启用" />
          <el-option label="已禁用" value="已禁用" />
        </el-select>
        <el-input 
          v-model="searchKeyword" 
          placeholder="搜索接口名称、地址、模块..." 
          class="search-input"
          @keyup.enter="loadCases"
        >
          <template #prefix>
            <el-icon><component :is="icons.Search" /></el-icon>
          </template>
        </el-input>
        <el-button type="primary" class="create-btn" @click="openCreateDialog">
          <el-icon><component :is="icons.Plus" /></el-icon>
          新建用例
        </el-button>
        <el-button class="batch-btn" @click="handleBatchDelete" :disabled="selectedCases.length === 0">
          <el-icon><component :is="icons.Delete" /></el-icon>
          批量删除
        </el-button>
      </div>
      
      <el-table :data="pagedCases" stripe border :row-style="{ height: '44px' }" @selection-change="handleSelectionChange">
        <el-table-column type="selection" width="45" />
        <el-table-column label="序号" width="60" align="center">
          <template #default="scope">
            <span class="index-badge">{{ (currentPage - 1) * pageSize + scope.$index + 1 }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="name" label="接口名称" min-width="180" sortable :show-overflow-tooltip="true" />
        <el-table-column prop="method" label="请求方式" width="100" align="center">
          <template #default="scope">
            <span class="method-tag" :class="'method-' + scope.row.method.toLowerCase()">{{ scope.row.method }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="url" label="请求地址" min-width="220" :show-overflow-tooltip="true">
          <template #default="scope">
            <code class="url-code">{{ scope.row.url }}</code>
          </template>
        </el-table-column>
        <el-table-column prop="module" label="所属模块" width="120" />
        <el-table-column label="所属项目" width="130">
          <template #default="scope">
            <el-tag v-if="getProjectName(scope.row.project_id)" type="warning" size="small" effect="plain">{{ getProjectName(scope.row.project_id) }}</el-tag>
            <span v-else class="empty-val">-</span>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="90" align="center">
          <template #default="scope">
            <el-tag :type="scope.row.status === '已启用' ? 'success' : 'info'" size="small" effect="plain">{{ scope.row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="160" sortable />
        <el-table-column label="操作" width="180" fixed="right" class-name="action-cell">
          <template #default="scope">
            <div class="action-btns">
              <el-button size="small" text @click="handleDebug(scope.row)">调试</el-button>
              <el-button size="small" text @click="handleEdit(scope.row)">编辑</el-button>
              <el-button size="small" text type="danger" @click="handleDelete(scope.row)">删除</el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>
      
      <el-pagination
        class="pagination"
        layout="total, prev, pager, next"
        :total="filteredCases.length"
        :page-size="pageSize"
        v-model:current-page="currentPage"
      />
    </el-card>

    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑接口用例' : '新建接口用例'" width="95%" top="2vh" :close-on-click-modal="false">
      <div class="edit-debug-layout">
        <!-- 左侧：编辑配置 -->
        <div class="edit-panel">
          <div class="panel-header">
            <span class="panel-title">接口配置</span>
          </div>
          <div class="panel-content">
            <el-form :model="caseForm" label-width="100px" class="edit-form">
              <el-row :gutter="12">
                <el-col :span="16">
                  <el-form-item label="接口名称" required>
                    <el-input v-model="caseForm.name" placeholder="请输入接口名称" />
                  </el-form-item>
                </el-col>
                <el-col :span="8">
                  <el-form-item label="请求方式">
                    <el-select v-model="caseForm.method" style="width: 100%">
                      <el-option label="GET" value="GET" />
                      <el-option label="POST" value="POST" />
                      <el-option label="PUT" value="PUT" />
                      <el-option label="DELETE" value="DELETE" />
                      <el-option label="PATCH" value="PATCH" />
                    </el-select>
                  </el-form-item>
                </el-col>
              </el-row>
              <el-form-item label="请求地址" required>
                <el-input v-model="caseForm.url" placeholder="如 /api/login" />
              </el-form-item>
              <el-row :gutter="12">
                <el-col :span="8">
                  <el-form-item label="所属模块">
                    <el-input v-model="caseForm.module" placeholder="模块" />
                  </el-form-item>
                </el-col>
                <el-col :span="8">
                  <el-form-item label="所属项目">
                    <el-select v-model="caseForm.project_id" placeholder="选择项目" style="width: 100%">
                      <el-option label="不指定" value="" />
                      <el-option v-for="proj in projects" :key="proj.id" :label="proj.name" :value="proj.id" />
                    </el-select>
                  </el-form-item>
                </el-col>
                <el-col :span="8">
                  <el-form-item label="测试环境">
                    <el-select v-model="caseForm.environment_id" placeholder="选择环境" clearable style="width: 100%">
                      <el-option label="不使用环境" value="" />
                      <el-option v-for="env in environments" :key="env.id" :label="env.name" :value="env.id" />
                    </el-select>
                  </el-form-item>
                </el-col>
              </el-row>

              <el-divider content-position="left">请求配置</el-divider>

              <el-form-item label="请求头">
                <div class="headers-container">
                  <div v-for="(header, index) in caseForm.headers" :key="index" class="header-row">
                    <el-input v-model="header.key" placeholder="Header名" class="header-input" />
                    <el-input v-model="header.value" placeholder="Header值" class="header-input" />
                    <el-button type="danger" size="small" @click="removeHeader(index)">
                      <el-icon><component :is="icons.Delete" /></el-icon>
                    </el-button>
                  </div>
                  <el-button type="primary" size="small" @click="addHeader">
                    <el-icon><component :is="icons.Plus" /></el-icon>
                    添加请求头
                  </el-button>
                </div>
              </el-form-item>

              <el-form-item label="URL参数">
                <div class="params-container">
                  <div v-for="(param, index) in caseForm.params" :key="index" class="param-row">
                    <el-input v-model="param.key" placeholder="参数名" class="param-input" />
                    <el-input v-model="param.value" placeholder="参数值" class="param-input" />
                    <el-button type="danger" size="small" @click="removeParam(index)">
                      <el-icon><component :is="icons.Delete" /></el-icon>
                    </el-button>
                  </div>
                  <el-button type="primary" size="small" @click="addParam">
                    <el-icon><component :is="icons.Plus" /></el-icon>
                    添加参数
                  </el-button>
                </div>
              </el-form-item>

              <el-row :gutter="12">
                <el-col :span="8">
                  <el-form-item label="请求体类型">
                    <el-select v-model="caseForm.body_type" style="width: 100%">
                      <el-option label="无" value="none" />
                      <el-option label="JSON" value="json" />
                      <el-option label="Form Data" value="form" />
                      <el-option label="Text" value="text" />
                    </el-select>
                  </el-form-item>
                </el-col>
                <el-col :span="8">
                  <el-form-item label="状态">
                    <el-radio-group v-model="caseForm.status">
                      <el-radio label="已启用" />
                      <el-radio label="已禁用" />
                    </el-radio-group>
                  </el-form-item>
                </el-col>
              </el-row>

              <el-form-item label="请求体">
                <el-input
                  v-model="caseForm.body"
                  type="textarea"
                  :rows="6"
                  placeholder='请输入请求体内容，如 {"username":"admin"}'
                  :disabled="caseForm.body_type === 'none'"
                />
              </el-form-item>

              <el-divider content-position="left">断言设置</el-divider>

              <el-form-item label="断言">
                <div class="assertions-container">
                  <div v-for="(assertion, index) in caseForm.assertions" :key="index" class="assertion-row">
                    <el-select v-model="assertion.type" class="assertion-select">
                      <el-option label="响应状态码" value="status_code" />
                      <el-option label="JSON路径" value="json_path" />
                      <el-option label="响应时间" value="response_time" />
                    </el-select>
                    <el-input v-model="assertion.field" placeholder="字段路径 如 data[0]" class="assertion-input-sm" v-if="assertion.type === 'json_path'" />
                    <el-select v-model="assertion.operator" class="assertion-op">
                      <el-option label="等于" value="==" />
                      <el-option label="不等于" value="!=" />
                      <el-option label="大于等于" value=">=" />
                      <el-option label="小于等于" value="<=" />
                      <el-option label="包含" value="contains" v-if="assertion.type === 'json_path'" />
                      <el-option label="不包含" value="not_contains" v-if="assertion.type === 'json_path'" />
                    </el-select>
                    <el-input v-model="assertion.expected" placeholder="期望值" class="assertion-input" />
                    <el-button type="danger" size="small" @click="removeAssertion(index)">
                      <el-icon><component :is="icons.Delete" /></el-icon>
                    </el-button>
                  </div>
                  <el-button type="primary" size="small" @click="addAssertion">
                    <el-icon><component :is="icons.Plus" /></el-icon>
                    添加断言
                  </el-button>
                </div>
              </el-form-item>
            </el-form>
          </div>
        </div>

        <!-- 右侧：调试结果 -->
        <div class="debug-panel">
          <div class="panel-header">
            <span class="panel-title">在线调试</span>
            <div class="debug-actions">
              <el-select v-model="debugEnvId" placeholder="调试环境" clearable size="small" style="width: 140px">
                <el-option label="使用用例环境" value="" />
                <el-option v-for="env in environments" :key="env.id" :label="env.name" :value="env.id" />
              </el-select>
              <el-button type="success" @click="runDebugFromForm" :loading="debugLoading">
                <el-icon><component :is="icons.Promotion" /></el-icon>
                发送调试
              </el-button>
            </div>
          </div>
          <div class="panel-content debug-content">
            <!-- 请求预览 -->
            <div class="request-preview">
              <div class="preview-line">
                <span class="method-tag method-post" :class="'method-' + caseForm.method.toLowerCase()">{{ caseForm.method }}</span>
                <span class="preview-url">{{ getFormFullUrl() }}</span>
                <el-tag v-if="debugResult" :type="debugResult.response?.status_code === 200 ? 'success' : 'danger'" size="small" effect="plain">
                  {{ debugResult.response?.status_code || '未发送' }}
                </el-tag>
                <span v-if="debugResult" class="preview-time">耗时: {{ debugResult.response?.time || 0 }}ms</span>
              </div>
            </div>

            <el-tabs v-model="debugActiveTab" class="debug-tabs">
              <el-tab-pane label="响应结果" name="response">
                <div v-if="debugResult" class="response-result">
                  <div class="response-stats">
                    <div class="stat-item">
                      <span class="stat-label">状态码</span>
                      <el-tag :type="debugResult.response?.status_code === 200 ? 'success' : 'danger'" size="small">
                        {{ debugResult.response?.status_code }}
                      </el-tag>
                    </div>
                    <div class="stat-item">
                      <span class="stat-label">耗时</span>
                      <span class="stat-value">{{ debugResult.response?.time || 0 }}ms</span>
                    </div>
                    <div class="stat-item" v-if="debugResult.response?.size">
                      <span class="stat-label">大小</span>
                      <span class="stat-value">{{ formatSize(debugResult.response?.size) }}</span>
                    </div>
                  </div>
                  <el-divider content-position="left">响应体</el-divider>
                  <pre class="code-block">{{ formatResponse(debugResult.response?.body) }}</pre>
                </div>
                <div v-else class="empty-response">
                  <el-icon :size="48" color="#909399"><component :is="icons.Document" /></el-icon>
                  <p>点击"发送调试"查看响应结果</p>
                </div>
              </el-tab-pane>

              <el-tab-pane label="响应头" name="headers">
                <div v-if="debugResult && responseHeadersList.length > 0" class="headers-result">
                  <el-table :data="responseHeadersList" border size="small" max-height="300">
                    <el-table-column prop="key" label="Key" width="180" />
                    <el-table-column prop="value" label="Value" />
                  </el-table>
                </div>
                <div v-else class="empty-response">
                  <el-icon :size="48" color="#909399"><component :is="icons.Document" /></el-icon>
                  <p>暂无响应头数据</p>
                </div>
              </el-tab-pane>

              <el-tab-pane label="断言结果" name="assertions">
                <div v-if="debugResult && debugResult.assertions && debugResult.assertions.length > 0">
                  <div v-for="(item, index) in debugResult.assertions" :key="index" class="assertion-result">
                    <div class="assertion-header">
                      <el-icon :size="16" :color="item.passed ? '#67C23A' : '#F56C6C'">
                        <component :is="item.passed ? icons.Check : icons.Close" />
                      </el-icon>
                      <span>{{ getAssertionDesc(item.assertion) }}</span>
                      <el-tag :type="item.passed ? 'success' : 'danger'" size="small">
                        {{ item.passed ? '通过' : '失败' }}
                      </el-tag>
                    </div>
                    <div class="assertion-detail">
                      <span>期望值: {{ item.assertion.expected }}</span>
                      <span>实际值: {{ item.actual !== null && item.actual !== undefined ? item.actual : 'null' }}</span>
                    </div>
                  </div>
                  <div class="assertions-summary" :class="{ failed: !debugResult.all_passed }">
                    <el-icon :size="20" :color="debugResult.all_passed ? '#67C23A' : '#F56C6C'">
                      <component :is="debugResult.all_passed ? icons.CircleCheck : icons.CircleClose" />
                    </el-icon>
                    <span>{{ debugResult.all_passed ? '所有断言通过' : '部分断言失败' }}</span>
                  </div>
                </div>
                <div v-else class="empty-response">
                  <el-icon :size="48" color="#909399"><component :is="icons.Document" /></el-icon>
                  <p>暂无断言或未发送请求</p>
                </div>
              </el-tab-pane>
            </el-tabs>
          </div>
        </div>
      </div>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSave">保存用例</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, reactive, onMounted, watch } from 'vue'
import * as icons from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { useProjects } from '../composables/useProjects'

const { projects, currentProjectId, loadProjects } = useProjects()

const showSwaggerSection = ref(false)
const swaggerInputType = ref('url')
const swaggerUrl = ref('')
const swaggerContent = ref('')
const swaggerFileInfo = ref(null)
const swaggerFileInput = ref(null)
const isSwaggerGenerating = ref(false)
const swaggerParseResult = ref(null)
const discoveredApis = ref([])
const selectedDiscoveredIds = ref([])
const discoveredTableRef = ref(null)
const importingDiscovered = ref(false)

const importConfig = reactive({
  project_id: '',
  module: '',
  useApiModule: true,
  environment_id: ''
})

const allDiscoveredSelected = computed(() => {
  return discoveredApis.value.length > 0 && selectedDiscoveredIds.value.length === discoveredApis.value.length
})

const isDiscoveredSelectable = () => true
const swaggerUrlExamples = [
  'https://petstore.swagger.io/v2/swagger.json',
  '/api/v1/swagger.json'
]
const swaggerExample = {
  "openapi": "3.0.0",
  "info": { "title": "示例API", "version": "1.0" },
  "paths": {
    "/api/users": {
      "get": {
        "summary": "获取用户列表",
        "responses": { "200": { "description": "成功" } }
      }
    }
  }
}

const searchKeyword = ref('')
const filterEnvironment = ref('')
const filterMethod = ref('')
const filterStatus = ref('')
const currentPage = ref(1)
const pageSize = ref(10)

const apiCases = ref([])
const environments = ref([])

const dialogVisible = ref(false)
const isEdit = ref(false)
const editingCase = ref(null)
const selectedCases = ref([])

const debugLoading = ref(false)
const debugResult = ref(null)
const debugEnvId = ref('')
const debugActiveTab = ref('response')

const caseForm = reactive({
  name: '',
  method: 'GET',
  url: '',
  module: '',
  project_id: '',
  environment_id: '',
  headers: [],
  params: [],
  body: '',
  body_type: 'none',
  assertions: [],
  status: '已启用'
})

const filteredCases = computed(() => {
  let result = apiCases.value
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    result = result.filter(c => c.name.toLowerCase().includes(keyword) || (c.url && c.url.toLowerCase().includes(keyword)) || (c.module && c.module.toLowerCase().includes(keyword)))
  }
  if (filterEnvironment.value) {
    result = result.filter(c => c.environment_id === filterEnvironment.value)
  }
  if (filterMethod.value) {
    result = result.filter(c => c.method === filterMethod.value)
  }
  if (filterStatus.value) {
    result = result.filter(c => c.status === filterStatus.value)
  }
  return result
})

const pagedCases = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  return filteredCases.value.slice(start, start + pageSize.value)
})

const responseHeadersList = computed(() => {
  const headers = debugResult.value?.response?.headers || {}
  return Object.entries(headers).map(([key, value]) => ({ key, value }))
})

const loadCases = async () => {
  try {
    const params = new URLSearchParams()
    if (currentProjectId.value) {
      params.append('project_id', currentProjectId.value)
    }
    const response = await fetch(`/api/v1/api_cases${params.toString() ? '?' + params.toString() : ''}`)
    const data = await response.json()
    apiCases.value = data.cases || []
  } catch (error) {
    console.error('加载接口用例失败:', error)
  }
}

const handleProjectChange = () => {
  loadCases()
}

watch(currentProjectId, () => {
  loadCases()
})

const loadEnvironments = async () => {
  try {
    const response = await fetch('/api/v1/environments')
    const data = await response.json()
    environments.value = data.environments || []
  } catch (error) {
    console.error('加载环境列表失败:', error)
  }
}

const resetForm = () => {
  caseForm.name = ''
  caseForm.method = 'GET'
  caseForm.url = ''
  caseForm.module = ''
  caseForm.project_id = currentProjectId.value || ''
  caseForm.environment_id = ''
  caseForm.headers = []
  caseForm.params = []
  caseForm.body = ''
  caseForm.body_type = 'none'
  caseForm.assertions = []
  caseForm.status = '已启用'
}

const handleAdd = () => {
  isEdit.value = false
  editingCase.value = null
  resetForm()
  dialogVisible.value = true
}

const handleEdit = (row) => {
  isEdit.value = true
  editingCase.value = row
  caseForm.name = row.name
  caseForm.method = row.method
  caseForm.url = row.url
  caseForm.module = row.module
  caseForm.project_id = row.project_id || currentProjectId.value || ''
  caseForm.environment_id = row.environment_id
  caseForm.headers = row.headers ? JSON.parse(JSON.stringify(row.headers)) : []
  caseForm.params = row.params ? JSON.parse(JSON.stringify(row.params)) : []
  caseForm.body = row.body || ''
  caseForm.body_type = row.body_type || 'none'
  caseForm.assertions = row.assertions ? JSON.parse(JSON.stringify(row.assertions)) : []
  caseForm.status = row.status
  dialogVisible.value = true
}

const handleDebug = (row) => {
  isEdit.value = true
  editingCase.value = row
  caseForm.name = row.name
  caseForm.method = row.method
  caseForm.url = row.url
  caseForm.module = row.module
  caseForm.project_id = row.project_id || currentProjectId.value || ''
  caseForm.environment_id = row.environment_id
  caseForm.headers = row.headers ? JSON.parse(JSON.stringify(row.headers)) : []
  caseForm.params = row.params ? JSON.parse(JSON.stringify(row.params)) : []
  caseForm.body = row.body || ''
  caseForm.body_type = row.body_type || 'none'
  caseForm.assertions = row.assertions ? JSON.parse(JSON.stringify(row.assertions)) : []
  caseForm.status = row.status
  debugEnvId.value = row.environment_id || ''
  debugResult.value = null
  debugActiveTab.value = 'response'
  dialogVisible.value = true
}

const runDebugFromForm = async () => {
  debugLoading.value = true
  debugResult.value = null
  debugActiveTab.value = 'response'

  try {
    // 先保存当前表单数据到后端进行调试
    const payload = {
      name: caseForm.name,
      method: caseForm.method,
      url: caseForm.url,
      module: caseForm.module,
      project_id: caseForm.project_id,
      environment_id: caseForm.environment_id,
      headers: caseForm.headers,
      params: caseForm.params,
      body: caseForm.body,
      body_type: caseForm.body_type,
      assertions: caseForm.assertions,
      status: caseForm.status,
      debug_env_id: debugEnvId.value || caseForm.environment_id
    }

    const response = await fetch('/api/v1/api_cases/debug_online', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })

    const data = await response.json()
    if (data.success !== false) {
      debugResult.value = data
    } else {
      ElMessage.error(data.message || '调试失败')
    }
  } catch (error) {
    console.error('调试接口失败:', error)
    ElMessage.error('调试接口失败，请检查网络连接')
  } finally {
    debugLoading.value = false
  }
}

const handleDelete = async (row) => {
  if (!confirm(`确定要删除接口用例「${row.name}」吗？`)) return
  try {
    const response = await fetch(`/api/v1/api_cases/${row.id}`, {
      method: 'DELETE'
    })
    const data = await response.json()
    if (data.success) {
      alert(data.message)
      loadCases()
    }
  } catch (error) {
    console.error('删除接口用例失败:', error)
  }
}

const openCreateDialog = () => {
  handleAdd()
}

const handleSelectionChange = (selection) => {
  selectedCases.value = selection
}

const handleBatchDelete = async () => {
  if (selectedCases.value.length === 0) return
  if (!confirm(`确定要删除选中的 ${selectedCases.value.length} 个接口用例吗？`)) return
  try {
    for (const row of selectedCases.value) {
      await fetch(`/api/v1/api_cases/${row.id}`, { method: 'DELETE' })
    }
    ElMessage.success(`成功删除 ${selectedCases.value.length} 个用例`)
    selectedCases.value = []
    loadCases()
  } catch (error) {
    console.error('批量删除失败:', error)
    ElMessage.error('批量删除失败')
  }
}

const handleSave = async () => {
  if (!caseForm.name || !caseForm.url) {
    alert('接口名称和请求地址不能为空')
    return
  }
  
  try {
    const url = isEdit.value ? `/api/v1/api_cases/${editingCase.value.id}` : '/api/v1/api_cases'
    const method = isEdit.value ? 'PUT' : 'POST'
    
    const response = await fetch(url, {
      method: method,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(caseForm)
    })
    
    const data = await response.json()
    if (data.success) {
      alert(data.message)
      dialogVisible.value = false
      loadCases()
    } else {
      alert(data.message || '保存失败')
    }
  } catch (error) {
    console.error('保存接口用例失败:', error)
    alert('保存接口用例失败，请检查网络连接')
  }
}

const getFormFullUrl = () => {
  const envId = debugEnvId.value || caseForm.environment_id
  const env = environments.value.find(e => e.id === envId)
  if (!env) return caseForm.url || '请输入URL'
  return (env.base_url || '').replace(/\/+$/, '') + (caseForm.url || '')
}

const formatSize = (bytes) => {
  if (!bytes) return '0 B'
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / 1024 / 1024).toFixed(2) + ' MB'
}

const formatResponse = (body) => {
  if (!body) return ''
  if (typeof body === 'object') {
    return JSON.stringify(body, null, 2)
  }
  return body
}

const getAssertionDesc = (assertion) => {
  if (assertion.type === 'status_code') {
    return `响应状态码 ${assertion.operator} ${assertion.expected}`
  } else if (assertion.type === 'json_path') {
    return `JSON字段 ${assertion.field} ${assertion.operator} ${assertion.expected}`
  } else if (assertion.type === 'response_time') {
    return `响应时间 ${assertion.operator} ${assertion.expected}ms`
  }
  return ''
}

const addHeader = () => {
  caseForm.headers.push({ key: '', value: '' })
}

const removeHeader = (index) => {
  caseForm.headers.splice(index, 1)
}

const addParam = () => {
  caseForm.params.push({ key: '', value: '' })
}

const removeParam = (index) => {
  caseForm.params.splice(index, 1)
}

const addAssertion = () => {
  caseForm.assertions.push({ type: 'status_code', operator: '==', expected: 200 })
}

const removeAssertion = (index) => {
  caseForm.assertions.splice(index, 1)
}

const getProjectName = (projectId) => {
  if (!projectId) return ''
  const proj = projects.value.find(p => p.id === projectId)
  return proj ? proj.name : ''
}

const triggerSwaggerUpload = () => {
  swaggerFileInput.value?.click()
}

const handleSwaggerFileSelect = (e) => {
  const file = e.target.files[0]
  if (file) {
    swaggerFileInfo.value = { name: file.name, size: file.size }
    const reader = new FileReader()
    reader.onload = (event) => {
      swaggerContent.value = event.target.result
    }
    reader.readAsText(file)
  }
}

const handleSwaggerDrop = (e) => {
  const file = e.dataTransfer.files[0]
  if (file) {
    swaggerFileInfo.value = { name: file.name, size: file.size }
    const reader = new FileReader()
    reader.onload = (event) => {
      swaggerContent.value = event.target.result
    }
    reader.readAsText(file)
  }
}

const clearSwaggerFile = () => {
  swaggerFileInfo.value = null
  swaggerContent.value = ''
}

const loadSwaggerExample = () => {
  swaggerContent.value = JSON.stringify(swaggerExample, null, 2)
}

const handleSwaggerGenerate = async () => {
  if (swaggerInputType.value === 'url' && !swaggerUrl.value.trim()) {
    ElMessage.warning('请输入 Swagger/OpenAPI 文档的 URL 地址')
    return
  }
  if (swaggerInputType.value === 'content' && !swaggerContent.value.trim()) {
    ElMessage.warning('请粘贴 Swagger/OpenAPI 文档内容')
    return
  }
  if (swaggerInputType.value === 'file' && !swaggerContent.value.trim()) {
    ElMessage.warning('请先上传 Swagger 文件')
    return
  }
  
  isSwaggerGenerating.value = true
  swaggerParseResult.value = null
  
  try {
    const body = {
      swagger_url: swaggerInputType.value === 'url' ? swaggerUrl.value.trim() : '',
      swagger_content: swaggerInputType.value !== 'url' ? swaggerContent.value.trim() : ''
    }
    
    const response = await fetch('/api/v1/swagger/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body)
    })
    
    const data = await response.json()
    
    if (response.ok && data.success) {
      swaggerParseResult.value = data.info
      discoveredApis.value = data.api_cases || []
      selectedDiscoveredIds.value = []
      importConfig.project_id = currentProjectId.value || ''
      importConfig.module = ''
      importConfig.useApiModule = true
      importConfig.environment_id = ''
      const totalCases = (data.info.case_ids || []).length
      ElMessage.success(`Swagger 解析成功！共发现 ${data.info.total_apis} 个 API 接口，已生成 ${totalCases} 个测试用例`)
    } else {
      discoveredApis.value = []
      ElMessage.error(data.detail || data.message || '解析失败，请确认 URL 指向的是有效的 Swagger/OpenAPI 文档')
    }
  } catch (error) {
    console.error('Swagger解析失败:', error)
    ElMessage.error('解析失败，请检查网络连接或后端服务是否正常')
  } finally {
    isSwaggerGenerating.value = false
  }
}

const handleDiscoveredSelectionChange = (selection) => {
  selectedDiscoveredIds.value = selection.map(item => item.id)
}

const toggleSelectAllDiscovered = () => {
  if (!discoveredTableRef.value) return
  if (allDiscoveredSelected.value) {
    discoveredTableRef.value.clearSelection()
  } else {
    discoveredApis.value.forEach(row => {
      discoveredTableRef.value.toggleRowSelection(row, true)
    })
  }
}

const importSelectedApis = async () => {
  if (selectedDiscoveredIds.value.length === 0) {
    ElMessage.warning('请先勾选要导入的 API 接口')
    return
  }
  const selected = discoveredApis.value.filter(api => selectedDiscoveredIds.value.includes(api.id))
  await _importApis(selected)
}

const importAllDiscoveredApis = async () => {
  if (!discoveredApis.value.length) return
  await _importApis(discoveredApis.value)
}

const _importApis = async (apis) => {
  if (!apis.length) {
    ElMessage.warning('没有可导入的接口')
    return
  }
  importingDiscovered.value = true
  try {
    const moduleVal = importConfig.useApiModule ? '' : importConfig.module
    const response = await fetch('/api/v1/api_cases/import_from_swagger', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        apis,
        project_id: importConfig.project_id || currentProjectId.value || '',
        module: moduleVal,
        environment_id: importConfig.environment_id || ''
      })
    })
    const data = await response.json()
    if (data.success) {
      ElMessage.success(`${data.message || `成功导入 ${data.imported} 条接口用例`}`)
      loadCases()
      selectedDiscoveredIds.value = []
      if (discoveredTableRef.value) discoveredTableRef.value.clearSelection()
    } else {
      ElMessage.error(data.message || '导入失败')
    }
  } catch (error) {
    console.error('导入接口失败:', error)
    ElMessage.error('导入失败，请检查网络连接或后端服务是否正常')
  } finally {
    importingDiscovered.value = false
  }
}

const importSwaggerCasesToLibrary = async () => {
  if (!swaggerParseResult.value?.case_ids?.length) {
    ElMessage.warning('没有可导入的用例')
    return
  }
  
  try {
    const response = await fetch('/api/v1/case_library/import_from_swagger', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        case_ids: swaggerParseResult.value.case_ids,
        project_id: currentProjectId.value || ''
      })
    })
    
    const data = await response.json()
    if (data.success) {
      ElMessage.success(`成功导入 ${data.count} 条用例到用例库`)
      swaggerParseResult.value = null
      loadCases()
    } else {
      ElMessage.error(data.message || '导入失败')
    }
  } catch (error) {
    console.error('导入用例失败:', error)
    ElMessage.error('导入失败，请检查网络连接')
  }
}

onMounted(async () => {
  await loadProjects(true)
  loadCases()
  loadEnvironments()
})
</script>

<style scoped>
.api-cases {
  max-width: 100%;
}

.page-header {
  margin-bottom: 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 16px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.header-icon {
  width: 48px;
  height: 48px;
  background: linear-gradient(135deg, var(--theme-primary) 0%, var(--theme-primary-dark) 100%);
  border-radius: var(--radius-lg);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  flex-shrink: 0;
}

.header-text h2 {
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  margin: 0 0 4px 0;
  line-height: 1.4;
}

.page-desc {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  margin: 0;
  line-height: 1.5;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.project-select {
  width: 200px;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.card-title {
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-medium);
}

.swagger-import-card {
  margin-bottom: 24px;
}

.swagger-import-section {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.swagger-tabs {
  display: flex;
  justify-content: center;
}

.swagger-url,
.swagger-content,
.swagger-file {
  width: 100%;
}

.swagger-url-tips {
  display: flex;
  gap: 8px;
  margin-top: 8px;
  flex-wrap: wrap;
}

.url-example {
  cursor: pointer;
}

.swagger-actions {
  display: flex;
  justify-content: center;
}

.swagger-upload-area {
  border: 2px dashed var(--color-border);
  border-radius: var(--radius-lg);
  padding: 32px;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s;
}

.swagger-upload-area:hover {
  border-color: var(--theme-primary);
  background-color: var(--theme-primary-light);
}

.upload-icon {
  color: var(--theme-primary);
}

.upload-title {
  font-size: var(--font-size-sm);
  color: var(--color-text-primary);
  margin: 8px 0 4px;
  font-weight: var(--font-weight-medium);
}

.upload-hint {
  font-size: var(--font-size-xs);
  color: var(--color-text-tertiary);
}

.file-input {
  display: none;
}

.swagger-file-info {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 8px;
  padding: 8px 12px;
  background-color: var(--color-divider);
  border-radius: var(--radius-md);
}

.clear-icon {
  cursor: pointer;
}

.swagger-result {
  background-color: #f0fdf4;
  border: 1px solid #86efac;
  border-radius: var(--radius-lg);
  padding: 16px;
}

.result-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
  color: #166534;
  font-weight: var(--font-weight-medium);
}

.result-info {
  display: flex;
  gap: 24px;
  flex-wrap: wrap;
  font-size: var(--font-size-sm);
  color: var(--color-text-primary);
  margin-bottom: 12px;
}

.import-config-panel {
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: 16px;
  margin-bottom: 16px;
}

.config-title {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px dashed var(--color-border);
}

.config-row {
  margin-bottom: 8px;
}

.config-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.config-item label {
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
  font-weight: var(--font-weight-medium);
}

.module-input-wrapper {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.module-checkbox {
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
}

.swagger-result-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 12px;
}

.discovered-apis {
  margin-top: 12px;
  border-top: 1px dashed #86efac;
  padding-top: 12px;
}

.discovered-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
  flex-wrap: wrap;
  gap: 8px;
}

.discovered-title {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-semibold);
  color: #166534;
}

.discovered-actions {
  display: flex;
  gap: 8px;
}

.url-code {
  background-color: var(--color-divider);
  padding: 1px 6px;
  border-radius: var(--radius-sm);
  font-size: var(--font-size-xs);
  color: var(--color-text-primary);
  font-family: Menlo, Monaco, Consolas, monospace;
}

.filter-bar {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
  align-items: center;
  flex-wrap: wrap;
}

.filter-select {
  width: 140px;
}

.search-input {
  width: 240px;
}

.create-btn {
  height: 36px;
}

.batch-btn {
  height: 36px;
}

.pagination {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}

.method-tag {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
  line-height: 1.5;
  text-align: center;
  min-width: 52px;
  border: 1px solid transparent;
}

.method-tag.method-get {
  background-color: #E7F7EC;
  color: #00A870;
  border-color: #B8E4CA;
}

.method-tag.method-post {
  background-color: #EBF3FF;
  color: #3366FF;
  border-color: #C2D4FF;
}

.method-tag.method-put {
  background-color: #FFF4E5;
  color: #D46B08;
  border-color: #FFD8A8;
}

.method-tag.method-delete {
  background-color: #FFECECEC;
  color: #E54D42;
  border-color: #FFC9C5;
}

.url-code {
  font-family: Menlo, Monaco, Consolas, monospace;
  font-size: 12px;
  color: var(--color-text-secondary);
  background: var(--color-bg-page);
  padding: 2px 6px;
  border-radius: 4px;
  max-width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.empty-val {
  color: var(--color-text-placeholder);
}

.headers-container,
.params-container,
.assertions-container {
  max-height: 200px;
  overflow-y: auto;
}

.header-row,
.param-row,
.assertion-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.header-input,
.param-input {
  width: 150px;
}

.assertion-select {
  width: 120px;
}

.assertion-input {
  width: 100px;
}

.debug-container {
  height: 500px;
}

.debug-request {
  padding: 12px;
}

.request-line {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 16px;
}

.debug-method {
  width: 120px;
}

.debug-tag {
  width: 60px;
  text-align: center;
}

.debug-url {
  flex: 1;
  font-family: monospace;
  color: var(--theme-primary);
}

.request-section,
.response-section {
  margin-bottom: 16px;
}

.request-section h4,
.response-section h4 {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-semibold);
  margin-bottom: 8px;
  color: var(--color-text-primary);
}

.code-block {
  background: var(--color-bg-hover);
  padding: 12px;
  border-radius: var(--radius-md);
  overflow-x: auto;
  font-family: monospace;
  font-size: var(--font-size-xs);
  color: var(--color-text-primary);
}

.debug-response,
.debug-assertions {
  padding: 12px;
  height: 400px;
  overflow-y: auto;
}

.response-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 16px;
}

.response-time {
  color: var(--color-text-tertiary);
  font-size: var(--font-size-sm);
}

.empty-response,
.empty-assertions {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: var(--color-text-tertiary);
}

.empty-response p,
.empty-assertions p {
  margin-top: 12px;
  font-size: var(--font-size-sm);
}

.assertion-result {
  background: var(--color-bg-hover);
  padding: 12px;
  border-radius: var(--radius-md);
  margin-bottom: 12px;
}

.assertion-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 8px;
}

.assertion-detail {
  display: flex;
  gap: 20px;
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

.assertions-summary {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  margin-top: 20px;
  padding: 16px;
  background: #f0fdf4;
  border-radius: var(--radius-md);
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-semibold);
  color: #10b981;
}

.assertions-summary.failed {
  background: #fef2f2;
  color: #ef4444;
}

.index-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 22px;
  height: 22px;
  background: var(--color-bg-hover);
  border-radius: var(--radius-sm);
  font-size: 12px;
  color: var(--color-text-secondary);
  font-weight: var(--font-weight-medium);
}

/* 左右分栏布局 */
.edit-debug-layout {
  display: flex !important;
  flex-direction: row !important;
  gap: 16px;
  height: 75vh;
  min-height: 500px;
  width: 100%;
  box-sizing: border-box;
}

.edit-panel,
.debug-panel {
  display: flex;
  flex-direction: column;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  overflow: hidden;
  min-width: 0;
  flex-shrink: 1;
}

.edit-panel {
  flex: 1.2 1 0%;
}

.debug-panel {
  flex: 1 1 0%;
}

.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  background: var(--color-bg-hover);
  border-bottom: 1px solid var(--color-border);
  flex-shrink: 0;
}

.panel-title {
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
}

.panel-content {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
}

.edit-form {
  padding-right: 8px;
}

/* 右侧调试面板 */
.debug-content {
  display: flex;
  flex-direction: column;
  padding: 12px;
}

.request-preview {
  background: var(--color-bg-hover);
  border-radius: var(--radius-md);
  padding: 10px 12px;
  margin-bottom: 12px;
  flex-shrink: 0;
}

.preview-line {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.preview-url {
  flex: 1;
  font-family: monospace;
  font-size: 13px;
  color: var(--theme-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  min-width: 100px;
}

.preview-time {
  font-size: 12px;
  color: var(--color-text-tertiary);
}

.debug-tabs {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.debug-tabs :deep(.el-tabs__content) {
  flex: 1;
  overflow: auto;
}

.debug-tabs :deep(.el-tab-pane) {
  height: 100%;
}

.response-stats {
  display: flex;
  gap: 16px;
  margin-bottom: 12px;
  flex-wrap: wrap;
}

.stat-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 8px 12px;
  background: var(--color-bg-hover);
  border-radius: var(--radius-md);
  min-width: 80px;
}

.stat-label {
  font-size: 12px;
  color: var(--color-text-tertiary);
}

.stat-value {
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
}

.headers-result {
  max-height: 300px;
}

.assertion-op {
  width: 100px;
}

.assertion-input-sm {
  width: 120px;
}

.debug-actions {
  display: flex;
  gap: 8px;
  align-items: center;
}

@media (max-width: 1200px) {
  .edit-debug-layout {
    flex-direction: column;
    height: auto;
    min-height: auto;
  }

  .edit-panel,
  .debug-panel {
    min-height: 400px;
  }
}</style>