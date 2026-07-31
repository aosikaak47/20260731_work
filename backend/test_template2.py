import os
import json
import uuid

RECORD_INJECT_SCRIPT = '''
(function() {
    window.__recordedActions = [];
    window.__recordActive = true;

    function getElementSelector(element) {
        if (element.id) return '#' + element.id;
        if (element.name) return element.tagName.toLowerCase() + '[name="' + element.name + '"]';
        var path = [];
        var current = element;
        while (current && current.nodeType === 1 && path.length < 5) {
            var selector = current.tagName.toLowerCase();
            if (current.id) { selector += '#' + current.id; path.unshift(selector); break; }
            var parent = current.parentNode;
            if (parent) {
                var siblings = Array.from(parent.children).filter(function(c) { return c.tagName === current.tagName; });
                if (siblings.length > 1) {
                    var index = siblings.indexOf(current) + 1;
                    selector += ':nth-of-type(' + index + ')';
                }
                path.unshift(selector);
            }
            current = current.parentNode;
        }
        return path.join(' > ');
    }

    function sendAction(action) {
        action.timestamp = Date.now();
        window.__recordedActions.push(action);
        console.log('__RECORD_ACTION__:' + JSON.stringify(action));
    }

    document.addEventListener('click', function(e) {
        if (!window.__recordActive) return;
        var action = { type: 'click', selector: 'test', elementType: 'button', text: 'Click Me', tagName: 'button' };
        sendAction(action);
    }, true);

    console.log('[UI Recorder] Recording started.');
})();
'''

template = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import asyncio
import json
import sys
import os

record_file = r"__RECORD_FILE__"
target_url = r"__TARGET_URL__"
headless_mode = __HEADLESS__

# 录制注入脚本
INJECT_SCRIPT = __INJECT_SCRIPT__

def save_actions(actions, status="recording"):
    try:
        data = {"actions": actions, "status": status, "count": len(actions)}
        with open(record_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False)
    except Exception as e:
        print(f"Save error: {e}", flush=True)

async def main():
    try:
        from playwright.async_api import async_playwright
        
        print(f"[Recorder] Starting browser, url={target_url}", flush=True)
        save_actions([], "starting")
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=headless_mode)
            context = await browser.new_context()
            page = await context.new_page()
            
            print(f"[Recorder] Browser launched, navigating to {target_url}", flush=True)
            
            # 注入录制脚本
            await page.add_init_script(INJECT_SCRIPT)
            
            recorded_actions = []
            
            def on_console(msg):
                try:
                    if msg.text.startswith('__RECORD_ACTION__:'):
                        action_data = msg.text.replace('__RECORD_ACTION__:', '')
                        action = json.loads(action_data)
                        recorded_actions.append(action)
                        save_actions(recorded_actions, "recording")
                        print(f"[Recorder] Captured action: {action.get('type', '')} - {action.get('selector', action.get('url', ''))}", flush=True)
                except Exception as e:
                    print(f"[Recorder] Console error: {e}", flush=True)
            
            page.on("console", on_console)
            
            # 导航到目标URL
            await page.goto(target_url, wait_until="domcontentloaded")
            print("[Recorder] Page loaded, waiting for user actions...", flush=True)
            save_actions(recorded_actions, "recording")
            
            # 等待用户操作或浏览器关闭
            try:
                # 定期保存状态
                async def heartbeat():
                    while True:
                        await asyncio.sleep(1)
                        save_actions(recorded_actions, "recording")
                
                heartbeat_task = asyncio.create_task(heartbeat())
                
                # 等待浏览器关闭或超时
                try:
                    await page.wait_for_event("close", timeout=3600000)
                except asyncio.TimeoutError:
                    print("[Recorder] Timeout, closing browser", flush=True)
                
                heartbeat_task.cancel()
                
            except Exception as e:
                print(f"[Recorder] Wait error: {e}", flush=True)
            
            save_actions(recorded_actions, "completed")
            print(f"[Recorder] Session ended. Total actions: {len(recorded_actions)}", flush=True)
            await browser.close()
            
    except Exception as e:
        print(f"[Recorder] Error: {e}", flush=True)
        try:
            save_actions([], f"error: {e}")
        except:
            pass

if __name__ == "__main__":
    asyncio.run(main())
'''

# 模拟后端的替换过程
session_id = str(uuid.uuid4())
url = "https://www.baidu.com"
headless = False

scripts_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config", "ui_scripts")
os.makedirs(scripts_dir, exist_ok=True)

record_file = os.path.join(scripts_dir, f"record_{session_id}.json")

# 执行替换
inject_script_repr = repr(RECORD_INJECT_SCRIPT)
print("Step 1 - inject_script_repr contains:")
print("  '{{' in repr:", '{{' in inject_script_repr)
print("  '}}' in repr:", '}}' in inject_script_repr)

script_content = template.replace("__RECORD_FILE__", record_file)
script_content = script_content.replace("__TARGET_URL__", url)
script_content = script_content.replace("__HEADLESS__", str(headless))
script_content = script_content.replace("__INJECT_SCRIPT__", inject_script_repr)

print("\nStep 2 - Checking generated script for double braces:")
print("  '{{' in script:", '{{' in script_content)
print("  '}}' in script:", '}}' in script_content)

# 查找双花括号位置
if '{{' in script_content:
    idx = script_content.find('{{')
    print(f"\nFirst double '{{' found at position {idx}:")
    print(repr(script_content[max(0,idx-50):idx+50]))

# 写入文件检查
test_script_path = os.path.join(scripts_dir, "test_generated.py")
with open(test_script_path, 'w', encoding='utf-8') as f:
    f.write(script_content)
print(f"\nGenerated script written to: {test_script_path}")

# 验证语法
import py_compile
try:
    py_compile.compile(test_script_path, doraise=True)
    print("Syntax check: PASSED")
except py_compile.PyCompileError as e:
    print(f"Syntax check: FAILED - {e}")