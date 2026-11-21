import sys, asyncio
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await b.new_page()
        await pg.goto(sys.argv[1], wait_until='networkidle'); await pg.wait_for_timeout(500)
        while await pg.locator('button.plus').count():
            await pg.click('button.plus'); await pg.wait_for_timeout(150)
        open(sys.argv[2],'w').write(await pg.inner_html('#site'))
        await b.close()
asyncio.run(main())
