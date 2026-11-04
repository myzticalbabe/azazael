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
        await page.goto('https://github.com/securitylab/secure-open-source-fund', wait_until='networkidle', timeout=60000)
        print('URL:', page.url)
        await page.wait_for_timeout(5000)
        
        # Look for links with "apply" or "grant" or "fund"
        elements = await page.query_selector_all('a')
        for el in elements:
            text = await el.text_content()
            href = await el.get_attribute('href')
            if text and text.strip() and ('apply' in text.lower() or 'grant' in text.lower() or 'fund' in text.lower() or 'submit' in text.lower() or 'proposal' in text.lower()):
                t = text.strip()[:80]
                print(f'  a: text="{t}" href={href}')
        
        # Check for forms
        forms = await page.query_selector_all('form')
        for i, f in enumerate(forms):
            action = await f.get_attribute('action')
            method = await f.get_attribute('method')
            print(f'  Form {i}: action={action} method={method}')
            inputs = await f.query_selector_all('input, textarea, select')
            for inp in inputs:
                name = await inp.get_attribute('name')
                id_attr = await inp.get_attribute('id')
                type_attr = await inp.get_attribute('type')
                placeholder = await inp.get_attribute('placeholder')
                print(f'    field: name={name} id={id_attr} type={type_attr} placeholder={placeholder}')
        
        await browser.close()

asyncio.run(check())