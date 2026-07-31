import os
import sys

# 检查系统浏览器
def check_system_browsers():
    browsers = []
    
    # 检查Chrome
    chrome_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
    ]
    for path in chrome_paths:
        if os.path.exists(path):
            browsers.append(("chrome", path))
            print(f"Found Chrome: {path}")
            break
    
    # 检查Edge
    edge_paths = [
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\Edge\Application\msedge.exe"),
    ]
    for path in edge_paths:
        if os.path.exists(path):
            browsers.append(("edge", path))
            print(f"Found Edge: {path}")
            break
    
    return browsers

print("Checking system browsers...")
browsers = check_system_browsers()

if browsers:
    print(f"\nFound {len(browsers)} browser(s):")
    for b_type, b_path in browsers:
        print(f"  - {b_type}: {b_path}")
else:
    print("\nNo system browsers found!")

# 检查Playwright浏览器
print("\nChecking Playwright browsers...")
try:
    from playwright._impl._driver import compute_driver_executable
    driver_path = compute_driver_executable()
    print(f"Playwright driver path: {driver_path}")
    
    # 尝试查找Playwright安装的浏览器
    import subprocess
    result = subprocess.run(
        [sys.executable, "-m", "playwright", "install", "--dry-run", "chromium"],
        capture_output=True, text=True, timeout=10
    )
    print(f"Playwright install status: {result.stdout}")
except Exception as e:
    print(f"Playwright check error: {e}")

# 直接测试Playwright是否能启动
print("\nTesting Playwright launch...")
try:
    import asyncio
    from playwright.async_api import async_playwright
    
    async def test_launch():
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            await browser.close()
            return True
    
    result = asyncio.run(test_launch())
    print(f"Playwright launch: {'OK' if result else 'FAILED'}")
except Exception as e:
    print(f"Playwright launch error: {e}")