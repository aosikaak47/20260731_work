import urllib.request
import json

print("=== 测试脚本生成 ===\n")

# 使用完整的用例数据测试
test_case = {
    "id": "test-1",
    "name": "百度搜索测试",
    "url": "https://www.baidu.com",
    "steps": [
        {"type": "navigate", "name": "打开百度", "params": {"url": "https://www.baidu.com"}},
        {"type": "input", "name": "搜索框输入", "element": "搜索框", "params": {"value": "Playwright"}},
        {"type": "click", "name": "点击搜索按钮", "element": "搜索按钮", "params": {}},
        {"type": "captcha", "name": "输入验证码", "params": {"input_selector": "input.captcha-input"}}
    ]
}

url = 'http://127.0.0.1:8000/api/v1/ui/playwright/generate'
data = json.dumps({
    "case": test_case
}).encode()

req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})

try:
    resp = urllib.request.urlopen(req, timeout=10)
    result = json.loads(resp.read().decode())
    if result.get('success'):
        script = result.get('script', '')
        print('✓ 脚本生成成功！')
        
        # 检查关键特性
        checks = [
            ('slow_mo', 'slow_mo 参数'),
            ('STEP_DELAY', 'STEP_DELAY 配置'),
            ('wait_for_timeout(STEP_DELAY)', '操作间隔等待'),
            ('wait_for_captcha_input', '验证码等待函数'),
            ('SESSION_ID', '验证码会话ID'),
            ('viewport', '视口设置'),
            ('captcha', '验证码步骤')
        ]
        
        print('\n关键特性检查:')
        for keyword, desc in checks:
            if keyword in script:
                print(f'  ✓ {desc}')
            else:
                print(f'  ✗ {desc}')
        
        print('\n脚本完整内容:')
        print(script)
    else:
        print(f'✗ 生成失败: {result.get("detail")}')
except Exception as e:
    print(f'✗ 请求失败: {e}')

print('\n=== 测试完成 ===')