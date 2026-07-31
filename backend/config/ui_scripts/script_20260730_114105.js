// Playwright 自动化测试脚本
// 用例名称: 点进进入教师档案袋
// 生成时间: 2026-07-30 11:41:04

const { chromium } = require('playwright');

test('点进进入教师档案袋', async () => {
  const browser = await chromium.launch({ headless: false });
  const context = await browser.newContext();
  const page = await context.newPage();

  // 打开目标页面
  await page.goto('http://192.168.100.61:7275/#/globalView');

  await browser.close();
});