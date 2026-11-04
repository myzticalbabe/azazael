import asyncio
from playwright.async_api import async_playwright

async def check():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, args=['--disable-blink-features=AutomationControlled'])
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            extra_http_headers={
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
            }
        )
        page = await context.new_page()
        await page.goto('https://nlnet.nl/propose', wait_until='networkidle', timeout=60000)
        print('URL:', page.url)
        await page.wait_for_timeout(3000)
        content = await page.content()
        print('Content length:', len(content))
        print('First 5000 chars:')
        print(content[:5000])
        await browser.close()

asyncio.run(check())