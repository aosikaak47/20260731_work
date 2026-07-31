import asyncio
import sys

async def test():
    try:
        from playwright.async_api import async_playwright
        print("Playwright imported successfully")
        
        async with async_playwright() as p:
            print("Playwright async initialized")
            
            browser = await p.chromium.launch(headless=False)
            print("Browser launched successfully")
            
            context = await browser.new_context()
            page = await context.new_page()
            print("New page created")
            
            await page.goto("https://www.baidu.com", wait_until="domcontentloaded")
            print("Page loaded successfully")
            
            title = await page.title()
            print(f"Page title: {title}")
            
            await asyncio.sleep(3)
            print("Waited 3 seconds")
            
            await browser.close()
            print("Browser closed")
            
        print("Test PASSED!")
    except Exception as e:
        print(f"Test FAILED: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test())