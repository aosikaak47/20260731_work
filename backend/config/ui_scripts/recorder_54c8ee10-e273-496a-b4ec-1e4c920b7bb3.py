#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import asyncio
import json
import sys
import os

record_file = 'E:\\trae_work\\autoProject\\backend\\config\\ui_scripts\\record_54c8ee10-e273-496a-b4ec-1e4c920b7bb3.json'
target_url = 'http://192.168.100.167/hxkr/#/config/appCenter'
headless_mode = False

# 录制注入脚本
INJECT_SCRIPT = '\n(function() {\n    window.__recordedActions = [];\n    window.__recordActive = true;\n\n    function getElementSelector(element) {\n        if (element.id) return \'#\' + element.id;\n        if (element.name) return element.tagName.toLowerCase() + \'[name="\' + element.name + \'"]\';\n        if (element.getAttribute(\'data-testid\')) return \'[data-testid="\' + element.getAttribute(\'data-testid\') + \'"]\';\n        var path = [];\n        var current = element;\n        while (current && current.nodeType === 1 && path.length < 5) {\n            var selector = current.tagName.toLowerCase();\n            if (current.id) { selector += \'#\' + current.id; path.unshift(selector); break; }\n            var parent = current.parentNode;\n            if (parent) {\n                var siblings = Array.from(parent.children).filter(function(c) { return c.tagName === current.tagName; });\n                if (siblings.length > 1) {\n                    var index = siblings.indexOf(current) + 1;\n                    selector += \':nth-of-type(\' + index + \')\';\n                }\n                path.unshift(selector);\n            }\n            current = current.parentNode;\n        }\n        return path.join(\' > \');\n    }\n\n    function getElementType(element) {\n        var tag = element.tagName.toLowerCase();\n        var type = element.type ? element.type.toLowerCase() : \'\';\n        if (tag === \'input\') return type === \'text\' ? \'input\' : type || \'input\';\n        if (tag === \'textarea\') return \'textarea\';\n        if (tag === \'select\') return \'select\';\n        if (tag === \'button\') return \'button\';\n        if (tag === \'a\') return \'link\';\n        if (tag === \'img\') return \'image\';\n        return \'element\';\n    }\n\n    function getActionDescription(element, action) {\n        var selector = getElementSelector(element);\n        var elementType = getElementType(element);\n        var text = element.textContent ? element.textContent.trim().substring(0, 30) : \'\';\n        if (action === \'click\') {\n            return { type: \'click\', selector: selector, elementType: elementType, text: text, tagName: element.tagName.toLowerCase() };\n        } else if (action === \'input\') {\n            return { type: \'input\', selector: selector, elementType: elementType, value: element.value, tagName: element.tagName.toLowerCase() };\n        } else if (action === \'select\') {\n            return { type: \'select\', selector: selector, elementType: elementType, value: element.value, tagName: element.tagName.toLowerCase() };\n        } else if (action === \'hover\') {\n            return { type: \'hover\', selector: selector, elementType: elementType, text: text, tagName: element.tagName.toLowerCase() };\n        }\n        return { type: action, selector: selector, elementType: elementType };\n    }\n\n    function sendAction(action) {\n        action.timestamp = Date.now();\n        window.__recordedActions.push(action);\n        // 通过console.log发送给后端Playwright监听\n        console.log(\'__RECORD_ACTION__:\' + JSON.stringify(action));\n    }\n\n    // 防抖：输入操作只在失焦或回车时记录\n    var inputTimeout = null;\n    var lastInputTarget = null;\n    var lastInputValue = \'\';\n\n    document.addEventListener(\'click\', function(e) {\n        if (!window.__recordActive) return;\n        // 忽略对录制控制面板的点击\n        if (e.target.id === \'__recorder_panel\') return;\n        var action = getActionDescription(e.target, \'click\');\n        sendAction(action);\n    }, true);\n\n    document.addEventListener(\'input\', function(e) {\n        if (!window.__recordActive) return;\n        var target = e.target;\n        if (target.tagName === \'INPUT\' || target.tagName === \'TEXTAREA\') {\n            // 防抖：延迟记录输入操作\n            if (inputTimeout) clearTimeout(inputTimeout);\n            lastInputTarget = target;\n            lastInputValue = target.value;\n            inputTimeout = setTimeout(function() {\n                if (lastInputTarget && lastInputValue) {\n                    var action = getActionDescription(lastInputTarget, \'input\');\n                    action.value = lastInputValue;\n                    sendAction(action);\n                }\n            }, 800);\n        }\n    }, true);\n\n    document.addEventListener(\'change\', function(e) {\n        if (!window.__recordActive) return;\n        if (e.target.tagName === \'SELECT\') {\n            var action = getActionDescription(e.target, \'select\');\n            sendAction(action);\n        }\n    }, true);\n\n    // 监听页面导航\n    var lastUrl = location.href;\n    setInterval(function() {\n        if (!window.__recordActive) return;\n        if (location.href !== lastUrl) {\n            var action = {\n                type: \'navigate\',\n                url: location.href,\n                fromUrl: lastUrl,\n                timestamp: Date.now()\n            };\n            window.__recordedActions.push(action);\n            console.log(\'__RECORD_ACTION__:\' + JSON.stringify(action));\n            lastUrl = location.href;\n        }\n    }, 500);\n\n    window.stopRecording = function() {\n        window.__recordActive = false;\n        return window.__recordedActions;\n    };\n\n    window.getRecordedActions = function() {\n        return window.__recordedActions;\n    };\n\n    console.log(\'[UI Recorder] Recording started. Actions will be captured automatically.\');\n})();\n'

def save_actions(actions, status="recording"):
    try:
        data = dict(actions=actions, status=status, count=len(actions))
        with open(record_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)
    except Exception as e:
        print("Save error: %s" % e, flush=True)

async def main():
    try:
        from playwright.async_api import async_playwright
        
        print("[Recorder] Starting browser, url=%s" % target_url, flush=True)
        save_actions([], "starting")
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=headless_mode)
            context = await browser.new_context()
            page = await context.new_page()
            
            print("[Recorder] Browser launched, navigating to %s" % target_url, flush=True)
            
            # 注入录制脚本
            await page.add_init_script(INJECT_SCRIPT)
            
            recorded_actions = []
            
            def on_console(msg):
                try:
                    if msg.text.startswith("__RECORD_ACTION__:"):
                        action_data = msg.text.replace("__RECORD_ACTION__:", "")
                        action = json.loads(action_data)
                        recorded_actions.append(action)
                        save_actions(recorded_actions, "recording")
                        print("[Recorder] Captured action: %s - %s" % (action.get("type", ""), action.get("selector", action.get("url", ""))), flush=True)
                except Exception as e:
                    print("[Recorder] Console error: %s" % e, flush=True)
            
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
                print("[Recorder] Wait error: %s" % e, flush=True)
            
            save_actions(recorded_actions, "completed")
            print("[Recorder] Session ended. Total actions: %d" % len(recorded_actions), flush=True)
            await browser.close()
            
    except Exception as e:
        print("[Recorder] Error: %s" % e, flush=True)
        try:
            save_actions([], "error: %s" % e)
        except:
            pass

if __name__ == "__main__":
    asyncio.run(main())
