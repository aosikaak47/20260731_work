<template>
  <div class="footer-wrapper">
    <span class="copyright">© 2026 智能自动化测试平台</span>
    <span class="version-info">v2.0.0</span>
  </div>
</template>

<script setup>
</script>

<style scoped>
.footer-wrapper {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: var(--font-size-xs);
  color: var(--color-text-tertiary);
}

.copyright {
  font-weight: var(--font-weight-medium);
}

.version-info {
  color: var(--color-text-tertiary);
}
</style>
