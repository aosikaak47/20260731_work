<template>
  <div class="ui-elements">
    <div class="page-header">
      <h2>页面元素管理</h2>
      <p class="page-desc">基于PO模式管理页面元素</p>
    </div>
    
    <el-card>
      <template #header>
        <div class="card-header">
          <span class="card-title">页面元素列表</span>
          <el-button type="primary" @click="handleAdd">
            <el-icon><component :is="icons.Plus" /></el-icon>
            新增元素
          </el-button>
        </div>
      </template>
      
      <div class="filter-bar">
        <el-select v-model="filterPage" size="small" placeholder="页面">
          <el-option label="全部" value="" />
          <el-option v-for="page in pages" :key="page.id" :label="page.name" :value="page.id" />
        </el-select>
        <el-select v-model="filterLocator" size="small" placeholder="定位方式">
          <el-option label="全部" value="" />
          <el-option label="XPath" value="xpath" />
          <el-option label="CSS" value="css" />
          <el-option label="ID" value="id" />
        </el-select>
        <el-input 
          v-model="searchKeyword" 
          placeholder="搜索元素名称..." 
          prefix-icon="Search"
          size="small"
          class="search-input"
        />
      </div>
      
      <el-table :data="elements" stripe border>
        <el-table-column type="selection" width="50" />
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="name" label="元素名称" width="120" />
        <el-table-column prop="locatorType" label="定位方式" width="100">
          <template #default="scope">
            <el-tag size="small">{{ scope.row.locatorType }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="locatorExpression" label="定位表达式" min-width="200" />
        <el-table-column prop="pageName" label="所属页面" width="120" />
        <el-table-column prop="status" label="状态" width="80">
          <template #default="scope">
            <el-tag :type="scope.row.status === '有效' ? 'success' : 'warning'">{{ scope.row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" class-name="action-cell">
          <template #default="scope">
            <div class="action-btns">
              <el-button size="small" @click="handleValidate(scope.row)">校验</el-button>
              <el-button size="small" @click="handleEdit(scope.row)">编辑</el-button>
              <el-button size="small" type="danger" @click="handleDelete(scope.row)">删除</el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>
      
      <el-pagination
        class="pagination"
        layout="total, prev, pager, next"
        :total="elements.length"
        :page-size="10"
      />
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import * as icons from '@element-plus/icons-vue'

const searchKeyword = ref('')
const filterPage = ref('')
const filterLocator = ref('')

const pages = [
  { id: 1, name: '登录页面' },
  { id: 2, name: '首页工作台' },
  { id: 3, name: '用例管理页面' },
  { id: 4, name: '接口自动化页面' }
]

const elements = ref([
  { id: 1, name: '用户名输入框', locatorType: 'XPath', locatorExpression: '//input[@name="username"]', pageName: '登录页面', status: '有效' },
  { id: 2, name: '密码输入框', locatorType: 'XPath', locatorExpression: '//input[@name="password"]', pageName: '登录页面', status: '有效' },
  { id: 3, name: '登录按钮', locatorType: 'CSS', locatorExpression: 'button.login-btn', pageName: '登录页面', status: '有效' },
  { id: 4, name: '验证码输入框', locatorType: 'ID', locatorExpression: 'captcha', pageName: '登录页面', status: '有效' },
  { id: 5, name: '数据卡片', locatorType: 'XPath', locatorExpression: '//div[@class="stat-card"]', pageName: '首页工作台', status: '有效' },
  { id: 6, name: '搜索框', locatorType: 'CSS', locatorExpression: 'input.search-input', pageName: '用例管理页面', status: '有效' },
  { id: 7, name: '新增按钮', locatorType: 'XPath', locatorExpression: '//button[contains(text(),"新增")]', pageName: '用例管理页面', status: '有效' },
  { id: 8, name: '接口列表', locatorType: 'CSS', locatorExpression: 'table.api-table', pageName: '接口自动化页面', status: '无效' }
])

const handleAdd = () => {
  alert('新增元素')
}

const handleValidate = (row) => {
  alert(`校验元素: ${row.name}`)
}

const handleEdit = (row) => {
  alert(`编辑元素: ${row.name}`)
}

const handleDelete = (row) => {
  elements.value = elements.value.filter(item => item.id !== row.id)
}
</script>

<style scoped>
.ui-elements {
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

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.card-title {
  font-size: 16px;
  font-weight: 600;
}

.filter-bar {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
}

.search-input {
  width: 200px;
}

.pagination {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}
</style>