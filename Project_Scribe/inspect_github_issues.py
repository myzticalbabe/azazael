import asyncio
from playwright.async_api import async_playwright

async def check():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, args=['--disable-blink-features=AutomationControlled'])
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        )
        page = await context.new_page()
        await page.goto('https://github.com/securitylab/secure-open-source-fund/issues/new/choose', wait_until='networkidle', timeout=60000)
        print('URL:', page.url)
        await page.wait_for_timeout(5000)
        elements = await page.query_selector_all('a')
        for el in elements:
            text = await el.text_content()
            href = await el.get_attribute('href')
            if text and ('apply' in text.lower() or 'grant' in text.lower() or 'fund' in text.lower() or 'proposal' in text.lower() or 'template' in text.lower()):
                t = text.strip()[:80]
                print(f'  a: text="{t}" href={href}')
        await browser.close()

asyncio.run(check())