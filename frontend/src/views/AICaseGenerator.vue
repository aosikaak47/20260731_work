<template>
  <div class="ai-case-generator">
    <div class="page-header">
      <div class="header-left">
        <div class="logo-section">
          <el-icon :size="32" class="logo-icon"><component :is="icons.Sunny" /></el-icon>
          <div>
            <h1>AI智能测试自动化平台</h1>
            <p class="subtitle">上传系统截图/需求文档 → 自动生成功能点·测试用例·测试边界·思维导图</p>
          </div>
        </div>
      </div>
    </div>
    
    <div class="main-container">
      <div class="left-panel">
        <div class="upload-section">
          <div class="upload-area" @click="triggerUpload" @dragover.prevent @drop="handleDrop">
            <el-icon :size="48" class="upload-icon"><component :is="icons.Upload" /></el-icon>
            <p class="upload-title">拖拽文件到此处 或点击选择</p>
            <p class="upload-hint">支持：系统截图(PNG/JPG/WEBP)、需求文档(TXT/MD/PDF/DOCX)</p>
          </div>
          <input type="file" ref="fileInput" class="file-input" @change="handleFileSelect" multiple />
          <div class="upload-tip">文件最大 25MB，图片最大 15MB</div>
          
          <div v-if="uploadedFiles.length > 0" class="uploaded-files">
            <div class="files-header">
              <span class="files-title">已上传文件</span>
              <el-button size="small" text @click="clearUploadedFiles">清空</el-button>
            </div>
            <div v-for="(file, index) in uploadedFiles" :key="index" class="file-item">
              <div class="file-icon">
                <el-icon v-if="isImage(file)" :size="20" color="#409EFF"><component :is="icons.PictureFilled" /></el-icon>
                <el-icon v-else-if="isDoc(file)" :size="20" color="#67C23A"><component :is="icons.Document" /></el-icon>
                <el-icon v-else :size="20" color="#909399"><component :is="icons.Document" /></el-icon>
              </div>
              <div class="file-info">
                <span class="file-name">{{ file.name }}</span>
                <span class="file-size">{{ formatFileSize(file.size) }}</span>
              </div>
              <div class="file-status">
                <span class="success-badge">
                  <el-icon :size="14" color="#67C23A"><component :is="icons.Check" /></el-icon>
                  上传成功
                </span>
              </div>
              <el-button size="small" text type="danger" @click="removeFile(index)">
                <el-icon :size="16"><component :is="icons.Delete" /></el-icon>
              </el-button>
            </div>
          </div>
        </div>
        
        <div class="doc-type-section">
          <span class="section-label">上传的文档视为：</span>
          <el-radio-group v-model="docType">
            <el-radio label="auto">自动识别</el-radio>
            <el-radio label="requirement">需求文档</el-radio>
            <el-radio label="api">接口文档</el-radio>
          </el-radio-group>
          <div v-if="docType === 'api'" class="api-tip">
            <span class="tip-icon">💡</span>
            接口文档会自动填入下方「接口文档」框并产出接口用例
          </div>
          <div v-if="docType === 'auto'" class="auto-tip">
            <span class="tip-icon">💡</span>
            自动识别会按 OpenAPI/Swagger 特征判断；自动识别会按 OpenAPI/Swagger 特征判断
          </div>
        </div>
        
        <div class="template-section">
          <span class="section-label">常见场景模板</span>
          <el-select v-model="selectedTemplate" placeholder="选择场景模板，注入测试关注点...">
            <el-option label="用户登录认证" value="login" />
            <el-option label="在线支付流程" value="payment" />
            <el-option label="数据查询筛选" value="query" />
            <el-option label="文件上传下载" value="file" />
            <el-option label="权限管理" value="permission" />
            <el-option label="表单验证" value="form" />
          </el-select>
          <p class="template-hint">选中后把该场景的测试关注点追加到下方需求框</p>
        </div>
        
        <div class="input-validation-section">
          <div class="section-header">
            <span class="section-label">输入分层校验</span>
            <el-tag size="small" :type="activeLayerCount >= 1 ? 'success' : 'danger'">
              已激活 {{ activeLayerCount }}/3 层
            </el-tag>
          </div>
          <div class="layer-badges">
            <div class="layer-badge" :class="{ active: inputLayers.A, empty: !inputLayers.A }">
              <span class="layer-letter">A</span>
              <span class="layer-name">需求文档</span>
              <span class="layer-status">{{ inputLayers.A ? '✓ 已提供' : '○ 未提供' }}</span>
            </div>
            <div class="layer-badge" :class="{ active: inputLayers.B, empty: !inputLayers.B }">
              <span class="layer-letter">B</span>
              <span class="layer-name">系统截图</span>
              <span class="layer-status">{{ inputLayers.B ? '✓ 已提供' : '○ 未提供' }}</span>
            </div>
            <div class="layer-badge" :class="{ active: inputLayers.C, empty: !inputLayers.C }">
              <span class="layer-letter">C</span>
              <span class="layer-name">文字描述</span>
              <span class="layer-status">{{ inputLayers.C ? '✓ 已提供' : '○ 未提供' }}</span>
            </div>
          </div>
          <div class="layer-tip">
            <el-icon :size="14"><component :is="icons.InfoFilled" /></el-icon>
            <span>三层任意提供一份即可启动生成，三份都提供则融合三份信息</span>
          </div>
        </div>

        <div class="description-section">
          <div class="section-header">
            <span class="section-label">文字描述 / 补充需求（分层C）</span>
          </div>
          <el-input
            v-model="requirementText"
            type="textarea"
            :rows="6"
            placeholder="粘贴需求文字描述、业务规则、页面交互细节等；上传的 TXT/MD/PDF/DOCX 文本文会自动填充。"
          />
          <div class="source-tags" v-if="uploadedFiles.length > 0">
            <span class="source-label">已识别素材来源：</span>
            <el-tag v-for="file in uploadedFiles" :key="file.name" size="small" type="info" class="source-tag">
              {{ isImage(file) ? '📷 截图' : '📄 文档' }} · {{ file.name }}
            </el-tag>
          </div>
        </div>
        
        <div class="action-section">
          <div class="generate-progress" v-if="isGenerating">
            <el-steps :active="generateStep" :process-status="'process'" align-center>
              <el-step title="校验输入" :icon="icons.Document" />
              <el-step title="信息融合拆解" :icon="icons.DataAnalysis" />
              <el-step title="场景分类" :icon="icons.Grid" />
              <el-step title="生成用例" :icon="icons.MagicStick" />
              <el-step title="自检报告" :icon="icons.CircleCheck" />
            </el-steps>
          </div>
          <el-button type="primary" @click="handleGenerate" :loading="isGenerating" class="generate-btn">
            <el-icon><component :is="icons.MagicStick" /></el-icon>
            一键生成测试用例
          </el-button>
          <p class="action-hint">根据上传的文档和需求描述，AI自动生成标准化测试用例（含自检报告、统计总结）</p>
        </div>
        
        <div class="swagger-section">
          <div class="section-header">
            <span class="section-label">Swagger文档导入</span>
            <el-tag size="small" type="warning">新增</el-tag>
          </div>
          <div class="swagger-tabs">
            <el-radio-group v-model="swaggerInputType">
              <el-radio label="url">URL地址</el-radio>
              <el-radio label="content">粘贴内容</el-radio>
              <el-radio label="file">上传文件</el-radio>
            </el-radio-group>
          </div>
          
          <div v-if="swaggerInputType === 'url'" class="swagger-url">
            <el-input 
              v-model="swaggerUrl" 
              placeholder="输入Swagger/OpenAPI文档URL，如 http://localhost:8000/openapi.json"
              :class="{ 'swagger-url-invalid': !swaggerUrlValid }"
            >
              <template #prepend>
                <el-icon><component :is="icons.Link" /></el-icon>
              </template>
            </el-input>
            <div v-if="!swaggerUrlValid && swaggerUrl" class="swagger-url-error">
              <el-icon :size="14" color="#f56c6c"><component :is="icons.Warning" /></el-icon>
              <span>URL 格式不正确，请输入有效的 http:// 或 https:// 协议地址</span>
            </div>
            <div class="swagger-url-tips">
              <el-tag v-for="example in swaggerUrlExamples" :key="example" size="small" @click="swaggerUrl = example" class="url-example">
                {{ example }}
              </el-tag>
            </div>
            <div class="swagger-url-hint">
              <el-icon :size="14" color="#909399"><component :is="icons.InfoFilled" /></el-icon>
              <span>支持 http:// 或 https:// 开头的完整 URL，或以 / 开头的相对路径</span>
            </div>
          </div>
          
          <div v-if="swaggerInputType === 'content'" class="swagger-content">
            <el-input 
              v-model="swaggerContent" 
              type="textarea" 
              :rows="6"
              placeholder="粘贴Swagger/OpenAPI JSON文档内容"
            />
            <el-button size="small" text @click="loadSwaggerExample">加载示例</el-button>
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
          
          <el-button 
            type="success" 
            @click="handleSwaggerGenerate" 
            :loading="isSwaggerGenerating"
            class="swagger-generate-btn"
          >
            <el-icon v-if="!isSwaggerGenerating"><component :is="icons.DocumentAdd" /></el-icon>
            {{ isSwaggerGenerating ? '正在解析 Swagger 文档...' : '解析Swagger生成接口用例' }}
          </el-button>
          <div v-if="isSwaggerGenerating" class="swagger-loading-tip">
            <el-icon class="is-loading"><component :is="icons.Loading" /></el-icon>
            <span>正在从后端获取并解析 Swagger 文档，这可能需要几秒钟...</span>
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
          </div>
        </div>
      </div>
      
      <div class="right-panel">
        <div class="project-header">
          <div class="project-info">
            <h2>{{ projectTitle }}</h2>
            <span class="auto-save">已自动保存 {{ lastSaveTime }}</span>
          </div>
          <div class="header-actions">
            <el-button @click="handleAddAllToLibrary" type="success" :icon="icons.ArrowRight" :disabled="!isGenerated || testCases.length === 0">
              全部导入用例库
            </el-button>
            <el-button @click="handleAddSelectedToLibrary" type="primary" :icon="icons.Check" :disabled="selectedCases.length === 0">
              选中导入用例库 ({{ selectedCases.length }})
            </el-button>
            <el-button @click="toggleEditMode" :type="editMode ? 'primary' : 'default'" :icon="editMode ? icons.View : icons.Edit">
              {{ editMode ? '预览模式' : '编辑模式' }}
            </el-button>
            <el-select v-model="exportScope" placeholder="导出范围" class="export-scope">
              <el-option label="全部" value="all" />
              <el-option label="仅选中" value="selected" />
            </el-select>
          </div>
        </div>
        
        <div class="export-buttons">
          <el-button @click="exportFile('markdown')" :icon="icons.Tickets" type="default" plain>Markdown</el-button>
          <el-button @click="exportFile('json')" :icon="icons.Document" type="default" plain>JSON</el-button>
          <el-button @click="exportFile('csv')" :icon="icons.List" type="default" plain>用例CSV</el-button>
          <el-button @click="exportFile('excel')" :icon="icons.Grid" type="default" plain>Excel</el-button>
          <el-button @click="exportFile('png')" :icon="icons.PictureFilled" type="default" plain>导图PNG</el-button>
          <el-button @click="exportFile('html')" :icon="icons.Document" type="default" plain>HTML报告</el-button>
          <el-button @click="exportFile('data_csv')" :icon="icons.Download" type="default" plain>数据CSV</el-button>
          <el-button @click="exportFile('sql')" :icon="icons.DataAnalysis" type="default" plain>造数SQL</el-button>
          <el-button @click="exportFile('script')" :icon="icons.Operation" type="default" plain>造数脚本</el-button>
          <el-button @click="exportFile('module_sql')" :icon="icons.Folder" type="default" plain>建表+造数SQL</el-button>
          <el-button @click="exportFile('module_script')" :icon="icons.FolderOpened" type="default" plain>建表+造数脚本</el-button>
          <el-button @click="exportFile('module_analysis')" :icon="icons.DataAnalysis" type="default" plain>按模块拆分SQL</el-button>
          
          <el-divider direction="vertical" class="divider" />
          
          <el-button @click="exportFile('curl')" :icon="icons.Link" type="default" plain>接口cURL</el-button>
          <el-button @click="exportFile('postman')" :icon="icons.Setting" type="default" plain>Postman</el-button>
          <el-button @click="exportFile('jmeter')" :icon="icons.Odometer" type="default" plain>JMeter</el-button>
          <el-button @click="exportFile('coverage_csv')" :icon="icons.Histogram" type="default" plain>覆盖度CSV</el-button>
          <el-button @click="exportFile('trace_csv')" :icon="icons.Clock" type="default" plain>追溯矩阵CSV</el-button>
          <el-button @click="exportFile('channel_csv')" :icon="icons.Share" type="default" plain>禅道CSV</el-button>
          <el-button @click="exportFile('jira')" :icon="icons.Ticket" type="default" plain>Jira+Xray</el-button>
          <el-button @click="exportFile('testlink')" :icon="icons.CircleCheck" type="default" plain>TestLink</el-button>
          <el-button @click="exportFile('testrail')" :icon="icons.CircleCheck" type="default" plain>TestRail</el-button>
        </div>
        
        <el-tabs v-model="activeTab" class="main-tabs">
          <el-tab-pane label="功能点" name="features">
            <div class="tab-content">
              <div v-if="!isGenerated" class="empty-tab">
                <el-icon :size="48" class="empty-icon"><component :is="icons.Box" /></el-icon>
                <span>暂无功能点数据，请先上传文件并生成</span>
              </div>
              <div v-else>
                <el-table :data="features" stripe border>
                  <el-table-column prop="name" label="功能点名称" min-width="200" />
                  <el-table-column prop="module" label="所属模块" width="120">
                    <template #default="scope">
                      <el-tag size="small">{{ scope.row.module }}</el-tag>
                    </template>
                  </el-table-column>
                  <el-table-column prop="description" label="描述" min-width="200" />
                  <el-table-column prop="casesCount" label="用例数" width="80" align="center" />
                  <el-table-column prop="coverage" label="覆盖率" width="100">
                    <template #default="scope">
                      <el-progress :percentage="scope.row.coverage" :color="scope.row.coverage === 100 ? '#67c23a' : '#409eff'" :stroke-width="12" />
                    </template>
                  </el-table-column>
                </el-table>
              </div>
            </div>
          </el-tab-pane>
          
          <el-tab-pane label="测试用例" name="cases">
            <div class="tab-content">
              <div v-if="!isGenerated" class="empty-tab">
                <el-icon :size="48" class="empty-icon"><component :is="icons.Box" /></el-icon>
                <span>暂无测试用例，请先上传文件并生成</span>
              </div>
              <div v-else>
                <div class="case-toolbar">
                  <div class="case-filters">
                    <el-tag
                      v-for="cat in scenarioCategories"
                      :key="cat.key"
                      :type="cat.count > 0 ? cat.tagType : 'info'"
                      :effect="'plain'"
                      class="filter-tag"
                      @click="filterByScenario(cat.key)"
                    >
                      {{ cat.label }} ({{ cat.count }})
                    </el-tag>
                  </div>
                  <el-select v-model="priorityFilter" placeholder="优先级筛选" class="priority-filter" clearable>
                    <el-option label="全部优先级" value="" />
                    <el-option label="P0 - 核心" value="P0" />
                    <el-option label="P1 - 重要" value="P1" />
                    <el-option label="P2 - 一般" value="P2" />
                  </el-select>
                </div>
                <el-table :data="filteredCases" stripe border class="cases-table" @selection-change="handleSelectionChange">
                  <el-table-column type="selection" width="45" />
                  <el-table-column label="序号" width="55" align="center">
                    <template #default="scope">
                      <span class="index-badge">{{ (pagination.currentPage - 1) * pagination.pageSize + scope.$index + 1 }}</span>
                    </template>
                  </el-table-column>
                  <el-table-column prop="case_id" label="用例ID" width="130">
                    <template #default="scope">
                      <code class="case-id">{{ scope.row.case_id }}</code>
                    </template>
                  </el-table-column>
                  <el-table-column prop="module" label="所属模块" width="140">
                    <template #default="scope">
                      <el-input v-if="editMode" v-model="scope.row.module" size="small" />
                      <el-tag v-else type="success" size="small">{{ scope.row.module || '未分类' }}</el-tag>
                    </template>
                  </el-table-column>
                  <el-table-column prop="name" label="测试标题" min-width="200" show-overflow-tooltip>
                    <template #default="scope">
                      <el-input v-if="editMode" v-model="scope.row.name" size="small" />
                      <span v-else>{{ scope.row.name }}</span>
                    </template>
                  </el-table-column>
                  <el-table-column prop="preconditions" label="前置条件" min-width="120" show-overflow-tooltip>
                    <template #default="scope">
                      <el-input v-if="editMode" v-model="scope.row.preconditions" type="textarea" size="small" :rows="2" />
                      <span v-else>{{ scope.row.preconditions }}</span>
                    </template>
                  </el-table-column>
                  <el-table-column prop="steps" label="操作步骤" min-width="200" show-overflow-tooltip>
                    <template #default="scope">
                      <el-input v-if="editMode" v-model="scope.row.steps" type="textarea" size="small" :rows="2" />
                      <span v-else>{{ Array.isArray(scope.row.steps) ? scope.row.steps.join(' → ') : scope.row.steps }}</span>
                    </template>
                  </el-table-column>
                  <el-table-column prop="expected_result" label="预期结果" min-width="150" show-overflow-tooltip>
                    <template #default="scope">
                      <el-input v-if="editMode" v-model="scope.row.expected_result" type="textarea" size="small" :rows="2" />
                      <span v-else>{{ scope.row.expected_result }}</span>
                    </template>
                  </el-table-column>
                  <el-table-column prop="test_type" label="测试类型" width="100">
                    <template #default="scope">
                      <el-select v-if="editMode" v-model="scope.row.test_type" size="small">
                        <el-option label="功能" value="功能" />
                        <el-option label="边界" value="边界" />
                        <el-option label="异常" value="异常" />
                        <el-option label="交互" value="交互" />
                        <el-option label="权限" value="权限" />
                        <el-option label="安全" value="安全" />
                        <el-option label="性能" value="性能" />
                      </el-select>
                      <el-tag v-else :type="getTagType(scope.row.test_type)" size="small">{{ scope.row.test_type || scope.row.type }}</el-tag>
                    </template>
                  </el-table-column>
                  <el-table-column prop="priority" label="优先级" width="90">
                    <template #default="scope">
                      <el-select v-if="editMode" v-model="scope.row.priority" size="small">
                        <el-option label="P0" value="P0" />
                        <el-option label="P1" value="P1" />
                        <el-option label="P2" value="P2" />
                      </el-select>
                      <el-tag v-else :type="scope.row.priority === 'P0' ? 'danger' : scope.row.priority === 'P1' ? 'warning' : 'info'" size="small">
                        {{ scope.row.priority }}
                      </el-tag>
                    </template>
                  </el-table-column>
                  <el-table-column prop="status" label="执行" width="80">
                    <template #default="scope">
                      <el-select v-model="scope.row.status" size="small" class="status-select">
                        <el-option label="未执行" value="未执行" />
                        <el-option label="执行中" value="执行中" />
                        <el-option label="通过" value="通过" />
                        <el-option label="失败" value="失败" />
                        <el-option label="阻塞" value="阻塞" />
                      </el-select>
                    </template>
                  </el-table-column>
                  <el-table-column prop="remark" label="备注/来源" min-width="140" show-overflow-tooltip>
                    <template #default="scope">
                      <el-input v-if="editMode" v-model="scope.row.remark" size="small" />
                      <span v-else class="remark-text">{{ scope.row.remark || '-' }}</span>
                    </template>
                  </el-table-column>
                  <el-table-column label="操作" width="140" fixed="right" class-name="action-cell">
                    <template #default="scope">
                      <div class="action-btns">
                        <el-button size="small" text @click="handleEdit(scope.row)">编辑</el-button>
                        <el-button size="small" text type="danger" @click="handleDelete(scope.row)">删除</el-button>
                      </div>
                    </template>
                  </el-table-column>
                </el-table>
                
                <el-pagination
                  class="pagination"
                  layout="total, sizes, prev, pager, next, jumper"
                  :total="pagination.total"
                  :page-size="pagination.pageSize"
                  :current-page="pagination.currentPage"
                  :page-sizes="[10, 20, 50, 100]"
                  @size-change="handlePageSizeChange"
                  @current-change="handlePageChange"
                />
              </div>
            </div>
          </el-tab-pane>
          
          <el-tab-pane label="自检报告" name="selfcheck">
            <div class="tab-content">
              <div v-if="!isGenerated" class="empty-tab">
                <el-icon :size="48" class="empty-icon"><component :is="icons.CircleCheck" /></el-icon>
                <span>暂无自检报告，请先生成测试用例</span>
              </div>
              <div v-else class="selfcheck-report">
                <div class="report-header">
                  <h3>AI生成自检报告</h3>
                  <el-tag type="success" size="small">生成完成</el-tag>
                </div>
                <div class="report-section">
                  <h4>✅ 覆盖完整性检查</h4>
                  <el-descriptions :column="2" border>
                    <el-descriptions-item label="覆盖模块数">{{ selfCheckData.modulesCovered }}</el-descriptions-item>
                    <el-descriptions-item label="总用例数">{{ selfCheckData.totalCases }}</el-descriptions-item>
                    <el-descriptions-item label="P0核心流程">{{ selfCheckData.p0Count }} 条</el-descriptions-item>
                    <el-descriptions-item label="P1重要场景">{{ selfCheckData.p1Count }} 条</el-descriptions-item>
                    <el-descriptions-item label="P2一般场景">{{ selfCheckData.p2Count }} 条</el-descriptions-item>
                    <el-descriptions-item label="控件覆盖率">{{ selfCheckData.controlCoverage }}%</el-descriptions-item>
                  </el-descriptions>
                </div>
                <div class="report-section">
                  <h4>📊 场景分类统计</h4>
                  <div class="scenario-stats">
                    <div class="stat-card normal">
                      <span class="stat-num">{{ selfCheckData.scenarioStats.normal }}</span>
                      <span class="stat-label">正常流程</span>
                    </div>
                    <div class="stat-card boundary">
                      <span class="stat-num">{{ selfCheckData.scenarioStats.boundary }}</span>
                      <span class="stat-label">边界值</span>
                    </div>
                    <div class="stat-card exception">
                      <span class="stat-num">{{ selfCheckData.scenarioStats.exception }}</span>
                      <span class="stat-label">异常输入</span>
                    </div>
                    <div class="stat-card interaction">
                      <span class="stat-num">{{ selfCheckData.scenarioStats.interaction }}</span>
                      <span class="stat-label">交互场景</span>
                    </div>
                  </div>
                </div>
                <div class="report-section">
                  <h4>🔍 逻辑真实性检查</h4>
                  <el-alert type="success" :closable="false" show-icon>
                    <template #title>
                      <span>✅ 未检测到AI虚构逻辑，所有用例均基于输入素材生成</span>
                    </template>
                  </el-alert>
                </div>
                <div class="report-section">
                  <h4>⚠️ 未覆盖场景标注</h4>
                  <div v-if="selfCheckData.uncoveredScenarios.length > 0" class="uncovered-list">
                    <el-tag
                      v-for="(item, idx) in selfCheckData.uncoveredScenarios"
                      :key="idx"
                      type="warning"
                      size="small"
                      class="uncovered-tag"
                    >
                      {{ item }}
                    </el-tag>
                  </div>
                  <el-empty v-else description="所有场景已全覆盖" :image-size="60" />
                </div>
                <div class="report-section summary-section">
                  <h4>📋 统计总结</h4>
                  <div class="summary-grid">
                    <div class="summary-item">
                      <span class="summary-value">{{ selfCheckData.modulesCovered }}</span>
                      <span class="summary-label">覆盖模块总数</span>
                    </div>
                    <div class="summary-item">
                      <span class="summary-value">{{ selfCheckData.totalCases }}</span>
                      <span class="summary-label">总用例数量</span>
                    </div>
                    <div class="summary-item">
                      <span class="summary-value">{{ selfCheckData.p0Count }}</span>
                      <span class="summary-label">P0核心流程</span>
                    </div>
                    <div class="summary-item">
                      <span class="summary-value">{{ selfCheckData.p1Count + selfCheckData.p2Count }}</span>
                      <span class="summary-label">P1+P2补充</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </el-tab-pane>
          
          <el-tab-pane label="测试边界" name="boundaries">
            <div class="tab-content">
              <div v-if="!isGenerated" class="empty-tab">
                <el-icon :size="48" class="empty-icon"><component :is="icons.Box" /></el-icon>
                <span>暂无测试边界数据，请先上传文件并生成</span>
              </div>
              <div v-else>
                <el-table :data="boundaries" stripe border>
                  <el-table-column prop="name" label="边界名称" min-width="200" />
                  <el-table-column prop="module" label="所属模块" width="120">
                    <template #default="scope">
                      <el-tag size="small">{{ scope.row.module }}</el-tag>
                    </template>
                  </el-table-column>
                  <el-table-column prop="description" label="边界描述" min-width="250" />
                  <el-table-column prop="type" label="边界类型" width="100">
                    <template #default="scope">
                      <el-tag type="warning">{{ scope.row.type }}</el-tag>
                    </template>
                  </el-table-column>
                </el-table>
              </div>
            </div>
          </el-tab-pane>
          
          <el-tab-pane label="测试数据" name="data">
            <div class="tab-content">
              <div v-if="!isGenerated" class="empty-tab">
                <el-icon :size="48" class="empty-icon"><component :is="icons.Box" /></el-icon>
                <span>暂无测试数据，请先上传文件并生成</span>
              </div>
              <div v-else>
                <el-table :data="testData" stripe border>
                  <el-table-column prop="name" label="数据名称" min-width="150" />
                  <el-table-column prop="module" label="所属模块" width="120">
                    <template #default="scope">
                      <el-tag size="small">{{ scope.row.module }}</el-tag>
                    </template>
                  </el-table-column>
                  <el-table-column prop="type" label="数据类型" width="100" />
                  <el-table-column prop="value" label="数据值" min-width="200" />
                </el-table>
              </div>
            </div>
          </el-tab-pane>
          
          <el-tab-pane label="接口用例" name="api">
            <div class="tab-content">
              <div v-if="!isGenerated" class="empty-tab">
                <el-icon :size="48" class="empty-icon"><component :is="icons.Box" /></el-icon>
                <span>暂无接口用例，请先上传文件并生成</span>
              </div>
              <div v-else>
                <div class="case-category-tabs">
                  <el-tabs v-model="caseCategory" type="card" class="category-tabs">
                    <el-tab-pane name="all">
                      <template #label>
                        <span>全部 ({{ swaggerAllCases.length }})</span>
                      </template>
                      <el-table :data="swaggerAllCases" stripe border size="small" max-height="500">
                        <el-table-column prop="name" label="用例名称" min-width="200" show-overflow-tooltip />
                        <el-table-column prop="module" label="模块" width="120">
                          <template #default="scope">
                            <el-tag size="small">{{ scope.row.module }}</el-tag>
                          </template>
                        </el-table-column>
                        <el-table-column prop="type" label="类型" width="80">
                          <template #default="scope">
                            <el-tag :type="getCaseTypeTag(scope.row.type)" size="small">{{ scope.row.type }}</el-tag>
                          </template>
                        </el-table-column>
                        <el-table-column prop="sub_type" label="子类" width="120" show-overflow-tooltip />
                        <el-table-column prop="priority" label="优先级" width="70">
                          <template #default="scope">
                            <el-tag :type="scope.row.priority === '高' ? 'danger' : scope.row.priority === '中' ? 'warning' : 'info'" size="small">
                              {{ scope.row.priority }}
                            </el-tag>
                          </template>
                        </el-table-column>
                        <el-table-column prop="status" label="执行" width="70">
                          <template #default="scope">
                            <el-tag :type="getStatusTagType(scope.row.status)" size="small">{{ scope.row.status }}</el-tag>
                          </template>
                        </el-table-column>
                      </el-table>
                    </el-tab-pane>
                    <el-tab-pane name="functional">
                      <template #label>
                        <span>功能 ({{ functionalCases.length }})</span>
                      </template>
                      <el-table :data="functionalCases" stripe border size="small" max-height="500">
                        <el-table-column prop="name" label="用例名称" min-width="200" show-overflow-tooltip />
                        <el-table-column prop="module" label="模块" width="120">
                          <template #default="scope">
                            <el-tag size="small">{{ scope.row.module }}</el-tag>
                          </template>
                        </el-table-column>
                        <el-table-column prop="sub_type" label="子类" width="120" show-overflow-tooltip />
                        <el-table-column prop="priority" label="优先级" width="70">
                          <template #default="scope">
                            <el-tag :type="scope.row.priority === '高' ? 'danger' : scope.row.priority === '中' ? 'warning' : 'info'" size="small">
                              {{ scope.row.priority }}
                            </el-tag>
                          </template>
                        </el-table-column>
                        <el-table-column prop="status" label="执行" width="70">
                          <template #default="scope">
                            <el-tag :type="getStatusTagType(scope.row.status)" size="small">{{ scope.row.status }}</el-tag>
                          </template>
                        </el-table-column>
                      </el-table>
                    </el-tab-pane>
                    <el-tab-pane name="performance">
                      <template #label>
                        <span>性能 ({{ performanceCases.length }})</span>
                      </template>
                      <el-table :data="performanceCases" stripe border size="small" max-height="500">
                        <el-table-column prop="name" label="用例名称" min-width="200" show-overflow-tooltip />
                        <el-table-column prop="module" label="模块" width="120">
                          <template #default="scope">
                            <el-tag size="small">{{ scope.row.module }}</el-tag>
                          </template>
                        </el-table-column>
                        <el-table-column prop="sub_type" label="子类" width="120" show-overflow-tooltip />
                        <el-table-column label="并发数" width="80">
                          <template #default="scope">
                            <span v-if="scope.row.performance_meta?.concurrency">{{ scope.row.performance_meta.concurrency }}</span>
                            <span v-else>-</span>
                          </template>
                        </el-table-column>
                        <el-table-column label="持续时长" width="90">
                          <template #default="scope">
                            <span v-if="scope.row.performance_meta?.duration_seconds">{{ scope.row.performance_meta.duration_seconds }}s</span>
                            <span v-else>-</span>
                          </template>
                        </el-table-column>
                        <el-table-column prop="priority" label="优先级" width="70">
                          <template #default="scope">
                            <el-tag :type="scope.row.priority === '高' ? 'danger' : scope.row.priority === '中' ? 'warning' : 'info'" size="small">
                              {{ scope.row.priority }}
                            </el-tag>
                          </template>
                        </el-table-column>
                      </el-table>
                    </el-tab-pane>
                    <el-tab-pane name="security">
                      <template #label>
                        <span>安全 ({{ securityCases.length }})</span>
                      </template>
                      <el-table :data="securityCases" stripe border size="small" max-height="500">
                        <el-table-column prop="name" label="用例名称" min-width="200" show-overflow-tooltip />
                        <el-table-column prop="module" label="模块" width="120">
                          <template #default="scope">
                            <el-tag size="small">{{ scope.row.module }}</el-tag>
                          </template>
                        </el-table-column>
                        <el-table-column prop="sub_type" label="子类" width="120" show-overflow-tooltip />
                        <el-table-column label="严重级别" width="90">
                          <template #default="scope">
                            <el-tag v-if="scope.row.security_meta?.severity" :type="scope.row.security_meta.severity === '高危' ? 'danger' : 'warning'" size="small">
                              {{ scope.row.security_meta.severity }}
                            </el-tag>
                            <span v-else>-</span>
                          </template>
                        </el-table-column>
                        <el-table-column prop="priority" label="优先级" width="70">
                          <template #default="scope">
                            <el-tag :type="scope.row.priority === '高' ? 'danger' : scope.row.priority === '中' ? 'warning' : 'info'" size="small">
                              {{ scope.row.priority }}
                            </el-tag>
                          </template>
                        </el-table-column>
                      </el-table>
                    </el-tab-pane>
                  </el-tabs>
                </div>

                <div v-if="riskAssessment" class="risk-assessment-section">
                  <el-divider>
                    <span class="divider-title">AI 缺陷风险评估</span>
                  </el-divider>
                  <el-descriptions :column="3" border size="small">
                    <el-descriptions-item label="风险等级">
                      <el-tag :type="riskAssessment.risk_level === '高' ? 'danger' : riskAssessment.risk_level === '中' ? 'warning' : 'success'">
                        {{ riskAssessment.risk_level }}
                      </el-tag>
                    </el-descriptions-item>
                    <el-descriptions-item label="接口数量">{{ riskAssessment.api_count }}</el-descriptions-item>
                    <el-descriptions-item label="用例汇总">{{ riskAssessment.summary }}</el-descriptions-item>
                  </el-descriptions>
                  <div v-if="riskAssessment.risks?.length" class="risks-list">
                    <div v-for="(risk, idx) in riskAssessment.risks" :key="idx" class="risk-item">
                      <el-tag :type="risk.level === '高' ? 'danger' : risk.level === '中' ? 'warning' : 'info'" size="small">
                        {{ risk.level }}风险
                      </el-tag>
                      <el-tag type="primary" size="small" style="margin-left: 8px">{{ risk.category }}</el-tag>
                      <span class="risk-desc">{{ risk.description }}</span>
                    </div>
                  </div>
                  <div v-if="riskAssessment.suggestions?.length" class="suggestions-list">
                    <span class="suggestions-label">AI 建议：</span>
                    <span v-for="(sug, idx) in riskAssessment.suggestions" :key="idx" class="suggestion-item">
                      {{ sug }}{{ idx < riskAssessment.suggestions.length - 1 ? ' | ' : '' }}
                    </span>
                  </div>
                </div>

                <div class="ai-output-actions">
                  <el-divider>
                    <span class="divider-title">AI 赋能产出 - 一键导出</span>
                  </el-divider>
                  <div class="export-buttons-row">
                    <el-button type="primary" :icon="icons.Setting" size="small" @click="downloadPostman">
                      Postman Collection
                    </el-button>
                    <el-button type="success" :icon="icons.Odometer" size="small" @click="downloadJMeter">
                      JMeter 性能测试计划
                    </el-button>
                    <el-button type="warning" :icon="icons.Document" size="small" @click="downloadPytest">
                      pytest 自动化脚本
                    </el-button>
                  </div>
                </div>
              </div>
            </div>
          </el-tab-pane>
          
          <el-tab-pane label="分析/追溯" name="analysis">
            <div class="tab-content">
              <div v-if="!isGenerated" class="empty-tab">
                <el-icon :size="48" class="empty-icon"><component :is="icons.Box" /></el-icon>
                <span>暂无分析数据，请先上传文件并生成</span>
              </div>
              <div v-else>
                <div class="coverage-section">
                  <div class="coverage-header">
                    <span class="section-title">覆盖率统计</span>
                    <div class="execution-row">
                      <span class="execution-label">执行轮次：</span>
                      <el-select v-model="executionRound" placeholder="默认/无轮次" class="round-select">
                        <el-option label="默认/无轮次" value="default" />
                      </el-select>
                      <el-button type="primary" size="small" class="new-round-btn">+ 新一轮次</el-button>
                      <el-button type="default" size="small" class="compare-btn">跨轮对比</el-button>
                      <span class="execution-hint">未选轮次（执行状态写入默认存储）</span>
                    </div>
                  </div>
                  
                  <div class="stats-row">
                    <div class="stat-item pass">
                      <el-icon><component :is="icons.CircleCheck" /></el-icon>
                      <span class="stat-value">通过 {{ coverageStats.passed }}</span>
                    </div>
                    <div class="stat-item fail">
                      <el-icon><component :is="icons.CircleClose" /></el-icon>
                      <span class="stat-value">失败 {{ coverageStats.failed }}</span>
                    </div>
                    <div class="stat-item blocked">
                      <el-icon><component :is="icons.Lock" /></el-icon>
                      <span class="stat-value">阻塞 {{ coverageStats.blocked }}</span>
                    </div>
                    <div class="stat-item pending">
                      <el-icon><component :is="icons.Clock" /></el-icon>
                      <span class="stat-value">未执行 {{ coverageStats.pending }}</span>
                    </div>
                  </div>
                  
                  <el-button type="text" size="small" class="clean-btn">清理无效执行状态</el-button>
                  
                  <div class="summary-cards">
                    <div class="summary-card">
                      <div class="card-value">{{ coverageStats.modules }}</div>
                      <div class="card-label">模块</div>
                    </div>
                    <div class="summary-card">
                      <div class="card-value">{{ coverageStats.features }}</div>
                      <div class="card-label">功能点</div>
                    </div>
                    <div class="summary-card">
                      <div class="card-value">{{ coverageStats.cases }}</div>
                      <div class="card-label">测试用例</div>
                    </div>
                    <div class="summary-card">
                      <div class="card-value">{{ coverageStats.boundaries }}</div>
                      <div class="card-label">测试边界</div>
                    </div>
                  </div>
                  
                  <div class="coverage-progress">
                    <div class="progress-header">
                      <span class="progress-title">功能点用例覆盖率：{{ coverageStats.featureCoverage }}/{{ coverageStats.features }} ({{ coverageStats.featureCoveragePercent }}%)</span>
                    </div>
                    <div class="progress-bar-container">
                      <div class="progress-bar-fill" :style="{ width: coverageStats.featureCoveragePercent + '%' }"></div>
                    </div>
                  </div>
                  
                  <div class="coverage-chart">
                    <div class="chart-ring">
                      <div class="ring-inner">
                        <div class="ring-value">{{ coverageStats.featureCoveragePercent }}%</div>
                        <div class="ring-label">已覆盖</div>
                      </div>
                    </div>
                    <div class="chart-legend">
                      <div class="legend-item">
                        <span class="legend-dot covered"></span>
                        <span>已覆盖 {{ coverageStats.featureCoverage }}</span>
                      </div>
                      <div class="legend-item">
                        <span class="legend-dot uncovered"></span>
                        <span>未覆盖 {{ coverageStats.features - coverageStats.featureCoverage }}</span>
                      </div>
                    </div>
                    <div class="chart-bars">
                      <div v-for="item in coverageBars" :key="item.name" class="bar-item">
                        <span class="bar-label">{{ item.name }}</span>
                        <div class="bar-track">
                          <div class="bar-fill" :style="{ width: item.coverage + '%' }"></div>
                        </div>
                        <span class="bar-value">{{ item.covered }}/{{ item.total }}</span>
                      </div>
                    </div>
                  </div>
                  
                  <div class="type-distribution">
                    <span class="dist-title">类型分布：</span>
                    <el-tag v-for="(count, type) in typeDistribution" :key="type" :type="getTagType(type)" size="small">
                      {{ type }} {{ count }}
                    </el-tag>
                  </div>
                  
                  <div class="module-cases">
                    <span class="dist-title">各模块用例数：</span>
                    <el-tag v-for="(count, module) in moduleCases" :key="module" type="info" size="small">
                      {{ module }} {{ count }}
                    </el-tag>
                  </div>
                  
                  <div class="gap-section">
                    <div class="gap-header">
                      <el-icon><component :is="icons.Warning" /></el-icon>
                      <span class="gap-title">覆盖缺口（建议补充）：</span>
                    </div>
                    <ul class="gap-list">
                      <li v-for="(gap, index) in coverageGaps" :key="index">
                        <span class="gap-bullet">•</span>
                        {{ gap }}
                      </li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          </el-tab-pane>
          
          <el-tab-pane label="思维导图" name="mindmap">
            <div class="tab-content">
              <div v-if="!isGenerated" class="empty-tab">
                <el-icon :size="48" class="empty-icon"><component :is="icons.Box" /></el-icon>
                <span>暂无思维导图数据，请先上传文件并生成</span>
              </div>
              <div v-else class="mindmap-container">
                <el-icon :size="128" class="mindmap-icon"><component :is="icons.Share" /></el-icon>
                <p class="mindmap-hint">思维导图展示区域</p>
              </div>
            </div>
          </el-tab-pane>
        </el-tabs>
      </div>
    </div>
    
    <el-dialog v-model="editDialogVisible" title="编辑测试用例" width="600px">
      <el-form :model="editForm" label-width="100px">
        <el-form-item label="模块">
          <el-input v-model="editForm.module" />
        </el-form-item>
        <el-form-item label="功能点">
          <el-input v-model="editForm.feature" />
        </el-form-item>
        <el-form-item label="用例标题">
          <el-input v-model="editForm.name" />
        </el-form-item>
        <el-form-item label="用例类型">
          <el-select v-model="editForm.type">
            <el-option label="功能" value="功能" />
            <el-option label="异常" value="异常" />
            <el-option label="边界" value="边界" />
            <el-option label="安全" value="安全" />
            <el-option label="性能" value="性能" />
            <el-option label="接口" value="接口" />
          </el-select>
        </el-form-item>
        <el-form-item label="优先级">
          <el-select v-model="editForm.priority">
            <el-option label="高" value="高" />
            <el-option label="中" value="中" />
            <el-option label="低" value="低" />
          </el-select>
        </el-form-item>
        <el-form-item label="前置条件">
          <el-input v-model="editForm.preconditions" type="textarea" :rows="3" />
        </el-form-item>
        <el-form-item label="操作步骤">
          <el-input v-model="editForm.stepsText" type="textarea" :rows="4" placeholder="每个步骤一行" />
        </el-form-item>
        <el-form-item label="预期结果">
          <el-input v-model="editForm.expected_result" type="textarea" :rows="3" />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="editForm.status">
            <el-option label="未执行" value="未执行" />
            <el-option label="执行中" value="执行中" />
            <el-option label="通过" value="通过" />
            <el-option label="失败" value="失败" />
            <el-option label="阻塞" value="阻塞" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSaveEdit">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import * as icons from '@element-plus/icons-vue'

const fileInput = ref(null)
const docType = ref('auto')
const selectedTemplate = ref('')
const requirementText = ref('')
const projectTitle = ref('智能自动化测试平台v1.0')
const lastSaveTime = ref('17:20')
const editMode = ref(false)
const exportScope = ref('all')
const activeTab = ref('analysis')
const executionRound = ref('default')

const isGenerated = ref(false)
const isGenerating = ref(false)
const generateStep = ref(0)

const inputLayers = reactive({
  A: false,
  B: false,
  C: false
})

const activeLayerCount = computed(() => {
  return Object.values(inputLayers).filter(v => v).length
})

const uploadedFiles = ref([])

const isImage = (file) => {
  return file.type.startsWith('image/')
}

const isDoc = (file) => {
  const docTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'application/msword', 'text/plain', 'text/markdown']
  return docTypes.includes(file.type) || file.name.endsWith('.md') || file.name.endsWith('.txt') || file.name.endsWith('.docx') || file.name.endsWith('.pdf')
}

watch(uploadedFiles, (files) => {
  if (files.length > 0) {
    const hasImages = files.some(f => isImage(f))
    const hasDocs = files.some(f => isDoc(f))
    inputLayers.A = hasDocs
    inputLayers.B = hasImages
    inputLayers.C = !!requirementText.value
  } else {
    inputLayers.A = false
    inputLayers.B = false
    inputLayers.C = !!requirementText.value
  }
}, { deep: true })

watch(requirementText, (val) => {
  if (val && val.trim()) {
    inputLayers.C = true
  } else if (uploadedFiles.value.length === 0) {
    inputLayers.C = false
  }
})

const priorityFilter = ref('')
const scenarioFilter = ref('')

const testCases = ref([])
const pagination = reactive({
  currentPage: 1,
  pageSize: 10,
  total: 0
})

const scenarioCategories = computed(() => {
  const cases = testCases.value
  return [
    { key: 'normal', label: '正常流程', count: cases.filter(c => c.test_type === '功能' || c.type === '功能').length, tagType: 'success' },
    { key: 'boundary', label: '边界值', count: cases.filter(c => c.test_type === '边界' || c.type === '边界').length, tagType: 'warning' },
    { key: 'exception', label: '异常输入', count: cases.filter(c => c.test_type === '异常' || c.type === '异常').length, tagType: 'danger' },
    { key: 'interaction', label: '交互场景', count: cases.filter(c => c.test_type === '交互' || c.test_type === '权限' || c.type === '交互' || c.type === '权限').length, tagType: 'primary' }
  ]
})

const filteredCases = computed(() => {
  let cases = testCases.value
  if (scenarioFilter.value) {
    const typeMap = {
      normal: ['功能'],
      boundary: ['边界'],
      exception: ['异常'],
      interaction: ['交互', '权限']
    }
    const types = typeMap[scenarioFilter.value] || []
    cases = cases.filter(c => types.includes(c.test_type || c.type))
  }
  if (priorityFilter.value) {
    cases = cases.filter(c => c.priority === priorityFilter.value)
  }
  const start = (pagination.currentPage - 1) * pagination.pageSize
  const end = start + pagination.pageSize
  pagination.total = cases.length
  return cases.slice(start, end)
})

const filterByScenario = (key) => {
  scenarioFilter.value = scenarioFilter.value === key ? '' : key
}

const selfCheckData = computed(() => {
  const cases = testCases.value
  const modules = [...new Set(cases.map(c => c.module).filter(Boolean))]
  const p0Count = cases.filter(c => c.priority === 'P0').length
  const p1Count = cases.filter(c => c.priority === 'P1').length
  const p2Count = cases.filter(c => c.priority === 'P2').length
  
  return {
    modulesCovered: modules.length,
    totalCases: cases.length,
    p0Count,
    p1Count,
    p2Count,
    controlCoverage: cases.length > 0 ? Math.min(100, Math.round(cases.length / 15 * 100)) : 0,
    scenarioStats: {
      normal: cases.filter(c => (c.test_type || c.type) === '功能').length,
      boundary: cases.filter(c => (c.test_type || c.type) === '边界').length,
      exception: cases.filter(c => (c.test_type || c.type) === '异常').length,
      interaction: cases.filter(c => ['交互', '权限'].includes(c.test_type || c.type)).length
    },
    uncoveredScenarios: cases.length === 0 ? ['暂无数据，等待生成'] : []
  }
})

const features = ref([])
const boundaries = ref([])
const testData = ref([])
const apiCases = ref([])

const selectedCases = ref([])
const editDialogVisible = ref(false)
const editingCase = ref(null)

const editForm = reactive({
  name: '',
  module: '',
  feature: '',
  type: '功能',
  priority: '中',
  preconditions: '',
  stepsText: '',
  expected_result: '',
  status: '未执行'
})

const coverageStats = reactive({
  passed: 0,
  failed: 0,
  blocked: 0,
  pending: 14,
  modules: 3,
  features: 9,
  cases: 14,
  boundaries: 6,
  featureCoverage: 9,
  featureCoveragePercent: 100
})

const coverageBars = ref([
  { name: '用户登录与认证', covered: 3, total: 3, coverage: 100 },
  { name: '考试作答', covered: 4, total: 4, coverage: 100 },
  { name: '成统与防作弊', covered: 2, total: 2, coverage: 100 }
])

const typeDistribution = reactive({
  '功能': 6,
  '边界': 1,
  '异常': 3,
  '安全': 2,
  '性能': 1,
  '场景': 0,
  '判定表': 0,
  '接口': 1
})

const moduleCases = reactive({
  '用户登录与认证': 6,
  '考试作答': 4,
  '成统与防作弊': 4
})

const coverageGaps = ref([
  '建议补充「场景法」用例（正常流程/异常流程各至少1条）'
])

const currentPageCases = computed(() => {
  const start = (pagination.currentPage - 1) * pagination.pageSize
  const end = start + pagination.pageSize
  return testCases.value.slice(start, end)
})

const swaggerInputType = ref('url')
const swaggerUrl = ref('')
const swaggerContent = ref('')
const swaggerFileInfo = ref(null)
const swaggerFileInput = ref(null)
const isSwaggerGenerating = ref(false)
const swaggerParseResult = ref(null)

const swaggerAllCases = ref([])
const functionalCases = ref([])
const performanceCases = ref([])
const securityCases = ref([])
const riskAssessment = ref(null)
const postmanCollection = ref(null)
const jmeterTemplate = ref('')
const pytestScript = ref('')
const caseCategory = ref('all')

const swaggerUrlExamples = [
  'http://localhost:8000/openapi.json',
  'https://petstore.swagger.io/v2/swagger.json',
  '/api/v1/swagger.json'
]

const swaggerUrlValid = ref(true)

const isValidUrl = (string) => {
  try {
    const url = new URL(string)
    return url.protocol === 'http:' || url.protocol === 'https:'
  } catch (_) {
    return false
  }
}

watch(swaggerUrl, (newVal) => {
  if (!newVal.trim()) {
    swaggerUrlValid.value = true
    return
  }
  const trimmed = newVal.trim()
  if (trimmed.startsWith('/')) {
    swaggerUrlValid.value = true
    return
  }
  swaggerUrlValid.value = isValidUrl(trimmed)
})

const swaggerExample = {
  "openapi": "3.0.0",
  "info": {
    "title": "示例API",
    "version": "1.0.0"
  },
  "paths": {
    "/api/login": {
      "post": {
        "summary": "用户登录",
        "tags": ["认证"],
        "requestBody": {
          "content": {
            "application/json": {
              "schema": {
                "type": "object",
                "properties": {
                  "username": { "type": "string" },
                  "password": { "type": "string" }
                }
              }
            }
          }
        },
        "responses": {
          "200": {
            "description": "登录成功",
            "content": {
              "application/json": {
                "schema": {
                  "type": "object",
                  "properties": {
                    "token": { "type": "string" }
                  }
                }
              }
            }
          }
        }
      }
    },
    "/api/user": {
      "get": {
        "summary": "获取用户信息",
        "tags": ["用户"],
        "parameters": [
          { "name": "id", "in": "query", "required": true, "schema": { "type": "string" } }
        ],
        "responses": {
          "200": {
            "description": "成功",
            "content": {
              "application/json": {
                "schema": {
                  "type": "object"
                }
              }
            }
          }
        }
      }
    }
  }
}

const loadSwaggerExample = () => {
  swaggerContent.value = JSON.stringify(swaggerExample, null, 2)
}

const triggerSwaggerUpload = () => {
  swaggerFileInput.value.click()
}

const handleSwaggerDrop = (e) => {
  const files = e.dataTransfer.files
  if (files.length > 0) {
    handleSwaggerFile(files[0])
  }
}

const handleSwaggerFileSelect = (e) => {
  const files = e.target.files
  if (files.length > 0) {
    handleSwaggerFile(files[0])
  }
}

const handleSwaggerFile = (file) => {
  swaggerFileInfo.value = { name: file.name, size: file.size }
  const reader = new FileReader()
  reader.onload = (e) => {
    swaggerContent.value = e.target.result
  }
  reader.readAsText(file)
}

const clearSwaggerFile = () => {
  swaggerFileInfo.value = null
  swaggerContent.value = ''
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

  if (swaggerInputType.value === 'url') {
    const trimmedUrl = swaggerUrl.value.trim()
    if (!isValidUrl(trimmedUrl) && !trimmedUrl.startsWith('/')) {
      ElMessage.error('URL 格式不正确，请输入有效的 http:// 或 https:// 开头的地址，或以 / 开头的相对路径')
      return
    }
  }

  isSwaggerGenerating.value = true
  swaggerParseResult.value = null

  try {
    const requestBody = {
      swagger_url: swaggerInputType.value === 'url' ? swaggerUrl.value.trim() : '',
      swagger_content: swaggerInputType.value !== 'url' ? swaggerContent.value.trim() : ''
    }

    const response = await fetch('/api/v1/swagger/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(requestBody)
    })

    if (!response.ok) {
      let errorDetail = `HTTP ${response.status}`
      try {
        const errorData = await response.json()
        errorDetail = errorData.detail || errorData.message || errorData.error || `服务器返回错误 (状态码 ${response.status})`
      } catch (_) {
        errorDetail = `服务器返回错误 (状态码 ${response.status})，请检查后端服务是否正常`
      }
      throw new Error(errorDetail)
    }

    const data = await response.json()

    if (data.success) {
      swaggerParseResult.value = data.info

      apiCases.value = data.api_cases || []
      testCases.value = data.test_cases || []
      features.value = data.features || []

      functionalCases.value = data.functional_cases || []
      performanceCases.value = data.performance_cases || []
      securityCases.value = data.security_cases || []
      swaggerAllCases.value = [
        ...functionalCases.value,
        ...performanceCases.value,
        ...securityCases.value
      ]
      riskAssessment.value = data.risk_assessment || null
      postmanCollection.value = data.postman_collection || null
      jmeterTemplate.value = data.jmeter_template || ''
      pytestScript.value = data.pytest_script || ''

      boundaries.value = []
      testData.value = []

      const totalCases = data.test_cases ? data.test_cases.length : 0
      const moduleCount = data.info ? data.info.modules : 0
      const stats = data.info?.stats || {}

      coverageStats.modules = moduleCount
      coverageStats.features = moduleCount
      coverageStats.cases = totalCases
      coverageStats.pending = totalCases
      coverageStats.featureCoverage = moduleCount
      coverageStats.featureCoveragePercent = moduleCount > 0 ? 100 : 0

      pagination.total = totalCases
      pagination.currentPage = 1

      moduleCases.value = {}
      if (features.value && Array.isArray(features.value)) {
        features.value.forEach(f => {
          moduleCases[f.name] = f.casesCount
        })
      }

      coverageBars.value = (features.value || []).map(f => ({
        name: f.name,
        covered: f.casesCount,
        total: f.casesCount,
        coverage: 100
      }))

      typeDistribution.value = {
        '接口': totalCases
      }

      isGenerated.value = true

      ElMessage.success(`Swagger 解析成功！共发现 ${data.info.total_apis} 个 API 接口，分布在 ${data.info.modules} 个模块，已生成 ${totalCases} 个测试用例`)
    } else {
      ElMessage.error(data.message || data.error || '解析失败，请确认 URL 指向的是有效的 Swagger/OpenAPI 文档')
    }
  } catch (error) {
    console.error('Swagger解析失败:', error)
    const errorMsg = error.message || '网络请求失败，请检查：\n1. URL 是否正确\n2. 后端服务是否正常\n3. 该地址是否可被后端服务器访问'
    ElMessage.error({
      message: errorMsg,
      duration: 5000,
      showClose: true
    })
  } finally {
    isSwaggerGenerating.value = false
  }
}

const formatFileSize = (bytes) => {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}

const clearUploadedFiles = () => {
  uploadedFiles.value = []
}

const removeFile = (index) => {
  uploadedFiles.value.splice(index, 1)
}

const triggerUpload = () => {
  fileInput.value.click()
}

const handleDrop = (e) => {
  const files = e.dataTransfer.files
  handleFiles(files)
}

const handleFileSelect = (e) => {
  const files = e.target.files
  handleFiles(files)
}

const handleFiles = (files) => {
  uploadedFiles.value = Array.from(files)
  uploadedFiles.value.forEach(file => {
    console.log('File uploaded:', file.name, file.size, file.type)
  })
}

const handleGenerate = async () => {
  if (activeLayerCount.value === 0) {
    ElMessage.warning('请至少提供一份输入素材（需求文档/系统截图/文字描述）')
    return
  }
  
  isGenerating.value = true
  generateStep.value = 1
  
  try {
    await new Promise(r => setTimeout(r, 500))
    generateStep.value = 2
    
    let data = null
    
    if (uploadedFiles.value.length > 0) {
      const formData = new FormData()
      formData.append('file', uploadedFiles.value[0])
      formData.append('doc_type', docType.value)
      formData.append('strategy', 'hybrid')
      formData.append('case_count', 20)
      
      const response = await fetch('/api/v1/upload', {
        method: 'POST',
        body: formData
      })
      
      data = await response.json()
      
      if (data.content) {
        requirementText.value = data.content
      }
    } else {
      let text = requirementText.value || '在线考试系统功能描述：用户登录认证、考试作答、成绩统计、防作弊等功能模块'
      
      const response = await fetch('/api/v1/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          text: text,
          doc_type: docType.value,
          strategy: 'hybrid',
          case_count: 20
        })
      })
      
      data = await response.json()
    }
    
    await new Promise(r => setTimeout(r, 500))
    generateStep.value = 3
    
    let cases = data?.test_cases || []
    
    if (cases.length > 0) {
      cases = cases.map((caseItem, idx) => {
        let moduleName = caseItem.module || caseItem.module_name || caseItem.feature_module || '未分类'
        let featureName = caseItem.feature || caseItem.feature_name || caseItem.function_point || '-'
        
        if (!moduleName || moduleName === '未分类') {
          const name = caseItem.name || ''
          if (name.includes('登录') || name.includes('认证')) moduleName = '用户登录与认证'
          else if (name.includes('考试') || name.includes('答题')) moduleName = '考试作答'
          else if (name.includes('成绩') || name.includes('排名')) moduleName = '成绩统计'
          else if (name.includes('作弊') || name.includes('异常')) moduleName = '防作弊'
          else moduleName = '其他模块'
        }
        
        if (!featureName || featureName === '-') {
          featureName = caseItem.name?.substring(0, 10) || '功能点'
        }
        
        const testType = caseItem.test_type || caseItem.type || '功能'
        const priority = caseItem.priority === '高' ? 'P0' : caseItem.priority === '中' ? 'P1' : caseItem.priority === '低' ? 'P2' : (caseItem.priority || 'P1')
        
        return {
          ...caseItem,
          case_id: caseItem.case_id || `TC-${moduleName.substring(0, 2).toUpperCase()}-${String(idx + 1).padStart(3, '0')}`,
          module: moduleName,
          feature: featureName,
          test_type: testType,
          priority: priority,
          remark: caseItem.remark || `素材来源：${inputLayers.A ? '需求文档' : inputLayers.B ? '系统截图' : '文字描述'}`,
          status: caseItem.status || '未执行'
        }
      })
    } else {
      const generationMode = data?.generation_mode || ''
      const analysisError = data?.analysis?.error || ''
      
      if (generationMode === 'rule' || generationMode === '') {
        ElMessage.warning('AI服务未启用，当前使用规则模板生成。请在"平台设置 > AI配置"中配置API Key')
      } else if (analysisError) {
        ElMessage.error(`AI生成失败: ${analysisError}`)
      } else {
        ElMessage.warning('AI生成结果为空，已回退到规则模板生成')
      }
      
      cases = []
    }
    
    await new Promise(r => setTimeout(r, 500))
    generateStep.value = 4
    
    testCases.value = cases
    
    const analysis = data?.analysis || {}
    const coverage = data?.coverage || {}
    
    if (analysis.features && Array.isArray(analysis.features)) {
      features.value = analysis.features
    } else {
      const moduleGroups = {}
      cases.forEach(c => {
        const m = c.module || '其他'
        if (!moduleGroups[m]) moduleGroups[m] = { name: m, module: m, description: '', casesCount: 0, coverage: 0 }
        moduleGroups[m].casesCount++
      })
      features.value = Object.values(moduleGroups)
    }
    
    if (analysis.boundaries && Array.isArray(analysis.boundaries)) {
      boundaries.value = analysis.boundaries
    } else {
      boundaries.value = []
    }
    
    if (coverage?.coverage_rate !== undefined) {
      coverageStats.rate = coverage.coverage_rate
    }
    
    await new Promise(r => setTimeout(r, 300))
    generateStep.value = 5
    
    pagination.total = testCases.value.length
    pagination.currentPage = 1
    
    coverageStats.cases = testCases.value.length
    coverageStats.pending = testCases.value.length
    
    isGenerated.value = true
    
    if (testCases.value.length === 0) {
      ElMessage.warning(data?.analysis?.error || '未生成任何测试用例，请检查AI配置')
    } else {
      ElMessage.success(`生成完成！共 ${testCases.value.length} 条测试用例`)
    }
  } catch (error) {
    console.error('生成失败:', error)
    ElMessage.error({
      message: '生成测试用例失败，请检查后端服务是否正常',
      duration: 5000,
      showClose: true
    })
  }
  
  isGenerating.value = false
  generateStep.value = 0
}

const toggleEditMode = () => {
  editMode.value = !editMode.value
}

const exportFile = (format) => {
  if (testCases.value.length === 0) {
    ElMessage.warning('暂无数据可导出')
    return
  }
  
  let content = ''
  let filename = `测试用例_${new Date().toLocaleDateString('zh-CN').replace(/\//g, '-')}`
  let mimeType = 'text/plain'
  
  const casesToExport = exportScope.value === 'selected' && selectedCases.value.length > 0
    ? selectedCases.value
    : testCases.value
  
  switch (format) {
    case 'markdown':
      content = generateMarkdown(casesToExport)
      filename += '.md'
      mimeType = 'text/markdown'
      break
    case 'json':
      content = JSON.stringify(casesToExport, null, 2)
      filename += '.json'
      mimeType = 'application/json'
      break
    case 'csv':
      content = generateCSV(casesToExport)
      filename += '.csv'
      mimeType = 'text/csv;charset=utf-8'
      break
    case 'excel':
      content = generateExcel(casesToExport)
      filename += '.xlsx'
      mimeType = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
      break
    case 'png':
      ElMessage.info('思维导图PNG导出功能正在开发中')
      return
    case 'html':
      content = generateHTML(casesToExport)
      filename += '.html'
      mimeType = 'text/html'
      break
    case 'data_csv':
      content = generateTestDataCSV()
      filename += '_测试数据.csv'
      mimeType = 'text/csv;charset=utf-8'
      break
    case 'sql':
      content = generateSQL(casesToExport)
      filename += '_造数.sql'
      mimeType = 'text/sql'
      break
    case 'script':
      content = generateScript(casesToExport)
      filename += '_造数脚本.py'
      mimeType = 'text/python'
      break
    case 'module_sql':
      content = generateModuleSQL(casesToExport)
      filename += '_建表造数.sql'
      mimeType = 'text/sql'
      break
    case 'module_script':
      content = generateModuleScript(casesToExport)
      filename += '_建表造数脚本.py'
      mimeType = 'text/python'
      break
    case 'module_analysis':
      content = generateModuleAnalysis(casesToExport)
      filename += '_模块分析.sql'
      mimeType = 'text/sql'
      break
    case 'curl':
      content = generateCurl(apiCases.value)
      filename += '_接口curl.txt'
      mimeType = 'text/plain'
      break
    case 'postman':
      content = generatePostman(apiCases.value)
      filename += '_postman_collection.json'
      mimeType = 'application/json'
      break
    case 'jmeter':
      content = generateJMeter(apiCases.value)
      filename += '_jmeter_plan.jmx'
      mimeType = 'application/xml'
      break
    case 'coverage_csv':
      content = generateCoverageCSV()
      filename += '_覆盖度.csv'
      mimeType = 'text/csv;charset=utf-8'
      break
    case 'trace_csv':
      content = generateTraceCSV(casesToExport)
      filename += '_追溯矩阵.csv'
      mimeType = 'text/csv;charset=utf-8'
      break
    case 'channel_csv':
      content = generateZentaoCSV(casesToExport)
      filename += '_禅道.csv'
      mimeType = 'text/csv;charset=utf-8'
      break
    case 'jira':
      content = generateJiraXray(casesToExport)
      filename += '_jira_xray.json'
      mimeType = 'application/json'
      break
    case 'testlink':
      content = generateTestLinkXML(casesToExport)
      filename += '_testlink.xml'
      mimeType = 'application/xml'
      break
    case 'testrail':
      content = generateTestRailCSV(casesToExport)
      filename += '_testrail.csv'
      mimeType = 'text/csv;charset=utf-8'
      break
    default:
      ElMessage.info(`正在开发${format}格式导出功能`)
      return
  }
  
  downloadFile(content, filename, mimeType)
}

const generateCSV = (cases) => {
  const headers = ['用例名称', '功能模块', '用例类型', '优先级', '前置条件', '测试步骤', '预期结果', '状态', '创建时间']
  const rows = cases.map(c => [
    `"${c.name || ''}"`,
    `"${c.module || ''}"`,
    `"${c.type || ''}"`,
    `"${c.priority || ''}"`,
    `"${c.preconditions || ''}"`,
    `"${Array.isArray(c.steps) ? c.steps.join('; ') : (c.steps || '')}"`,
    `"${c.expected_result || ''}"`,
    `"${c.status || ''}"`,
    `"${c.created_at || ''}"`
  ])
  return [headers.join(','), ...rows.map(r => r.join(','))].join('\n')
}

const generateMarkdown = (cases) => {
  let md = `# 测试用例导出报告\n\n`
  md += `生成时间: ${new Date().toLocaleString('zh-CN')}\n`
  md += `用例数量: ${cases.length}\n\n`
  cases.forEach((c, index) => {
    md += `## ${index + 1}. ${c.name}\n\n`
    md += `| 属性 | 值 |\n|------|----|\n`
    md += `| 功能模块 | ${c.module || '未分类'} |\n`
    md += `| 用例类型 | ${c.type || ''} |\n`
    md += `| 优先级 | ${c.priority || ''} |\n`
    md += `| 状态 | ${c.status || ''} |\n\n`
    md += `**前置条件**\n\n${c.preconditions || '-'} \n\n`
    md += `**测试步骤**\n\n`
    if (Array.isArray(c.steps)) {
      c.steps.forEach((step, i) => {
        md += `${i + 1}. ${step}\n`
      })
    } else {
      md += `${c.steps || '-'}\n`
    }
    md += `\n**预期结果**\n\n${c.expected_result || '-'} \n\n`
    md += `---\n\n`
  })
  return md
}

const generateHTML = (cases) => {
  return `<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <title>测试用例报告</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 40px; }
    h1 { color: #333; }
    table { border-collapse: collapse; width: 100%; margin: 20px 0; }
    th, td { border: 1px solid #ddd; padding: 12px; text-align: left; }
    th { background-color: #f2f2f2; }
    .tag { padding: 2px 8px; border-radius: 4px; font-size: 12px; }
    .tag-primary { background-color: #409eff; color: white; }
    .tag-danger { background-color: #f56c6c; color: white; }
    .tag-warning { background-color: #e6a23c; color: white; }
    .tag-success { background-color: #67c23a; color: white; }
    .tag-info { background-color: #909399; color: white; }
  </style>
</head>
<body>
  <h1>测试用例导出报告</h1>
  <p>生成时间: ${new Date().toLocaleString('zh-CN')}</p>
  <p>用例数量: ${cases.length}</p>
  <table>
    <tr><th>用例名称</th><th>功能模块</th><th>用例类型</th><th>优先级</th><th>前置条件</th><th>测试步骤</th><th>预期结果</th><th>状态</th></tr>
    ${cases.map(c => `
    <tr>
      <td>${c.name}</td>
      <td><span class="tag tag-success">${c.module}</span></td>
      <td><span class="tag tag-primary">${c.type}</span></td>
      <td><span class="tag ${c.priority === '高' ? 'tag-danger' : c.priority === '中' ? 'tag-warning' : 'tag-info'}">${c.priority}</span></td>
      <td>${c.preconditions}</td>
      <td>${Array.isArray(c.steps) ? c.steps.join('<br>') : c.steps}</td>
      <td>${c.expected_result}</td>
      <td><span class="tag tag-info">${c.status}</span></td>
    </tr>
    `).join('')}
  </table>
</body>
</html>`
}

const generateExcel = (cases) => {
  const headers = ['用例名称', '功能模块', '用例类型', '优先级', '前置条件', '测试步骤', '预期结果', '状态', '创建时间']
  const rows = cases.map(c => [
    c.name || '',
    c.module || '',
    c.type || '',
    c.priority || '',
    c.preconditions || '',
    Array.isArray(c.steps) ? c.steps.join('; ') : (c.steps || ''),
    c.expected_result || '',
    c.status || '',
    c.created_at || ''
  ])
  
  let content = headers.join('\t') + '\n'
  rows.forEach(row => {
    content += row.map(cell => {
      const str = String(cell)
      return str.includes('\t') || str.includes('\n') ? `"${str.replace(/"/g, '""')}"` : str
    }).join('\t') + '\n'
  })
  return content
}

const generateTestDataCSV = () => {
  const headers = ['数据名称', '所属模块', '数据类型', '数据值']
  const rows = testData.value.map(d => [
    `"${d.name || ''}"`,
    `"${d.module || ''}"`,
    `"${d.type || ''}"`,
    `"${d.value || ''}"`
  ])
  return [headers.join(','), ...rows.map(r => r.join(','))].join('\n')
}

const generateSQL = (cases) => {
  let sql = `-- 测试用例造数SQL\n-- 生成时间: ${new Date().toLocaleString('zh-CN')}\n-- 用例数量: ${cases.length}\n\n`
  sql += 'INSERT INTO test_cases (name, module, type, priority, preconditions, steps, expected_result, status) VALUES\n'
  const values = cases.map((c, i) => {
    const steps = Array.isArray(c.steps) ? c.steps.join('; ') : (c.steps || '')
    return `  ('${c.name.replace(/'/g, "''")}', '${c.module.replace(/'/g, "''")}', '${c.type.replace(/'/g, "''")}', '${c.priority.replace(/'/g, "''")}', '${c.preconditions.replace(/'/g, "''")}', '${steps.replace(/'/g, "''")}', '${c.expected_result.replace(/'/g, "''")}', '${c.status.replace(/'/g, "''")}')`
  })
  sql += values.join(',\n') + ';\n'
  return sql
}

const generateScript = (cases) => {
  let script = `# 测试用例造数脚本\n# 生成时间: ${new Date().toLocaleString('zh-CN')}\n# 用例数量: ${cases.length}\n\nimport sqlite3\n\nconn = sqlite3.connect('test_cases.db')\ncursor = conn.cursor()\n\n# 创建表\ncursor.execute('''\nCREATE TABLE IF NOT EXISTS test_cases (\n    id INTEGER PRIMARY KEY AUTOINCREMENT,\n    name TEXT,\n    module TEXT,\n    type TEXT,\n    priority TEXT,\n    preconditions TEXT,\n    steps TEXT,\n    expected_result TEXT,\n    status TEXT\n)\n''')\n\n# 插入数据\ntest_cases = [\n`
  cases.forEach((c, i) => {
    const steps = Array.isArray(c.steps) ? c.steps.join('; ') : (c.steps || '')
    script += `  {'name': '${c.name.replace(/'/g, "\\'")}', 'module': '${c.module.replace(/'/g, "\\'")}', 'type': '${c.type.replace(/'/g, "\\'")}', 'priority': '${c.priority.replace(/'/g, "\\'")}', 'preconditions': '${c.preconditions.replace(/'/g, "\\'")}', 'steps': '${steps.replace(/'/g, "\\'")}', 'expected_result': '${c.expected_result.replace(/'/g, "\\'")}', 'status': '${c.status.replace(/'/g, "\\'")}'}${i < cases.length - 1 ? ',' : ''}\n`
  })
  script += `]\n\ncursor.executemany('INSERT INTO test_cases (name, module, type, priority, preconditions, steps, expected_result, status) VALUES (:name, :module, :type, :priority, :preconditions, :steps, :expected_result, :status)', test_cases)\nconn.commit()\nprint(f'成功插入 {len(test_cases)} 条测试用例')\nconn.close()\n`
  return script
}

const generateModuleSQL = (cases) => {
  const modules = [...new Set(cases.map(c => c.module))]
  let sql = `-- 建表+造数SQL\n-- 生成时间: ${new Date().toLocaleString('zh-CN')}\n\n-- 创建测试用例表\nCREATE TABLE IF NOT EXISTS test_cases (\n    id INTEGER PRIMARY KEY AUTOINCREMENT,\n    name VARCHAR(255) NOT NULL,\n    module VARCHAR(100),\n    type VARCHAR(50),\n    priority VARCHAR(20),\n    preconditions TEXT,\n    steps TEXT,\n    expected_result TEXT,\n    status VARCHAR(20) DEFAULT '未执行',\n    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP\n);\n\n-- 创建功能模块表\nCREATE TABLE IF NOT EXISTS modules (\n    id INTEGER PRIMARY KEY AUTOINCREMENT,\n    name VARCHAR(100) UNIQUE NOT NULL,\n    description TEXT\n);\n\n-- 插入模块数据\nINSERT OR IGNORE INTO modules (name) VALUES\n${modules.map(m => `  ('${m.replace(/'/g, "''")}')`).join(',\n')};\n\n-- 插入测试用例数据\nINSERT INTO test_cases (name, module, type, priority, preconditions, steps, expected_result, status) VALUES\n`
  const values = cases.map((c, i) => {
    const steps = Array.isArray(c.steps) ? c.steps.join('; ') : (c.steps || '')
    return `  ('${c.name.replace(/'/g, "''")}', '${c.module.replace(/'/g, "''")}', '${c.type.replace(/'/g, "''")}', '${c.priority.replace(/'/g, "''")}', '${c.preconditions.replace(/'/g, "''")}', '${steps.replace(/'/g, "''")}', '${c.expected_result.replace(/'/g, "''")}', '${c.status.replace(/'/g, "''")}')`
  })
  sql += values.join(',\n') + ';\n'
  return sql
}

const generateModuleScript = (cases) => {
  let script = `# 建表造数脚本\n# 生成时间: ${new Date().toLocaleString('zh-CN')}\n\nimport sqlite3\n\nconn = sqlite3.connect('test_cases.db')\ncursor = conn.cursor()\n\n# 创建测试用例表\ncursor.execute('''\nCREATE TABLE IF NOT EXISTS test_cases (\n    id INTEGER PRIMARY KEY AUTOINCREMENT,\n    name VARCHAR(255) NOT NULL,\n    module VARCHAR(100),\n    type VARCHAR(50),\n    priority VARCHAR(20),\n    preconditions TEXT,\n    steps TEXT,\n    expected_result TEXT,\n    status VARCHAR(20) DEFAULT '未执行',\n    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP\n)\n''')\n\n# 创建功能模块表\ncursor.execute('''\nCREATE TABLE IF NOT EXISTS modules (\n    id INTEGER PRIMARY KEY AUTOINCREMENT,\n    name VARCHAR(100) UNIQUE NOT NULL,\n    description TEXT\n)\n''')\n\n# 插入模块数据\nmodules = [${[...new Set(cases.map(c => c.module))].map(m => `'${m.replace(/'/g, "\\'")}'`).join(', ')}]\ncursor.executemany('INSERT OR IGNORE INTO modules (name) VALUES (?)', [(m,) for m in modules])\n\n# 插入测试用例数据\ntest_cases = [\n`
  cases.forEach((c, i) => {
    const steps = Array.isArray(c.steps) ? c.steps.join('; ') : (c.steps || '')
    script += `  ('${c.name.replace(/'/g, "\\'")}', '${c.module.replace(/'/g, "\\'")}', '${c.type.replace(/'/g, "\\'")}', '${c.priority.replace(/'/g, "\\'")}', '${c.preconditions.replace(/'/g, "\\'")}', '${steps.replace(/'/g, "\\'")}', '${c.expected_result.replace(/'/g, "\\'")}', '${c.status.replace(/'/g, "\\'")}')${i < cases.length - 1 ? ',' : ''}\n`
  })
  script += `]\n\ncursor.executemany('INSERT INTO test_cases (name, module, type, priority, preconditions, steps, expected_result, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?)', test_cases)\nconn.commit()\nprint(f'成功插入 {len(test_cases)} 条测试用例')\nconn.close()\n`
  return script
}

const generateModuleAnalysis = (cases) => {
  const moduleCases = {}
  cases.forEach(c => {
    if (!moduleCases[c.module]) moduleCases[c.module] = []
    moduleCases[c.module].push(c)
  })
  
  let sql = `-- 按模块拆分SQL\n-- 生成时间: ${new Date().toLocaleString('zh-CN')}\n\n`
  Object.keys(moduleCases).forEach((module, idx) => {
    sql += `-- ========== ${module} (${moduleCases[module].length}条) ==========\n\n`
    sql += `INSERT INTO test_cases (name, module, type, priority, preconditions, steps, expected_result, status) VALUES\n`
    const values = moduleCases[module].map((c, i) => {
      const steps = Array.isArray(c.steps) ? c.steps.join('; ') : (c.steps || '')
      return `  ('${c.name.replace(/'/g, "''")}', '${c.module.replace(/'/g, "''")}', '${c.type.replace(/'/g, "''")}', '${c.priority.replace(/'/g, "''")}', '${c.preconditions.replace(/'/g, "''")}', '${steps.replace(/'/g, "''")}', '${c.expected_result.replace(/'/g, "''")}', '${c.status.replace(/'/g, "''")}')`
    })
    sql += values.join(',\n') + ';\n\n'
  })
  return sql
}

const getCaseTypeTag = (type) => {
  const map = { '功能': 'primary', '性能': 'warning', '安全': 'danger', '接口': 'success', '边界': 'info', '异常': 'info' }
  return map[type] || ''
}

const downloadPostman = () => {
  if (!postmanCollection.value) {
    ElMessage.warning('暂无 Postman 集合数据')
    return
  }
  const json = JSON.stringify(postmanCollection.value, null, 2)
  downloadFile(json, 'swagger_postman_collection.json', 'application/json')
  ElMessage.success('Postman Collection 已下载')
}

const downloadJMeter = () => {
  if (!jmeterTemplate.value) {
    ElMessage.warning('暂无 JMeter 模板数据')
    return
  }
  downloadFile(jmeterTemplate.value, 'swagger_jmeter_plan.jmx', 'application/xml')
  ElMessage.success('JMeter 测试计划已下载')
}

const downloadPytest = () => {
  if (!pytestScript.value) {
    ElMessage.warning('暂无 pytest 脚本数据')
    return
  }
  downloadFile(pytestScript.value, 'swagger_test_cases.py', 'text/python')
  ElMessage.success('pytest 自动化脚本已下载')
}

const generateCurl = (apis) => {
  let content = `# 接口cURL命令\n# 生成时间: ${new Date().toLocaleString('zh-CN')}\n\n`
  apis.forEach(api => {
    content += `# ${api.name}\n`
    content += `curl -X ${api.method} \\\n`
    content += `  http://localhost:8000${api.url} \\\n`
    content += `  -H "Content-Type: application/json"\n\n`
  })
  return content
}

const generatePostman = (apis) => {
  const collection = {
    info: {
      name: '测试接口集合',
      description: `生成时间: ${new Date().toLocaleString('zh-CN')}`,
      schema: 'https://schema.getpostman.com/json/collection/v2.1.0/collection.json'
    },
    item: apis.map(api => ({
      name: api.name,
      request: {
        method: api.method,
        url: {
          raw: `http://localhost:8000${api.url}`,
          protocol: 'http',
          host: ['localhost'],
          port: '8000',
          path: api.url.split('/').filter(p => p)
        },
        headers: [{ key: 'Content-Type', value: 'application/json' }]
      }
    }))
  }
  return JSON.stringify(collection, null, 2)
}

const generateJMeter = (apis) => {
  let xml = `<?xml version="1.0" encoding="UTF-8"?>
<jmeterTestPlan version="1.2" properties="5.0" jmeter="5.5">
  <hashTree>
    <TestPlan guiclass="TestPlanGui" testclass="TestPlan" testname="测试接口计划" enabled="true">
      <stringProp name="TestPlan.comments">生成时间: ${new Date().toLocaleString('zh-CN')}</stringProp>
      <boolProp name="TestPlan.functional_mode">false</boolProp>
      <boolProp name="TestPlan.serialize_threadgroups">false</boolProp>
      <elementProp name="TestPlan.user_defined_variables" elementType="Arguments" guiclass="ArgumentsPanel" testclass="Arguments" testname="用户定义的变量" enabled="true"/>
      <stringProp name="TestPlan.user_define_classpath"></stringProp>
    </TestPlan>
    <hashTree>
      <ThreadGroup guiclass="ThreadGroupGui" testclass="ThreadGroup" testname="线程组" enabled="true">
        <stringProp name="ThreadGroup.on_sample_error">continue</stringProp>
        <elementProp name="ThreadGroup.main_controller" elementType="LoopController" guiclass="LoopControlPanel" testclass="LoopController" testname="循环控制器" enabled="true">
          <boolProp name="LoopController.continue_forever">false</boolProp>
          <intProp name="LoopController.loops">1</intProp>
        </elementProp>
        <stringProp name="ThreadGroup.num_threads">1</stringProp>
        <stringProp name="ThreadGroup.ramp_time">1</stringProp>
        <boolProp name="ThreadGroup.scheduler">false</boolProp>
        <stringProp name="ThreadGroup.duration"></stringProp>
        <stringProp name="ThreadGroup.delay"></stringProp>
      </ThreadGroup>
      <hashTree>
`
  apis.forEach(api => {
    xml += `        <HTTPSamplerProxy guiclass="HttpTestSampleGui" testclass="HTTPSamplerProxy" testname="${api.name}" enabled="true">
          <elementProp name="HTTPsampler.Arguments" elementType="Arguments" guiclass="HTTPArgumentsPanel" testclass="Arguments" enabled="true"/>
          <stringProp name="HTTPSampler.domain">localhost</stringProp>
          <stringProp name="HTTPSampler.port">8000</stringProp>
          <stringProp name="HTTPSampler.protocol">http</stringProp>
          <stringProp name="HTTPSampler.contentEncoding"></stringProp>
          <stringProp name="HTTPSampler.path">${api.url}</stringProp>
          <stringProp name="HTTPSampler.method">${api.method}</stringProp>
          <boolProp name="HTTPSampler.follow_redirects">true</boolProp>
          <boolProp name="HTTPSampler.auto_redirects">false</boolProp>
          <boolProp name="HTTPSampler.use_keepalive">true</boolProp>
          <boolProp name="HTTPSampler.DO_MULTIPART_POST">false</boolProp>
          <stringProp name="HTTPSampler.embedded_url_re"></stringProp>
        </HTTPSamplerProxy>
        <hashTree/>
`
  })
  xml += `      </hashTree>
    </hashTree>
  </hashTree>
</jmeterTestPlan>`
  return xml
}

const generateCoverageCSV = () => {
  const rows = [
    ['统计项', '数值'],
    ['模块数', coverageStats.modules],
    ['功能点数', coverageStats.features],
    ['测试用例数', coverageStats.cases],
    ['测试边界数', coverageStats.boundaries],
    ['通过', coverageStats.passed],
    ['失败', coverageStats.failed],
    ['阻塞', coverageStats.blocked],
    ['未执行', coverageStats.pending],
    ['功能点覆盖率', coverageStats.featureCoveragePercent + '%']
  ]
  return rows.map(r => r.join(',')).join('\n')
}

const generateTraceCSV = (cases) => {
  const headers = ['用例名称', '功能模块', '用例类型', '优先级', '关联功能点']
  const rows = cases.map(c => [
    `"${c.name || ''}"`,
    `"${c.module || ''}"`,
    `"${c.type || ''}"`,
    `"${c.priority || ''}"`,
    `"${c.module || ''}"`
  ])
  return [headers.join(','), ...rows.map(r => r.join(','))].join('\n')
}

const generateZentaoCSV = (cases) => {
  const headers = ['用例标题', '所属模块', '用例类型', '优先级', '前置条件', '步骤', '预期', '状态']
  const rows = cases.map(c => [
    `"${c.name || ''}"`,
    `"${c.module || ''}"`,
    `"${c.type || '功能'}"`,
    `"${c.priority === '高' ? '1' : c.priority === '中' ? '2' : '3'}"`,
    `"${c.preconditions || ''}"`,
    `"${Array.isArray(c.steps) ? c.steps.join('\n') : (c.steps || '')}"`,
    `"${c.expected_result || ''}"`,
    `"${c.status || '未执行'}"`
  ])
  return [headers.join(','), ...rows.map(r => r.join(','))].join('\n')
}

const generateJiraXray = (cases) => {
  const json = {
    info: {
      project: { key: 'TEST' },
      summary: '测试用例导入',
      description: `生成时间: ${new Date().toLocaleString('zh-CN')}`
    },
    tests: cases.map(c => ({
      summary: c.name,
      description: c.preconditions || '',
      steps: (Array.isArray(c.steps) ? c.steps : [c.steps]).map(step => ({
        action: step || '',
        result: c.expected_result || ''
      })),
      customFields: {
        '模块': c.module || '',
        '用例类型': c.type || '',
        '优先级': c.priority || ''
      }
    }))
  }
  return JSON.stringify(json, null, 2)
}

const generateTestLinkXML = (cases) => {
  let xml = `<?xml version="1.0" encoding="UTF-8"?>
<testcases>
  <testsuite name="测试用例集">
`
  cases.forEach(c => {
    xml += `    <testcase name="${c.name}">
      <node_order>1</node_order>
      <external_id>${c.id}</external_id>
      <summary>${c.preconditions || ''}</summary>
      <steps>
`
    const steps = Array.isArray(c.steps) ? c.steps : [c.steps]
    steps.forEach((step, i) => {
      xml += `        <step>
          <step_number>${i + 1}</step_number>
          <actions>${step || ''}</actions>
          <expectedresults>${c.expected_result || ''}</expectedresults>
        </step>
`
    })
    xml += `      </steps>
      <custom_fields>
        <custom_field>
          <name>模块</name>
          <value>${c.module || ''}</value>
        </custom_field>
        <custom_field>
          <name>类型</name>
          <value>${c.type || ''}</value>
        </custom_field>
        <custom_field>
          <name>优先级</name>
          <value>${c.priority || ''}</value>
        </custom_field>
      </custom_fields>
    </testcase>
`
  })
  xml += `  </testsuite>
</testcases>`
  return xml
}

const generateTestRailCSV = (cases) => {
  const headers = ['Case ID', 'Title', 'Section', 'Type', 'Priority', 'Preconditions', 'Steps', 'Expected', 'Status']
  const rows = cases.map((c, i) => [
    '',
    `"${c.name || ''}"`,
    `"${c.module || ''}"`,
    `"${c.type || '功能'}"`,
    `"${c.priority || '中'}"`,
    `"${c.preconditions || ''}"`,
    `"${Array.isArray(c.steps) ? c.steps.join('\n') : (c.steps || '')}"`,
    `"${c.expected_result || ''}"`,
    `"${c.status || '未执行'}"`
  ])
  return [headers.join(','), ...rows.map(r => r.join(','))].join('\n')
}

const downloadFile = (content, filename, mimeType) => {
  const blob = new Blob([content], { type: mimeType })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
}

const handleSelectionChange = (val) => {
  selectedCases.value = val
}

const handlePageChange = (page) => {
  pagination.currentPage = page
}

const handlePageSizeChange = (size) => {
  pagination.pageSize = size
  pagination.currentPage = 1
}

const handleEdit = (row) => {
  editingCase.value = row
  editForm.module = row.module || ''
  editForm.feature = row.feature || ''
  editForm.name = row.name || ''
  editForm.type = row.type || '功能'
  editForm.priority = row.priority || '中'
  editForm.preconditions = row.preconditions || ''
  editForm.stepsText = Array.isArray(row.steps) ? row.steps.join('\n') : (row.steps || '')
  editForm.expected_result = row.expected_result || ''
  editForm.status = row.status || '未执行'
  editDialogVisible.value = true
}

const handleSaveEdit = () => {
  if (!editForm.name.trim()) {
    ElMessage.warning('请输入用例标题')
    return
  }
  
  const index = testCases.value.findIndex(c => c.id === editingCase.value.id)
  if (index !== -1) {
    testCases.value[index] = {
      ...testCases.value[index],
      module: editForm.module,
      feature: editForm.feature,
      name: editForm.name,
      type: editForm.type,
      priority: editForm.priority,
      preconditions: editForm.preconditions,
      steps: editForm.stepsText.split('\n').map(s => s.trim()).filter(s => s),
      expected_result: editForm.expected_result,
      status: editForm.status
    }
    ElMessage.success('保存成功')
  }
  
  editDialogVisible.value = false
  editingCase.value = null
}

const handleDelete = (row) => {
  if (confirm(`确定要删除用例 "${row.name}" 吗？`)) {
    testCases.value = testCases.value.filter(item => item.id !== row.id)
    pagination.total = testCases.value.length
    ElMessage.success('删除成功')
  }
}

const handleStatusChange = (row, value) => {
  row.status = value
}

const handleAddAllToLibrary = async () => {
  if (testCases.value.length === 0) return
  
  try {
    const response = await fetch('/api/v1/case_library', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ test_cases: testCases.value })
    })
    
    const data = await response.json()
    if (response.ok) {
      ElMessage.success(`成功将${data.count || testCases.value.length}条用例导入用例库`)
    } else {
      ElMessage.error('导入失败: ' + (data.detail || '未知错误'))
    }
  } catch (error) {
    console.error('导入失败:', error)
    ElMessage.error('导入用例库失败，请检查后端服务')
  }
}

const handleAddSelectedToLibrary = async () => {
  if (selectedCases.value.length === 0) {
    ElMessage.warning('请先选择要导入的用例')
    return
  }
  
  try {
    const response = await fetch('/api/v1/case_library', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ test_cases: selectedCases.value })
    })
    
    const data = await response.json()
    if (response.ok) {
      ElMessage.success(`成功将${data.count || selectedCases.value.length}条用例导入用例库`)
      selectedCases.value = []
    } else {
      ElMessage.error('导入失败: ' + (data.detail || '未知错误'))
    }
  } catch (error) {
    console.error('导入失败:', error)
    ElMessage.error('导入用例库失败，请检查后端服务')
  }
}

const getTagType = (type) => {
  const types = { '功能': 'success', '异常': 'danger', '边界': 'warning', '安全': 'danger', '性能': 'warning', '接口': 'primary', '交互': 'primary', '权限': 'info' }
  return types[type] || 'info'
}

const getStatusTagType = (status) => {
  const types = { '未执行': 'info', '执行中': 'warning', '通过': 'success', '失败': 'danger', '阻塞': 'error' }
  return types[status] || 'info'
}
</script>

<style scoped>
.ai-case-generator {
  min-height: 100vh;
  background-color: var(--color-bg-page);
}

.input-validation-section {
  margin-bottom: 16px;
  padding: 12px;
  background: var(--color-bg-hover);
  border-radius: var(--radius-lg);
  border: 1px solid var(--color-border);
}

.layer-badges {
  display: flex;
  gap: 12px;
  margin-top: 10px;
}

.layer-badge {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  font-size: var(--font-size-xs);
  transition: all 0.2s;
}

.layer-badge.active {
  border-color: var(--theme-primary);
  background: var(--theme-primary-light);
}

.layer-badge.empty {
  opacity: 0.6;
}

.layer-letter {
  width: 20px;
  height: 20px;
  background: var(--color-border);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: var(--font-weight-semibold);
  font-size: 12px;
  color: var(--color-text-secondary);
}

.layer-badge.active .layer-letter {
  background: var(--theme-primary);
  color: #fff;
}

.layer-name {
  font-weight: var(--font-weight-medium);
  color: var(--color-text-primary);
}

.layer-status {
  margin-left: auto;
  color: var(--color-text-tertiary);
}

.layer-badge.active .layer-status {
  color: var(--theme-primary);
}

.layer-tip {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 10px;
  font-size: var(--font-size-xs);
  color: var(--color-text-tertiary);
}

.source-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 10px;
  align-items: center;
}

.source-label {
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
  font-weight: var(--font-weight-medium);
}

.source-tag {
  font-size: 12px;
}

.generate-progress {
  margin-bottom: 16px;
  padding: 12px;
  background: var(--color-bg-card);
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border);
}

.generate-progress :deep(.el-step__title) {
  font-size: var(--font-size-xs);
}

.case-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
  gap: 12px;
  flex-wrap: wrap;
}

.case-filters {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.filter-tag {
  cursor: pointer;
  user-select: none;
  transition: all 0.2s;
}

.filter-tag:hover {
  opacity: 0.85;
}

.filter-tag.el-tag.is-active {
  background-color: var(--theme-primary);
  border-color: var(--theme-primary);
  color: #fff;
}

.priority-filter {
  width: 160px;
}

.case-id {
  background: var(--color-bg-hover);
  padding: 2px 6px;
  border-radius: var(--radius-sm);
  font-family: Menlo, Monaco, Consolas, monospace;
  font-size: 12px;
  color: var(--color-text-primary);
}

.remark-text {
  font-size: var(--font-size-xs);
  color: var(--color-text-tertiary);
}

.action-btns {
  display: inline-flex;
  gap: 8px;
  align-items: center;
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

.selfcheck-report {
  padding: 8px 0;
}

.report-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--color-divider);
}

.report-header h3 {
  margin: 0;
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
}

.report-section {
  margin-bottom: 20px;
}

.report-section h4 {
  margin: 0 0 12px 0;
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
}

.scenario-stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
}

.stat-card {
  padding: 16px;
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  text-align: center;
}

.stat-card.normal { border-top: 3px solid var(--theme-primary); }
.stat-card.boundary { border-top: 3px solid #f59e0b; }
.stat-card.exception { border-top: 3px solid #ef4444; }
.stat-card.interaction { border-top: 3px solid #6366f1; }

.stat-num {
  display: block;
  font-size: 28px;
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  line-height: 1.2;
}

.stat-label {
  display: block;
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
  margin-top: 4px;
}

.uncovered-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.uncovered-tag {
  background: #fef3c7;
  border-color: #fde68a;
  color: #92400e;
}

.summary-section {
  padding-top: 16px;
  border-top: 1px solid var(--color-divider);
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
}

.summary-item {
  text-align: center;
  padding: 16px;
  background: var(--color-bg-hover);
  border-radius: var(--radius-lg);
}

.summary-value {
  display: block;
  font-size: 32px;
  font-weight: var(--font-weight-semibold);
  color: var(--theme-primary);
  line-height: 1.2;
}

.summary-label {
  display: block;
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
  margin-top: 4px;
}

@media (max-width: 768px) {
  .scenario-stats,
  .summary-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

.page-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 24px 32px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.header-left {
  display: flex;
  align-items: center;
}

.logo-section {
  display: flex;
  align-items: center;
  gap: 16px;
}

.logo-icon {
  color: #ffd700;
}

.page-header h1 {
  font-size: 24px;
  font-weight: 600;
  margin: 0;
}

.subtitle {
  font-size: 14px;
  opacity: 0.9;
  margin: 4px 0 0 0;
}

.main-container {
  display: grid;
  grid-template-columns: 360px 1fr;
  gap: 20px;
  padding: 20px;
  max-width: 1920px;
  margin: 0 auto;
}

.left-panel {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.upload-section {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}

.upload-area {
  border: 2px dashed #d9d9d9;
  border-radius: 8px;
  padding: 40px 20px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s;
  background: #fafafa;
}

.upload-area:hover {
  border-color: #667eea;
  background: #f5f3ff;
}

.upload-icon {
  color: #667eea;
  margin-bottom: 12px;
}

.upload-title {
  font-size: 16px;
  font-weight: 500;
  color: #303133;
  margin: 0 0 8px 0;
}

.upload-hint {
  font-size: 13px;
  color: #909399;
  margin: 0;
}

.file-input {
  display: none;
}

.upload-tip {
  font-size: 12px;
  color: #c0c4cc;
  margin-top: 12px;
  text-align: center;
}

.uploaded-files {
  margin-top: 16px;
  border-top: 1px solid #ebeef5;
  padding-top: 16px;
}

.files-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.files-title {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
}

.file-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 12px;
  background: #fafafa;
  border-radius: 8px;
  margin-bottom: 8px;
  transition: all 0.2s;
}

.file-item:hover {
  background: #f5f7fa;
}

.file-icon {
  flex-shrink: 0;
}

.file-info {
  flex: 1;
  min-width: 0;
}

.file-name {
  display: block;
  font-size: 13px;
  color: #303133;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.file-size {
  display: block;
  font-size: 12px;
  color: #909399;
}

.file-status {
  flex-shrink: 0;
}

.success-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #67C23A;
  padding: 2px 8px;
  background: #f0f9eb;
  border-radius: 4px;
}

.doc-type-section, .template-section, .description-section, .action-section {
  background: white;
  border-radius: 12px;
  padding: 16px 20px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}

.section-label {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
  margin-bottom: 12px;
  display: block;
}

.api-tip, .auto-tip, .template-hint {
  font-size: 12px;
  color: #909399;
  margin-top: 8px;
  display: flex;
  align-items: center;
  gap: 4px;
}

.tip-icon {
  font-size: 14px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.generate-btn {
  width: 100%;
  padding: 14px;
  font-size: 16px;
  font-weight: 500;
}

.action-hint {
  font-size: 12px;
  color: var(--color-text-tertiary);
  margin-top: 8px;
  text-align: center;
}

.right-panel {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.project-header {
  background: white;
  border-radius: 12px;
  padding: 16px 24px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.project-info h2 {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  margin: 0;
}

.auto-save {
  font-size: 12px;
  color: #909399;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.export-scope {
  width: 120px;
}

.export-buttons {
  background: white;
  border-radius: 12px;
  padding: 16px 20px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
}

.divider {
  margin: 0 4px;
}

.main-tabs {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
  flex: 1;
}

.tab-content {
  padding: 20px;
}

.empty-tab {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 0;
  color: #9ca3af;
  gap: 12px;
}

.empty-icon {
  color: #c0c4cc;
}

.cases-table {
  margin-bottom: 16px;
}

.pagination {
  display: flex;
  justify-content: flex-end;
}

.status-select {
  width: 100%;
}

.coverage-section {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.coverage-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  flex-wrap: wrap;
  gap: 12px;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.execution-row {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.execution-label {
  font-size: 14px;
  color: #606266;
}

.round-select {
  width: 160px;
}

.new-round-btn {
  padding: 4px 12px;
}

.compare-btn {
  padding: 4px 12px;
}

.execution-hint {
  font-size: 12px;
  color: #909399;
}

.stats-row {
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  border-radius: 8px;
  background: #f5f7fa;
}

.stat-item.pass { color: #67c23a; }
.stat-item.fail { color: #f56c6c; }
.stat-item.blocked { color: #e6a23c; }
.stat-item.pending { color: #909399; }

.stat-value {
  font-size: 14px;
  font-weight: 500;
}

.clean-btn {
  color: #909399;
  padding: 0;
}

.summary-cards {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.summary-card {
  background: #f8fafc;
  border-radius: 12px;
  padding: 20px;
  text-align: center;
}

.card-value {
  font-size: 32px;
  font-weight: 700;
  color: #667eea;
}

.card-label {
  font-size: 14px;
  color: #909399;
  margin-top: 4px;
}

.coverage-progress {
  background: #f8fafc;
  border-radius: 12px;
  padding: 16px 20px;
}

.progress-header {
  margin-bottom: 12px;
}

.progress-title {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
}

.progress-bar-container {
  height: 8px;
  background: #e4e7ed;
  border-radius: 4px;
  overflow: hidden;
}

.progress-bar-fill {
  height: 100%;
  background: linear-gradient(90deg, #67c23a, #85ce61);
  border-radius: 4px;
  transition: width 0.5s;
}

.coverage-chart {
  display: flex;
  gap: 24px;
  align-items: flex-start;
  flex-wrap: wrap;
}

.chart-ring {
  width: 160px;
  height: 160px;
  border-radius: 50%;
  background: conic-gradient(#67c23a 100%, #e4e7ed 0%);
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}

.chart-ring::before {
  content: '';
  position: absolute;
  width: 120px;
  height: 120px;
  border-radius: 50%;
  background: white;
}

.ring-inner {
  position: relative;
  z-index: 1;
  text-align: center;
}

.ring-value {
  font-size: 28px;
  font-weight: 700;
  color: #67c23a;
  display: block;
}

.ring-label {
  font-size: 12px;
  color: #909399;
}

.chart-legend {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #606266;
}

.legend-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
}

.legend-dot.covered { background: #67c23a; }
.legend-dot.uncovered { background: #e4e7ed; }

.chart-bars {
  flex: 1;
  min-width: 300px;
}

.bar-item {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.bar-label {
  width: 140px;
  font-size: 13px;
  color: #606266;
  flex-shrink: 0;
}

.bar-track {
  flex: 1;
  height: 12px;
  background: #e4e7ed;
  border-radius: 6px;
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  background: #67c23a;
  border-radius: 6px;
  transition: width 0.5s;
}

.bar-value {
  width: 60px;
  font-size: 13px;
  color: #606266;
  text-align: right;
  flex-shrink: 0;
}

.type-distribution, .module-cases {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
}

.dist-title {
  font-size: 14px;
  color: #606266;
}

.gap-section {
  background: #fffbe6;
  border-radius: 8px;
  padding: 16px;
  border-left: 4px solid #e6a23c;
}

.gap-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}

.gap-title {
  font-size: 14px;
  font-weight: 500;
  color: #e6a23c;
}

.gap-list {
  margin: 0;
  padding-left: 20px;
}

.gap-list li {
  font-size: 13px;
  color: #8b7355;
  margin-bottom: 4px;
}

.gap-bullet {
  color: #e6a23c;
}

.mindmap-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 0;
  color: #9ca3af;
}

.mindmap-icon {
  color: #c0c4cc;
  margin-bottom: 16px;
}

.mindmap-hint {
  font-size: 14px;
}

.case-category-tabs {
  margin-bottom: 16px;
}

.category-tabs :deep(.el-tabs__item) {
  font-size: 13px;
  padding: 0 16px;
}

.category-tabs :deep(.el-tabs__item.is-active) {
  font-weight: 600;
}

.risk-assessment-section {
  margin-top: 16px;
  padding: 16px;
  background: #f9fafb;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
}

.divider-title {
  font-size: 14px;
  font-weight: 600;
  color: #374151;
}

.risks-list {
  margin-top: 12px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.risk-item {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 8px 12px;
  background: #fff;
  border-radius: 6px;
  border-left: 3px solid #e6a23c;
}

.risk-item:first-child {
  border-left-color: #f56c6c;
}

.risk-desc {
  font-size: 13px;
  color: #606266;
}

.suggestions-list {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px dashed #e5e7eb;
  font-size: 13px;
  color: #606266;
}

.suggestions-label {
  font-weight: 600;
  color: #374151;
}

.ai-output-actions {
  margin-top: 16px;
}

.export-buttons-row {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

@media (max-width: 1200px) {
  .main-container {
    grid-template-columns: 1fr;
  }
  
  .left-panel {
    order: 2;
  }
  
  .right-panel {
    order: 1;
  }
  
  .summary-cards {
    grid-template-columns: repeat(2, 1fr);
  }
}

.swagger-section {
  background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
  border: 1px solid #bae6fd;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 16px;
}

.swagger-section .section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}

.swagger-section .section-label {
  font-size: 14px;
  font-weight: 600;
  color: #0369a1;
}

.swagger-tabs {
  margin-bottom: 12px;
}

.swagger-url,
.swagger-content,
.swagger-file {
  margin-bottom: 12px;
}

.swagger-url-tips {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 8px;
}

.url-example {
  cursor: pointer;
  transition: all 0.2s;
}

.url-example:hover {
  background-color: #e0f2fe;
}

.swagger-url-hint {
  display: flex;
  align-items: center;
  gap: 4px;
  margin-top: 6px;
  font-size: 12px;
  color: #909399;
}

.swagger-url-error {
  display: flex;
  align-items: center;
  gap: 4px;
  margin-top: 6px;
  font-size: 12px;
  color: #f56c6c;
}

.swagger-url-invalid :deep(.el-input__wrapper) {
  box-shadow: 0 0 0 1px #f56c6c inset !important;
}

.swagger-loading-tip {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 10px;
  padding: 8px 12px;
  background-color: #f0f9ff;
  border: 1px solid #bae6fd;
  border-radius: 6px;
  font-size: 13px;
  color: #0284c7;
}

.swagger-loading-tip .el-icon {
  animation: rotate 1s linear infinite;
}

@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.swagger-upload-area {
  border: 2px dashed #bae6fd;
  border-radius: 8px;
  padding: 20px;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s;
}

.swagger-upload-area:hover {
  border-color: #0284c7;
  background-color: #f0f9ff;
}

.swagger-upload-area .upload-icon {
  color: #0284c7;
  margin-bottom: 8px;
}

.swagger-upload-area .upload-title {
  font-size: 14px;
  color: #0369a1;
  margin-bottom: 4px;
}

.swagger-upload-area .upload-hint {
  font-size: 12px;
  color: #64748b;
}

.swagger-file-info {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 8px;
  padding: 8px;
  background-color: #f0fdf4;
  border-radius: 4px;
}

.swagger-file-info .clear-icon {
  cursor: pointer;
  margin-left: auto;
  color: #ef4444;
}

.swagger-generate-btn {
  width: 100%;
  margin-bottom: 12px;
}

.swagger-result {
  background-color: #f0fdf4;
  border: 1px solid #86efac;
  border-radius: 6px;
  padding: 12px;
}

.swagger-result .result-header {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #166534;
  font-size: 14px;
  font-weight: 500;
  margin-bottom: 8px;
}

.swagger-result .result-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
  font-size: 12px;
  color: #475569;
}
</style>