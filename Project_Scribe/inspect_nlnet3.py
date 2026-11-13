import asyncio
from playwright.async_api import async_playwright

async def check():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, args=['--disable-blink-features=AutomationControlled'])
        context = await browser.new_context()
        page = await context.new_page()
        await page.goto('https://nlnet.nl/grants/', wait_until='networkidle', timeout=60000)
        print('URL:', page.url)
        # Wait longer for dynamic content
        await page.wait_for_timeout(5000)
        content = await page.content()
        print('Content length:', len(content))
        # Check for any links
        elements = await page.query_selector_all('a')
        print(f'Found {len(elements)} links')
        for el in elements[:20]:
            text = await el.text_content()
            href = await el.get_attribute('href')
            if text and text.strip():
                print(f'  a: "{text.strip()[:80]}" href={href}')
        await browser.close()

asyncio.run(check())