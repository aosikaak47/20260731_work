import urllib.request
import json

print("=== 测试录制脚本生成 ===\n")

# 模拟录制的操作
test_actions = [
    {"type": "navigate", "url": "https://www.baidu.com"},
    {"type": "input", "selector": "#kw", "value": "Playwright自动化测试", "text": "搜索框"},
    {"type": "click", "selector": "#su", "text": "百度一下"},
]

# 调用停止录制API生成脚本
url = 'http://127.0.0.1:8000/api/v1/ui/record/stop'
data = json.dumps({
    'session_id': 'test-session',
    'case_name': '百度搜索测试',
    'url': 'https://www.baidu.com',
    'actions': test_actions
}).encode()

req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})

try:
    resp = urllib.request.urlopen(req, timeout=10)
    result = json.loads(resp.read().decode())
    if result.get('success'):
        script = result.get('script', '')
        print('✓ 录制脚本生成成功！')
        
        # 检查关键特性
        checks = [
            ('slow_mo', 'slow_mo 参数'),
            ('STEP_DELAY', 'STEP_DELAY 配置'),
            ('wait_for_timeout(STEP_DELAY)', '操作间隔等待'),
            ('viewport', '视口设置'),
            ('try:', '异常处理'),
            ('except Exception', '异常捕获'),
        ]
        
        print('\n关键特性检查:')
        for keyword, desc in checks:
            if keyword in script:
                print(f'  ✓ {desc}')
            else:
                print(f'  ✗ {desc}')
        
        print('\n脚本完整内容:')
        print(script)
        
        # 保存脚本到文件
        with open('e:\\trae_work\\autoProject\\backend\\test_recorded_script.py', 'w', encoding='utf-8') as f:
            f.write(script)
        print('\n脚本已保存到: e:\\trae_work\\autoProject\\backend\\test_recorded_script.py')
    else:
        print(f'✗ 生成失败: {result.get("detail")}')
except Exception as e:
    print(f'✗ 请求失败: {e}')

print('\n=== 测试完成 ===')