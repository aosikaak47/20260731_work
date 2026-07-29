<template>
  <div class="ui-screenshots">
    <div class="page-header">
      <h2>失败截图记录</h2>
      <p class="page-desc">查看UI自动化失败截图</p>
    </div>

    <el-card>
      <template #header>
        <div class="card-header">
          <span class="card-title">截图列表</span>
          <div class="header-actions">
            <el-select v-model="filterProject" size="small" placeholder="全部项目" clearable class="filter-select">
              <el-option v-for="p in projectOptions" :key="p" :label="p" :value="p" />
            </el-select>
            <el-select v-model="filterCase" size="small" placeholder="全部用例" clearable class="filter-select">
              <el-option v-for="c in caseOptions" :key="c" :label="c" :value="c" />
            </el-select>
            <el-input
              v-model="searchKeyword"
              placeholder="搜索截图..."
              size="small"
              class="search-input"
              @keyup.enter="loadScreenshots"
            >
              <template #prefix>
                <el-icon><component :is="icons.Search" /></el-icon>
              </template>
            </el-input>
            <el-button size="small" type="primary" @click="loadScreenshots">
              <el-icon><component :is="icons.Refresh" /></el-icon>
              <span class="btn-text">刷新</span>
            </el-button>
          </div>
        </div>
      </template>

      <div v-if="loading" class="loading-state">
        <el-icon :size="32" class="is-loading"><component :is="icons.Loading" /></el-icon>
        <span>加载中...</span>
      </div>

      <div v-else-if="filteredScreenshots.length === 0" class="empty-state">
        <el-icon :size="48" class="empty-icon"><component :is="icons.Picture" /></el-icon>
        <span>暂无截图</span>
      </div>

      <div v-else class="screenshots-grid">
        <el-row :gutter="16">
          <el-col
            v-for="item in pagedScreenshots"
            :key="item.id"
            :xs="24" :sm="12" :md="8" :lg="6"
            class="grid-col"
          >
            <el-card shadow="hover" class="screenshot-card" :body-style="{ padding: '0' }">
              <div class="screenshot-thumb" @click="handlePreview(item)">
                <img
                  v-if="item.image_url || item.url || item.path"
                  :src="item.image_url || item.url || item.path"
                  :alt="item.case_name || item.name || 'screenshot'"
                  class="thumb-img"
                  loading="lazy"
                />
                <div v-else class="no-image">
                  <el-icon :size="40"><component :is="icons.Picture" /></el-icon>
                </div>
                <div class="screenshot-overlay">
                  <el-icon :size="28"><component :is="icons.View" /></el-icon>
                </div>
                <div v-if="item.status === 'failed'" class="status-badge failed">失败</div>
                <div v-else class="status-badge success">通过</div>
              </div>
              <div class="screenshot-info">
                <div class="info-title" :title="item.case_name || item.name || '未命名用例'">
                  <el-icon class="info-icon"><component :is="icons.Document" /></el-icon>
                  <span>{{ item.case_name || item.name || '未命名用例' }}</span>
                </div>
                <div class="info-meta">
                  <el-tag v-if="item.project" size="small" type="info">{{ item.project }}</el-tag>
                  <span class="info-time">
                    <el-icon><component :is="icons.Clock" /></el-icon>
                    {{ formatTime(item.created_at || item.createdAt) }}
                  </span>
                </div>
                <div class="info-actions">
                  <el-button size="small" type="primary" link @click="handlePreview(item)">
                    <el-icon><component :is="icons.View" /></el-icon>
                    <span>预览</span>
                  </el-button>
                  <el-button size="small" type="danger" link @click="handleDownload(item)">
                    <el-icon><component :is="icons.Download" /></el-icon>
                    <span>下载</span>
                  </el-button>
                  <el-button size="small" type="danger" link @click="handleDelete(item)">
                    <el-icon><component :is="icons.Delete" /></el-icon>
                    <span>删除</span>
                  </el-button>
                </div>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>

      <el-pagination
        v-if="filteredScreenshots.length > 0"
        class="pagination"
        layout="total, sizes, prev, pager, next, jumper"
        :total="filteredScreenshots.length"
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[12, 24, 48, 96]"
      />
    </el-card>

    <el-dialog
      v-model="previewVisible"
      :title="previewItem ? (previewItem.case_name || previewItem.name || '截图预览') : '截图预览'"
      width="80%"
      top="5vh"
      destroy-on-close
      class="preview-dialog"
    >
      <div class="preview-content" v-if="previewItem">
        <div class="preview-meta">
          <el-descriptions :column="3" border size="small">
            <el-descriptions-item label="所属项目">{{ previewItem.project || '-' }}</el-descriptions-item>
            <el-descriptions-item label="用例名称">{{ previewItem.case_name || previewItem.name || '-' }}</el-descriptions-item>
            <el-descriptions-item label="执行时间">{{ formatTime(previewItem.created_at || previewItem.createdAt) }}</el-descriptions-item>
            <el-descriptions-item label="状态">
              <el-tag :type="previewItem.status === 'failed' ? 'danger' : 'success'" size="small">
                {{ previewItem.status === 'failed' ? '失败' : '通过' }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item v-if="previewItem.step_name" label="步骤">{{ previewItem.step_name }}</el-descriptions-item>
            <el-descriptions-item v-if="previewItem.error_message" label="错误信息" :span="3">
              <span class="error-msg">{{ previewItem.error_message }}</span>
            </el-descriptions-item>
          </el-descriptions>
        </div>
        <div class="preview-image-wrapper">
          <img
            v-if="previewImageUrl"
            :src="previewImageUrl"
            alt="preview"
            class="preview-image"
          />
        </div>
      </div>
      <template #footer>
        <el-button @click="previewVisible = false">关闭</el-button>
        <el-button type="primary" @click="handleDownload(previewItem)">下载</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import * as icons from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const loading = ref(false)
const screenshots = ref([])
const searchKeyword = ref('')
const filterProject = ref('')
const filterCase = ref('')
const currentPage = ref(1)
const pageSize = ref(24)

const previewVisible = ref(false)
const previewItem = ref(null)
const previewImageUrl = ref('')

const projectOptions = computed(() => {
  const set = new Set()
  screenshots.value.forEach(s => s.project && set.add(s.project))
  return Array.from(set)
})

const caseOptions = computed(() => {
  const set = new Set()
  screenshots.value.forEach(s => {
    const name = s.case_name || s.name
    if (name) set.add(name)
  })
  return Array.from(set)
})

const filteredScreenshots = computed(() => {
  let result = screenshots.value
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    result = result.filter(s =>
      (s.case_name || s.name || '').toLowerCase().includes(keyword) ||
      (s.project || '').toLowerCase().includes(keyword)
    )
  }
  if (filterProject.value) {
    result = result.filter(s => s.project === filterProject.value)
  }
  if (filterCase.value) {
    const caseName = filterCase.value
    result = result.filter(s => (s.case_name || s.name) === caseName)
  }
  return result
})

const pagedScreenshots = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  return filteredScreenshots.value.slice(start, start + pageSize.value)
})

const loadScreenshots = async () => {
  loading.value = true
  try {
    const response = await fetch('/api/v1/ui/screenshots')
    const data = await response.json()
    screenshots.value = data.screenshots || data.data || data.items || []
  } catch (error) {
    console.error('加载截图列表失败:', error)
    ElMessage.error('加载截图列表失败')
  } finally {
    loading.value = false
  }
}

const getImageUrl = (item) => item.image_url || item.url || item.path || ''

const handlePreview = (item) => {
  previewItem.value = item
  previewImageUrl.value = getImageUrl(item)
  previewVisible.value = true
}

const handleDownload = async (item) => {
  const url = getImageUrl(item)
  if (!url) {
    ElMessage.warning('图片地址不存在')
    return
  }
  try {
    const response = await fetch(url)
    const blob = await response.blob()
    const blobUrl = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = blobUrl
    a.download = `${item.case_name || item.name || 'screenshot'}_${Date.now()}.png`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    window.URL.revokeObjectURL(blobUrl)
    ElMessage.success('下载成功')
  } catch {
    const a = document.createElement('a')
    a.href = url
    a.download = `${item.case_name || item.name || 'screenshot'}.png`
    a.target = '_blank'
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
  }
}

const handleDelete = async (item) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除用例「${item.case_name || item.name}」的截图吗？删除后不可恢复。`,
      '删除确认',
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
  } catch {
    return
  }

  try {
    const response = await fetch(`/api/v1/ui/screenshots/${item.id}`, {
      method: 'DELETE'
    })
    const data = await response.json()
    if (response.ok && (data.success === undefined || data.success === true)) {
      ElMessage.success('删除成功')
      if (previewVisible.value) previewVisible.value = false
      loadScreenshots()
    } else {
      ElMessage.error(data.message || '删除失败')
    }
  } catch (error) {
    console.error('删除截图失败:', error)
    ElMessage.error('删除失败')
  }
}

const formatTime = (time) => {
  if (!time) return '-'
  if (typeof time === 'string') return time.replace('T', ' ').substring(0, 19)
  return new Date(time).toLocaleString('zh-CN')
}

onMounted(() => {
  loadScreenshots()
})
</script>

<style scoped>
.ui-screenshots { padding: 20px; }

.page-header { margin-bottom: 24px; }
.page-header h2 { font-size: 24px; font-weight: 600; color: #1f2937; margin-bottom: 4px; }
.page-desc { font-size: 14px; color: #6b7280; }

.card-header { display: flex; align-items: center; justify-content: space-between; }
.card-title { font-size: 16px; font-weight: 600; }
.header-actions { display: flex; gap: 12px; align-items: center; }
.filter-select { width: 140px; }
.search-input { width: 220px; }
.btn-text { margin-left: 4px; }

.loading-state {
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  padding: 60px; color: #9ca3af; gap: 12px;
}
.loading-state .is-loading { color: #6366f1; }

.empty-state {
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  padding: 60px; color: #9ca3af; gap: 12px;
}
.empty-icon { color: #c0c4cc; }

.screenshots-grid { margin-top: 8px; }
.grid-col { margin-bottom: 16px; }

.screenshot-card {
  overflow: hidden;
  transition: transform 0.2s, box-shadow 0.2s;
}
.screenshot-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

.screenshot-thumb {
  position: relative;
  width: 100%;
  height: 180px;
  background-color: #f3f4f6;
  overflow: hidden;
  cursor: zoom-in;
  display: flex;
  align-items: center;
  justify-content: center;
}
.thumb-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}
.screenshot-card:hover .thumb-img { transform: scale(1.05); }

.no-image {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
  color: #9ca3af;
  background: linear-gradient(135deg, #f3f4f6, #e5e7eb);
}

.screenshot-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.45);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  opacity: 0;
  transition: opacity 0.2s;
}
.screenshot-thumb:hover .screenshot-overlay { opacity: 1; }

.status-badge {
  position: absolute;
  top: 8px;
  right: 8px;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
  color: #fff;
}
.status-badge.failed { background-color: #ef4444; }
.status-badge.success { background-color: #10b981; }

.screenshot-info { padding: 12px; }
.info-title {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  font-weight: 500;
  color: #1f2937;
  margin-bottom: 8px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.info-title .info-icon { color: #6366f1; font-size: 14px; flex-shrink: 0; }
.info-title span {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.info-meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
  gap: 8px;
}
.info-time {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #6b7280;
}

.info-actions {
  display: flex;
  justify-content: space-between;
  border-top: 1px solid #f3f4f6;
  padding-top: 8px;
}
.info-actions .el-button { padding: 4px 8px; }
.info-actions .el-button span { margin-left: 2px; }

.pagination { display: flex; justify-content: flex-end; margin-top: 16px; }

.preview-content { padding: 0; }
.preview-meta { margin-bottom: 16px; }
.error-msg { color: #ef4444; word-break: break-all; }

.preview-image-wrapper {
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #f9fafb;
  border-radius: 8px;
  padding: 16px;
  max-height: 70vh;
  overflow: auto;
}
.preview-image {
  max-width: 100%;
  height: auto;
  border-radius: 4px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}
</style>
