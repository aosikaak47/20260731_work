<template>
  <div class="app-layout">
    <el-container class="layout-container">
      <el-aside :width="sidebarCollapsed ? '64px' : '220px'" class="sidebar">
        <Sidebar @toggle="sidebarCollapsed = !sidebarCollapsed" :collapsed="sidebarCollapsed" />
      </el-aside>
      <el-container class="main-container">
        <el-header class="header">
          <Header />
        </el-header>
        <el-main class="main-content">
          <router-view v-slot="{ Component }">
            <transition name="fade" mode="out-in">
              <component :is="Component" />
            </transition>
          </router-view>
        </el-main>
        <el-footer class="footer">
          <Footer />
        </el-footer>
      </el-container>
    </el-container>
    <AiAssistant />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import Sidebar from './Sidebar.vue'
import Header from './Header.vue'
import Footer from './Footer.vue'
import AiAssistant from './AiAssistant.vue'

const sidebarCollapsed = ref(false)
</script>

<style scoped>
.app-layout {
  min-height: 100vh;
  background-color: var(--color-bg-page);
}

.layout-container {
  height: 100vh;
}

.sidebar {
  background-color: var(--color-bg-sidebar);
  transition: width 0.3s ease;
  overflow: hidden;
  border-right: 1px solid var(--color-border);
}

.main-container {
  flex: 1;
  background-color: var(--color-bg-page);
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.header {
  padding: 0;
  border-bottom: 1px solid var(--color-border);
  background-color: var(--color-bg-card);
  height: var(--layout-header-height);
  line-height: var(--layout-header-height);
  flex-shrink: 0;
}

.main-content {
  padding: var(--layout-content-padding);
  overflow-y: auto;
  flex: 1;
  min-height: 0;
  scrollbar-width: thin;
  scrollbar-color: var(--color-text-tertiary) transparent;
  height: 0;
}

.main-content::-webkit-scrollbar {
  width: 6px;
}

.main-content::-webkit-scrollbar-track {
  background: transparent;
}

.main-content::-webkit-scrollbar-thumb {
  background: var(--color-text-tertiary);
  border-radius: 3px;
}

.main-content::-webkit-scrollbar-thumb:hover {
  background: var(--color-text-secondary);
}

.footer {
  padding: 12px var(--layout-content-padding);
  text-align: center;
  background-color: var(--color-bg-card);
  border-top: 1px solid var(--color-border);
  height: var(--layout-footer-height);
  line-height: 24px;
  font-size: var(--font-size-xs);
  color: var(--color-text-tertiary);
  flex-shrink: 0;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
