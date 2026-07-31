// Playwright 自动化测试脚本
// 用例名称: 登录功能测试
// 生成时间: 2026-07-30 11:44:57

const { chromium } = require('playwright');

test('登录功能测试', async () => {
  const browser = await chromium.launch({ headless: false });
  const context = await browser.newContext();
  const page = await context.newPage();

  // 打开目标页面
  await page.goto('http://localhost:5173/login');

  // 打开登录页
  await page.goto('http://localhost:5173/login');

  // 输入用户名
  await page.locator('//input[@name='username']').fill('admin');

  // 输入密码
  await page.locator('//input[@name='password']').fill('123456');

  // 点击登录
  await page.locator('button.login-btn').click();

  // 验证登录成功
  await expect(page.getByText('首页工作台')).toBeVisible();

  await browser.close();
});