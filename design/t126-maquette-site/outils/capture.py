import sys, asyncio
from playwright.async_api import async_playwright
base, out = sys.argv[1], sys.argv[2]
pages = [a.split('=',1) for a in sys.argv[3:]]
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        for nom, url in pages:
            for w in (320, 1440):
                for sch in ('light','dark'):
                    ctx = await b.new_context(viewport={'width':w,'height':900}, color_scheme=sch, reduced_motion='reduce')
                    pg = await ctx.new_page()
                    await pg.goto(base+url, wait_until='networkidle')
                    await pg.wait_for_timeout(700)
                    await pg.screenshot(path=f'{out}/{nom}-{w}-{sch}.png', full_page=True)
                    await ctx.close()
        await b.close()
asyncio.run(main())
