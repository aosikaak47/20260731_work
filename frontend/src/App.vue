<template>
  <AppLayout />
</template>

<script setup>
import AppLayout from './components/layout/AppLayout.vue'
</script>

<style>
:root {
  --theme-primary: #008866;
  --theme-primary-light: #E6F5F1;
  --theme-primary-dark: #00664d;

  --color-bg-page: #F8FAFC;
  --color-bg-card: #FFFFFF;
  --color-bg-hover: #F9FAFB;
  --color-bg-row-hover: #F9FAFB;
  --color-bg-header: #F9FAFB;
  --color-bg-sidebar: #1F2937;
  --color-bg-sidebar-hover: #374151;

  --color-border: #E5E7EB;
  --color-border-light: #F3F4F6;
  --color-divider: #F3F4F6;

  --color-text-primary: #1F2937;
  --color-text-secondary: #6B7280;
  --color-text-tertiary: #9CA3AF;
  --color-text-inverse: #FFFFFF;

  --color-success: #10B981;
  --color-warning: #F59E0B;
  --color-danger: #EF4444;
  --color-info: #3B82F6;

  --shadow-card: 0 1px 3px rgba(0, 0, 0, 0.04);
  --shadow-card-hover: 0 2px 8px rgba(0, 0, 0, 0.08);
  --shadow-dropdown: 0 4px 16px rgba(0, 0, 0, 0.12);

  --radius-sm: 4px;
  --radius-md: 6px;
  --radius-lg: 8px;
  --radius-xl: 12px;

  --font-size-xs: 12px;
  --font-size-sm: 14px;
  --font-size-base: 16px;
  --font-size-lg: 20px;
  --font-size-xl: 24px;

  --font-weight-normal: 400;
  --font-weight-medium: 500;
  --font-weight-semibold: 600;

  --spacing-1: 4px;
  --spacing-2: 8px;
  --spacing-3: 12px;
  --spacing-4: 16px;
  --spacing-5: 24px;
  --spacing-6: 32px;

  --layout-header-height: 56px;
  --layout-footer-height: 48px;
  --layout-sidebar-width: 220px;
  --layout-sidebar-collapsed: 64px;
  --layout-content-padding: 24px;
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html {
  font-family: 'Source Han Sans CN', 'Noto Sans SC', -apple-system, BlinkMacSystemFont,
    'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: var(--color-text-primary);
  background-color: var(--color-bg-page);
}

body {
  font-family: inherit;
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-normal);
  line-height: 1.6;
  color: var(--color-text-primary);
  background-color: var(--color-bg-page);
}

#app {
  min-height: 100vh;
}

.el-card {
  border: 1px solid var(--color-border-light) !important;
  border-radius: var(--radius-lg) !important;
  box-shadow: var(--shadow-card) !important;
  transition: box-shadow 0.2s ease !important;
}

.el-card:hover {
  box-shadow: var(--shadow-card-hover) !important;
}

.el-card__header {
  padding: var(--spacing-4) var(--spacing-4) !important;
  border-bottom: 1px solid var(--color-divider) !important;
  font-weight: var(--font-weight-medium) !important;
  font-size: var(--font-size-base) !important;
  color: var(--color-text-primary) !important;
}

.el-card__body {
  padding: var(--spacing-4) !important;
}

.el-button {
  height: 36px !important;
  border-radius: var(--radius-md) !important;
  font-weight: var(--font-weight-medium) !important;
  font-size: var(--font-size-sm) !important;
  transition: all 0.2s ease !important;
}

.el-button--primary {
  background-color: var(--theme-primary) !important;
  border-color: var(--theme-primary) !important;
}

.el-button--primary:hover {
  background-color: var(--theme-primary-dark) !important;
  border-color: var(--theme-primary-dark) !important;
}

.el-button--success {
  background-color: var(--color-success) !important;
  border-color: var(--color-success) !important;
}

.el-button--warning {
  background-color: var(--color-warning) !important;
  border-color: var(--color-warning) !important;
}

.el-button--danger {
  background-color: var(--color-danger) !important;
  border-color: var(--color-danger) !important;
}

.el-button.is-text,
.el-button.is-link {
  height: auto !important;
}

.el-input__wrapper,
.el-select__wrapper {
  min-height: 36px !important;
  border-radius: var(--radius-md) !important;
  box-shadow: 0 0 0 1px var(--color-border) inset !important;
  transition: box-shadow 0.2s ease !important;
}

.el-input__wrapper:hover,
.el-select__wrapper:hover {
  box-shadow: 0 0 0 1px var(--color-text-tertiary) inset !important;
}

.el-input__wrapper.is-focus,
.el-select__wrapper.is-focus {
  box-shadow: 0 0 0 2px var(--theme-primary) inset !important;
}

.el-table {
  border-radius: var(--radius-lg) !important;
  overflow: hidden !important;
}

.el-table th.el-table__cell {
  background-color: var(--color-bg-header) !important;
  color: var(--color-text-primary) !important;
  font-weight: var(--font-weight-medium) !important;
  font-size: var(--font-size-sm) !important;
  padding: 12px 16px !important;
  border-bottom: 1px solid var(--color-border) !important;
  white-space: nowrap !important;
  overflow: visible !important;
  text-overflow: clip !important;
}

.el-table th.el-table__cell .cell {
  white-space: nowrap !important;
  overflow: visible !important;
  text-overflow: clip !important;
}

.el-table td.el-table__cell {
  padding: 12px 16px !important;
  font-size: var(--font-size-sm) !important;
  color: var(--color-text-primary) !important;
  border-bottom: 1px solid var(--color-divider) !important;
}

.el-table td.el-table__cell .cell {
  white-space: nowrap !important;
}

.el-table .cell {
  white-space: nowrap !important;
  overflow: hidden;
  text-overflow: ellipsis;
}

.el-table .action-cell,
.el-table .action-cell .cell {
  overflow: visible !important;
  white-space: normal !important;
  text-overflow: unset !important;
}

.el-table .action-btns {
  display: flex !important;
  align-items: center !important;
  gap: 6px !important;
  flex-wrap: wrap !important;
  white-space: normal !important;
}

.el-table .action-btns .el-button {
  height: 28px !important;
  padding: 0 8px !important;
  font-size: 12px !important;
  border-radius: var(--radius-sm) !important;
  flex-shrink: 0 !important;
  margin: 2px 0 !important;
}

.el-table .action-btns .el-button.is-text,
.el-table .action-btns .el-button.is-link {
  height: auto !important;
  padding: 0 4px !important;
  font-size: 12px !important;
}

.el-table .index-cell {
  width: 50px;
  text-align: center;
}

.el-table .index-cell .index-badge {
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

.el-table .action-cell .cell {
  overflow: visible !important;
  white-space: normal !important;
}

.el-table .action-cell .action-btns {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
  align-items: center;
  white-space: normal;
}

.el-table .action-cell .el-button.is-text {
  font-size: 12px !important;
  padding: 0 4px !important;
}

.el-table .action-cell .el-button.is-text + .el-button.is-text::before {
  content: '|';
  color: var(--color-border);
  margin-right: 6px;
}

.el-table .action-cell .el-button.is-text:last-child::before {
  display: none;
}

.el-table .cell .cell-inner {
  display: flex;
  align-items: center;
  gap: 8px;
}

.el-table--enable-row-hover .el-table__body tr:hover > td.el-table__cell {
  background-color: var(--color-bg-row-hover) !important;
}

.el-table--striped .el-table__body tr.el-table__row--striped td.el-table__cell {
  background-color: #FAFBFC !important;
}

.el-tag {
  border-radius: var(--radius-sm) !important;
  font-size: var(--font-size-xs) !important;
  padding: 2px 8px !important;
  font-weight: var(--font-weight-medium) !important;
  border: none !important;
}

.el-pagination {
  padding: 16px 0 4px !important;
  justify-content: flex-end !important;
}

.el-pagination button,
.el-pagination .el-pager li {
  min-width: 32px !important;
  height: 32px !important;
  border-radius: var(--radius-md) !important;
  font-size: var(--font-size-sm) !important;
}

.el-pagination button:hover,
.el-pagination .el-pager li:hover {
  color: var(--theme-primary) !important;
}

.el-pagination .el-pager li.is-active {
  background-color: var(--theme-primary) !important;
  color: var(--color-text-inverse) !important;
}

.el-dialog {
  border-radius: var(--radius-lg) !important;
  overflow: hidden !important;
}

.el-dialog__header {
  padding: var(--spacing-5) var(--spacing-5) var(--spacing-2) !important;
  border-bottom: 1px solid var(--color-divider) !important;
  margin: 0 !important;
}

.el-dialog__title {
  font-size: var(--font-size-xl) !important;
  font-weight: var(--font-weight-semibold) !important;
  color: var(--color-text-primary) !important;
}

.el-dialog__body {
  padding: var(--spacing-5) !important;
}

.el-dialog__footer {
  padding: var(--spacing-4) var(--spacing-5) var(--spacing-5) !important;
  border-top: 1px solid var(--color-divider) !important;
}

.el-form-item__label {
  font-weight: var(--font-weight-medium) !important;
  color: var(--color-text-primary) !important;
  font-size: var(--font-size-sm) !important;
}

.el-radio__label,
.el-checkbox__label {
  font-size: var(--font-size-sm) !important;
  color: var(--color-text-primary) !important;
}

.el-tabs__item {
  font-size: var(--font-size-sm) !important;
  font-weight: var(--font-weight-medium) !important;
}

.el-tabs__item.is-active {
  color: var(--theme-primary) !important;
}

.el-tabs__active-bar {
  background-color: var(--theme-primary) !important;
}

.el-divider {
  border-color: var(--color-divider) !important;
}

.el-badge__content {
  background-color: var(--color-danger) !important;
}

.el-dropdown-menu {
  border-radius: var(--radius-md) !important;
  box-shadow: var(--shadow-dropdown) !important;
  border: 1px solid var(--color-border-light) !important;
  padding: 4px !important;
}

.el-dropdown-menu__item {
  border-radius: var(--radius-sm) !important;
  padding: 8px 12px !important;
  font-size: var(--font-size-sm) !important;
  color: var(--color-text-primary) !important;
}

.el-dropdown-menu__item:hover {
  background-color: var(--theme-primary-light) !important;
  color: var(--theme-primary) !important;
}

.el-timeline-item__node {
  background-color: var(--theme-primary) !important;
}

.el-switch.is-checked .el-switch__core {
  background-color: var(--theme-primary) !important;
  border-color: var(--theme-primary) !important;
}

.el-progress-bar__inner {
  background-color: var(--theme-primary) !important;
}

.el-input,
.el-select,
.el-date-editor {
  --el-component-size: 36px !important;
}

.el-input__wrapper,
.el-select__wrapper,
.el-date-editor .el-input__wrapper {
  height: 36px !important;
  min-height: 36px !important;
}

.el-input__inner {
  height: 32px !important;
  line-height: 32px !important;
}

.el-form-item {
  margin-bottom: var(--spacing-4) !important;
}

.el-form-item--inline {
  margin-right: var(--spacing-5) !important;
  margin-bottom: 0 !important;
}

.el-checkbox {
  margin-right: var(--spacing-4) !important;
}

.el-radio {
  margin-right: var(--spacing-4) !important;
}

.el-loading-mask {
  background-color: rgba(255, 255, 255, 0.85) !important;
}

.el-message {
  border-radius: var(--radius-md) !important;
  box-shadow: var(--shadow-dropdown) !important;
}

.el-empty__description p {
  font-size: var(--font-size-sm) !important;
  color: var(--color-text-tertiary) !important;
}

::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

::-webkit-scrollbar-track {
  background: transparent;
}

::-webkit-scrollbar-thumb {
  background: var(--color-border);
  border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
  background: var(--color-text-tertiary);
}

.dark-mode {
  --color-bg-page: #1a1a2e;
  --color-bg-card: #27272a;
  --color-bg-hover: #3f3f46;
  --color-bg-row-hover: #2d2d35;
  --color-bg-header: #3f3f46;
  --color-bg-sidebar: #111827;
  --color-border: #3f3f46;
  --color-border-light: #2d2d35;
  --color-divider: #3f3f46;
  --color-text-primary: #e4e4e7;
  --color-text-secondary: #a1a1aa;
  --color-text-tertiary: #71717a;
  --color-bg-header: #2d2d35;
}

.dark-mode .el-table--striped .el-table__body tr.el-table__row--striped td.el-table__cell {
  background-color: #2d2d35 !important;
}

.dark-mode .el-table--enable-row-hover .el-table__body tr:hover > td.el-table__cell {
  background-color: #3f3f46 !important;
}
</style>
