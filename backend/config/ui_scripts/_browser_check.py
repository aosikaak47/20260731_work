import asyncio
from playwright.async_api import async_playwright

async def test():
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            await browser.close()
            print("BROWSER_OK")
    except Exception as e:
        print(f"BROWSER_ERROR: {e}")

asyncio.run(test())
