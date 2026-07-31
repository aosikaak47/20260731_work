import os
import json
import uuid
import sys

# 模拟新的脚本生成逻辑
RECORD_INJECT_SCRIPT = '''
(function() {
    window.__recordedActions = [];
    document.addEventListener('click', function(e) {
        var action = { type: 'click', selector: 'test' };
        console.log('__RECORD_ACTION__:' + JSON.stringify(action));
    }, true);
})();
'''

session_id = str(uuid.uuid4())
url = "https://www.baidu.com"
headless = False

scripts_dir = os.path.join(os.path.dirname(__file__), "config", "ui_scripts")
os.makedirs(scripts_dir, exist_ok=True)

record_file = os.path.join(scripts_dir, f"record_{session_id}.json")

# 直接构建脚本内容
inject_script_str = repr(RECORD_INJECT_SCRIPT)

lines = [
    '#!/usr/bin/env python3',
    '# -*- coding: utf-8 -*-',
    'import asyncio',
    'import json',
    'import sys',
    'import os',
    '',
    'record_file = ' + repr(record_file),
    'target_url = ' + repr(url),
    'headless_mode = ' + str(headless),
    '',
    '# 录制注入脚本',
    'INJECT_SCRIPT = ' + inject_script_str,
    '',
    'def save_actions(actions, status="recording"):',
    '    try:',
    '        data = dict(actions=actions, status=status, count=len(actions))',
    '        with open(record_file, "w", encoding="utf-8") as f:',
    '            json.dump(data, f, ensure_ascii=False)',
    '    except Exception as e:',
    '        print("Save error: %s" % e, flush=True)',
    '',
    'async def main():',
    '    try:',
    '        from playwright.async_api import async_playwright',
    '        ',
    '        print("[Recorder] Starting browser, url=%s" % target_url, flush=True)',
    '        save_actions([], "starting")',
    '        ',
    '        async with async_playwright() as p:',
    '            browser = await p.chromium.launch(headless=headless_mode)',
    '            context = await browser.new_context()',
    '            page = await context.new_page()',
    '            ',
    '            print("[Recorder] Browser launched, navigating to %s" % target_url, flush=True)',
    '            ',
    '            # 注入录制脚本',
    '            await page.add_init_script(INJECT_SCRIPT)',
    '            ',
    '            recorded_actions = []',
    '            ',
    '            def on_console(msg):',
    '                try:',
    '                    if msg.text.startswith("__RECORD_ACTION__:"):',
    '                        action_data = msg.text.replace("__RECORD_ACTION__:", "")',
    '                        action = json.loads(action_data)',
    '                        recorded_actions.append(action)',
    '                        save_actions(recorded_actions, "recording")',
    '                        print("[Recorder] Captured action: %s - %s" % (action.get("type", ""), action.get("selector", action.get("url", ""))), flush=True)',
    '                except Exception as e:',
    '                    print("[Recorder] Console error: %s" % e, flush=True)',
    '            ',
    '            page.on("console", on_console)',
    '            ',
    '            # 导航到目标URL',
    '            await page.goto(target_url, wait_until="domcontentloaded")',
    '            print("[Recorder] Page loaded, waiting for user actions...", flush=True)',
    '            save_actions(recorded_actions, "recording")',
    '            ',
    '            # 等待用户操作或浏览器关闭',
    '            try:',
    '                # 定期保存状态',
    '                async def heartbeat():',
    '                    while True:',
    '                        await asyncio.sleep(1)',
    '                        save_actions(recorded_actions, "recording")',
    '                ',
    '                heartbeat_task = asyncio.create_task(heartbeat())',
    '                ',
    '                # 等待浏览器关闭或超时',
    '                try:',
    '                    await page.wait_for_event("close", timeout=3600000)',
    '                except asyncio.TimeoutError:',
    '                    print("[Recorder] Timeout, closing browser", flush=True)',
    '                ',
    '                heartbeat_task.cancel()',
    '                ',
    '            except Exception as e:',
    '                print("[Recorder] Wait error: %s" % e, flush=True)',
    '            ',
    '            save_actions(recorded_actions, "completed")',
    '            print("[Recorder] Session ended. Total actions: %d" % len(recorded_actions), flush=True)',
    '            await browser.close()',
    '            ',
    '    except Exception as e:',
    '        print("[Recorder] Error: %s" % e, flush=True)',
    '        try:',
    '            save_actions([], "error: %s" % e)',
    '        except:',
    '            pass',
    '',
    'if __name__ == "__main__":',
    '    asyncio.run(main())',
    ''
]

script_content = '\n'.join(lines)

# 写入文件检查
test_script_path = os.path.join(scripts_dir, "test_new_generated.py")
with open(test_script_path, 'w', encoding='utf-8') as f:
    f.write(script_content)

print("Generated script written to:", test_script_path)

# 验证语法
import py_compile
try:
    py_compile.compile(test_script_path, doraise=True)
    print("Syntax check: PASSED!")
except py_compile.PyCompileError as e:
    print(f"Syntax check: FAILED - {e}")

# 检查是否有双花括号
if '{{' in script_content:
    print("WARNING: Double braces '{{' found!")
else:
    print("No double braces found - OK!")

if '}}' in script_content:
    print("WARNING: Double braces '}}' found!")
else:
    print("No double braces found - OK!")

# 显示前30行
print("\nFirst 30 lines of generated script:")
for i, line in enumerate(script_content.split('\n')[:30]):
    print(f"{i+1}: {line}")