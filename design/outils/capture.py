"""Captures d'écran et PDF avec Chrome, polices et CDN servis en local."""
import asyncio, json, sys, re
from playwright.async_api import async_playwright
T='/tmp/design/tools'
FONTMAP=json.load(open(f'{T}/fontmap.json'))
GF=open(f'{T}/gfonts.css').read()
TW=open(f'{T}/tw-python.css').read()
FA='/tmp/vendor/fortawesome-fontawesome-free-6.4.0/package'

async def route(r):
    u=r.request.url
    if 'fonts.googleapis.com' in u:
        return await r.fulfill(status=200, content_type='text/css', body=GF)
    if 'fonts.gstatic.com/local/' in u:
        fn=u.rsplit('/',1)[1]
        if fn in FONTMAP: return await r.fulfill(path=FONTMAP[fn], content_type='font/woff2')
    if 'cdn.tailwindcss.com' in u:
        js='(function(){var s=document.createElement("style");s.textContent='+json.dumps(TW)+';document.head.appendChild(s);window.tailwind={};})();'
        return await r.fulfill(status=200, content_type='application/javascript', body=js)
    if 'cdnjs.cloudflare.com/ajax/libs/font-awesome' in u:
        if u.endswith('.css'):
            css=open(f'{FA}/css/all.min.css').read().replace('../webfonts/','https://cdnjs.cloudflare.com/fa-local/')
            return await r.fulfill(status=200, content_type='text/css', body=css)
    if 'cdnjs.cloudflare.com/fa-local/' in u:
        fn=u.rsplit('/',1)[1].split('?')[0]
        return await r.fulfill(path=f'{FA}/webfonts/{fn}')
    if u.startswith('http://localhost') or u.startswith('file:') or u.startswith('data:'):
        return await r.continue_()
    return await r.abort()

async def run(jobs):
    async with async_playwright() as p:
        b=await p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox'])
        for j in jobs:
            ctx=await b.new_context(viewport={'width':j.get('w',1280),'height':j.get('h',900)},
                                    color_scheme=j.get('scheme','light'), device_scale_factor=j.get('dpr',1))
            if j.get('storage'):
                await ctx.add_init_script("try{localStorage.setItem('theme',%s)}catch(e){}" % json.dumps(j['storage']))
            pg=await ctx.new_page()
            await pg.route('**/*', route)
            await pg.goto(j['url'], wait_until='load')
            await pg.wait_for_timeout(j.get('wait',700))
            if j.get('media'): await pg.emulate_media(media=j['media'])
            if j.get("js"):
                await pg.evaluate(j["js"]); await pg.wait_for_timeout(1500)
            if j.get('pdf'):
                await pg.pdf(path=j['out'], prefer_css_page_size=True, print_background=True)
            else:
                if j.get('selector'):
                    el=await pg.query_selector(j['selector']); await el.screenshot(path=j['out'])
                else:
                    await pg.screenshot(path=j['out'], full_page=j.get('full',False))
            print('ok', j['out'])
            await ctx.close()
        await b.close()

if __name__=='__main__':
    asyncio.run(run(json.load(open(sys.argv[1]))))
