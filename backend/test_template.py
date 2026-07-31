import os
import json

RECORD_INJECT_SCRIPT = '''
(function() {
    window.__recordedActions = [];
    document.addEventListener('click', function(e) {
        var action = { type: 'click', selector: 'test' };
        console.log('__RECORD_ACTION__:' + JSON.stringify(action));
    }, true);
})();
'''

template = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import asyncio
import json

record_file = r"__RECORD_FILE__"
target_url = r"__TARGET_URL__"
headless_mode = __HEADLESS__

INJECT_SCRIPT = __INJECT_SCRIPT__

def save_actions(actions, status="recording"):
    try:
        data = {"actions": actions, "status": status, "count": len(actions)}
        with open(record_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False)
    except Exception as e:
        print(f"Save error: {e}", flush=True)

async def main():
    print(f"Starting browser, url={target_url}", flush=True)
    data = {"test": True}

if __name__ == "__main__":
    asyncio.run(main())
'''

# 执行替换
inject_script_repr = repr(RECORD_INJECT_SCRIPT)
print('repr output:', inject_script_repr[:200])
print()

script_content = template.replace("__RECORD_FILE__", "test.json")
script_content = script_content.replace("__TARGET_URL__", "https://example.com")
script_content = script_content.replace("__HEADLESS__", "False")
script_content = script_content.replace("__INJECT_SCRIPT__", inject_script_repr)

print('Resulting script:')
print(script_content)