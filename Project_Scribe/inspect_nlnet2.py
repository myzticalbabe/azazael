import asyncio
from playwright.async_api import async_playwright

async def check():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, args=['--disable-blink-features=AutomationControlled'])
        context = await browser.new_context()
        page = await context.new_page()
        await page.goto('https://nlnet.nl/grants/', wait_until='networkidle', timeout=60000)
        print('URL:', page.url)
        elements = await page.query_selector_all('a, button')
        for el in elements:
            tag = await el.evaluate('el => el.tagName.toLowerCase()')
            text = await el.text_content()
            href = await el.get_attribute('href') if tag == 'a' else None
            if text and text.strip():
                t = text.strip()[:80]
                print(f'  {tag}: text="{t}" href={href}')
        await page.wait_for_timeout(2000)
        forms = await page.query_selector_all('form')
        for f in forms:
            action = await f.get_attribute('action')
            print(f'  form action: {action}')
        await browser.close()

asyncio.run(check())