# Phone bot (Nov 23 2026, his rule: "make it work for phone, gonna be using phone mostly").
# Runs every screen at the Galaxy S23 Ultra's size with real finger touches: home, Body, Build, Details, Part Maker, Photo, camera buttons.
# Checks: every button can be reached and is big enough to tap, the mech (or the picked part) stays in view above the open panel,
# nothing makes the page scroll sideways, the main jobs work by touch, no page errors. Paint has its own bot (paint_bot.py).
# Run: python3 tools/bot/phone_bot.py [page]   (default index.html). Needs playwright + chrome; three.js served from ROOT.
import asyncio, os, sys, time
from playwright.async_api import async_playwright
ROOT = '/tmp/t/node_modules/three'
PAGE = sys.argv[1] if len(sys.argv) > 1 else 'index.html'
W, H = 384, 824
BOX = """(sel=>{const M=window.__mf,T=M.mech.position.constructor,c=window.__cam,root=sel==='*'?M.mech:M.held[sel];M.mech.updateMatrixWorld(true);
  let x0=1e9,y0=1e9,x1=-1e9,y1=-1e9;const v=new T();root.traverse(o=>{if(o.isMesh&&o.visible&&!o.userData.ui&&!o.userData.overlay){o.geometry.computeBoundingBox();const b=o.geometry.boundingBox;
  for(const p of [[b.min.x,b.min.y,b.min.z],[b.max.x,b.max.y,b.max.z],[b.min.x,b.max.y,b.min.z],[b.max.x,b.min.y,b.max.z],[b.min.x,b.min.y,b.max.z],[b.max.x,b.max.y,b.min.z]]){v.set(...p).applyMatrix4(o.matrixWorld).project(c);
  const sx=(v.x+1)/2*innerWidth,sy=(1-v.y)/2*innerHeight;x0=Math.min(x0,sx);x1=Math.max(x1,sx);y0=Math.min(y0,sy);y1=Math.max(y1,sy)}}});
  const cover=[...document.querySelectorAll('#bar,#body.open,#build.open,#details.open,#paint.open,#photoBar')].filter(e=>e.offsetParent!==null).map(e=>e.getBoundingClientRect().top);
  const top=Math.min(innerHeight,...cover);
  return {seen:Math.round(100*Math.max(0,Math.min(y1,top)-Math.max(y0,0))/Math.max(1,y1-y0)),wide:Math.round(100*Math.max(0,Math.min(x1,innerWidth)-Math.max(x0,0))/Math.max(1,x1-x0)),tall:Math.round(y1-y0),free:Math.round(top)}})"""
MID = """(s=>{const h=window.__mf.held[s],T=window.__mf.mech.position.constructor,c=new T();let n=0;window.__mf.mech.updateMatrixWorld(true);
  h.traverse(m=>{if(m.isMesh&&m.userData.paintable){m.geometry.computeBoundingSphere();c.add(m.geometry.boundingSphere.center.clone().applyMatrix4(m.matrixWorld));n++}});
  c.multiplyScalar(1/n).project(window.__cam);return [(c.x+1)/2*innerWidth,(1-c.y)/2*innerHeight]})"""

async def main():
    fails = []
    def check(ok, what):
        print(('  ok   ' if ok else '  FAIL ') + what, flush=True)
        if not ok: fails.append(what)
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--use-gl=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': W, 'height': H}, is_mobile=True, has_touch=True, device_scale_factor=3, accept_downloads=True)
        pg = await ctx.new_page()
        errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
        async def route(r): await r.fulfill(path=os.path.join(ROOT, r.request.url.split('three@0.170.0/')[1]), content_type='application/javascript')
        await pg.route('https://cdn.jsdelivr.net/**', route)
        url = 'file://' + os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', PAGE))
        await pg.goto(url); await pg.evaluate("localStorage.clear()"); await pg.reload(); await pg.wait_for_timeout(3500)
        cdp = await ctx.new_cdp_session(pg)
        async def poke(x, y):
            t0 = time.time()
            await cdp.send('Input.dispatchTouchEvent', {'type': 'touchStart', 'touchPoints': [{'x': x, 'y': y}], 'timestamp': t0})
            await cdp.send('Input.dispatchTouchEvent', {'type': 'touchEnd', 'touchPoints': [], 'timestamp': t0 + .08}); await pg.wait_for_timeout(500)
        async def tap(sel, wait=350):
            el = await pg.query_selector(sel); await el.scroll_into_view_if_needed(); await el.tap(); await pg.wait_for_timeout(wait)
        async def settle(ms=700):                                       # wait for the camera to finish gliding (software rendering here is slow)
            await pg.wait_for_timeout(250)
            for _ in range(60):
                if not await pg.evaluate("window.__mf.camBusy()"): break
                await pg.wait_for_timeout(250)
            await pg.wait_for_timeout(ms)
        async def controls(scope, label, min_size=34):
            ids = await pg.evaluate("""(scope=>{document.querySelectorAll('[data-botid]').forEach(e=>delete e.dataset.botid);
              return [...document.querySelectorAll(scope)].flatMap(root=>[...root.querySelectorAll('button, select, input')]).filter(e=>e.offsetParent!==null&&!e.closest('[hidden]')).map((e,i)=>{e.dataset.botid='b'+i;return 'b'+i})})""", scope)
            bad, small = [], []
            for i in ids:
                el = await pg.query_selector(f'[data-botid="{i}"]')
                try: await el.scroll_into_view_if_needed(timeout=2500)
                except Exception: bad.append(i); continue
                r = await el.bounding_box()
                if not r or r['y'] < -1 or r['y'] + r['height'] > H + 1 or r['x'] < -1 or r['x'] + r['width'] > W + 1: bad.append(i)
                elif r['height'] < min_size - .5 and await el.evaluate("e=>e.type!=='range'"): small.append(await el.evaluate("e=>(e.textContent||e.id||e.type).trim().slice(0,14)"))
            check(not bad, f'{label}: {len(ids) - len(bad)}/{len(ids)} controls can be reached')
            check(not small, f'{label}: every button is at least {min_size}px tall' + (f' (too small: {small[:6]})' if small else ''))
        async def no_sideways(label):
            w = await pg.evaluate("Math.max(document.documentElement.scrollWidth, document.body.scrollWidth)")
            check(w <= W + 1, f'{label}: the page does not scroll sideways ({w}px wide)')

        await pg.evaluate("(async()=>{await window.__mf.applyBuild('standard','kit',{...window.MF_STARTERS[0].parts})})()"); await settle(1500)
        await pg.evaluate("document.querySelector('[data-view=\"angle\"]').click()"); await settle()

        print('1. Home screen', flush=True)
        iw = await pg.evaluate("innerWidth")
        check(iw == W, f'the page is laid out at phone width ({iw}px, phone is {W}px)')
        bar = await pg.evaluate("document.getElementById('bar').getBoundingClientRect().height")
        check(bar <= 110, f'bottom buttons take two rows or fewer ({bar:.0f}px)')
        vis = await pg.evaluate("[...document.querySelectorAll('#bar button')].filter(b=>b.offsetParent!==null).every(b=>{const r=b.getBoundingClientRect();return r.left>=-1&&r.right<=innerWidth+1&&r.bottom<=innerHeight+1})")
        check(vis, 'every bottom button is on screen without swiping')
        await controls('#bar', 'bottom buttons', 36)
        s = await pg.evaluate(BOX + "('*')")
        check(s['seen'] >= 98 and s['wide'] >= 98, f"whole mech on screen: {s['seen']}% tall, {s['wide']}% wide")
        check(s['tall'] >= .5 * s['free'], f"mech fills the screen well ({s['tall']}px of {s['free']}px free)")
        pr = await pg.evaluate("window.__mf.renderer.getPixelRatio()")
        check(pr <= 2, f'drawing detail capped for speed (pixel ratio {pr})')
        await no_sideways('home')
        await tap('#viewsBtn'); await controls('#views', 'camera buttons', 34); await tap('#viewsBtn')
        check(not await pg.evaluate("document.getElementById('views').offsetParent!==null"), 'camera buttons fold away again')

        print('2. Body', flush=True)
        await tap('#bodyBtn'); await settle()
        await controls('#body', 'Body panel')
        s = await pg.evaluate(BOX + "('*')"); check(s['seen'] >= 95 and s['wide'] >= 95, f"mech stays in view above the panel: {s['seen']}% tall, {s['wide']}% wide")
        h0 = await pg.evaluate(BOX + "('*')")
        await pg.evaluate("(()=>{const i=document.querySelector('#sliders input');i.value=+i.max;i.dispatchEvent(new Event('input'))})()"); await settle(1200)
        top0 = await pg.evaluate("window.__bones.head.getWorldPosition(new (window.__mf.mech.position.constructor)()).y")
        await pg.evaluate("(()=>{const i=document.querySelector('#sliders input');i.value=1;i.dispatchEvent(new Event('input'))})()"); await settle(1200)
        top1 = await pg.evaluate("window.__bones.head.getWorldPosition(new (window.__mf.mech.position.constructor)()).y")
        check(top0 > top1 * 1.05, f'size slider reshapes the mech (head height {top1:.1f} -> {top0:.1f})')
        await no_sideways('Body'); await tap('#bodyBtn')

        print('3. Build', flush=True)
        await tap('#buildBtn'); await settle()
        await controls('#build', 'Build panel')
        s = await pg.evaluate(BOX + "('*')"); check(s['seen'] >= 95, f"mech stays in view above the panel: {s['seen']}% tall")
        x, y = await pg.evaluate(MID + "('chest')"); await poke(x, y); await settle()
        check(await pg.evaluate("document.getElementById('bonePick').value") == 'chest', 'tapping the chest on the mech picks the chest spot')
        s = await pg.evaluate(BOX + "('chest')"); check(s['seen'] >= 90 and s['wide'] >= 80, f"the picked part stays in view: {s['seen']}% tall, {s['wide']}% wide")
        on = await pg.evaluate("(()=>{const b=document.querySelector('#choices .on');if(!b)return false;const r=b.getBoundingClientRect();return r.left>=0&&r.right<=innerWidth})()")
        check(on, 'the part that is on is shown in the swipe row')
        before = await pg.evaluate("window.__mf.held.chest.userData.p.id")
        await tap('#choices button:nth-child(3)', 900); after = await pg.evaluate("window.__mf.held.chest.userData.p.id")
        check(before != after, f'tapping a part in the row swaps it ({before} -> {after})')
        await tap('#weaponRow [data-spot="weapon.R"]', 900); await tap('#choices button:nth-child(6)', 900)
        check(await pg.evaluate("!!window.__mf.held['weapon.R']"), 'a weapon can be put in the right hand')
        await no_sideways('Build'); await tap('#buildBtn'); await settle(1500)

        print('4. Details', flush=True)
        await tap('#detailsBtn'); await settle()
        await controls('#details', 'Details panel')
        n0 = await pg.evaluate("document.querySelectorAll('#detailChoices button').length")
        await tap('#detailChoices button'); x, y = await pg.evaluate(MID + "('chest')"); await poke(x, y); await settle(900)
        placed = await pg.evaluate("document.getElementById('detailEdit').style.display !== 'none' || JSON.parse(localStorage.getItem('mf-build2')||'{}').details?.length > 0")
        check(n0 > 0 and placed, 'a detail can be picked and stuck on the mech by tapping')
        await controls('#details', 'Details panel (editing)')
        await no_sideways('Details'); await tap('#detailsBtn')

        print('5. Part Maker', flush=True)
        await tap('#makeBtn', 900)
        check(await pg.evaluate("document.getElementById('maker').classList.contains('open')"), 'Part Maker opens')
        await controls('#maker', 'Part Maker')
        cv = await pg.evaluate("(()=>{const r=document.getElementById('mkCv').getBoundingClientRect();return [r.width,r.left,r.right]})()")
        check(cv[0] >= 300 and cv[1] >= 0 and cv[2] <= W + 1, f'sketch pad fits the screen ({cv[0]:.0f}px wide)')
        await no_sideways('Part Maker')
        await pg.evaluate("document.querySelector('#maker .mk-head button').click()"); await pg.wait_for_timeout(500)
        check(not await pg.evaluate("document.getElementById('maker').classList.contains('open')"), 'Part Maker closes')

        print('6. Photo mode', flush=True)
        await tap('#photoBtn'); await settle()
        await controls('#photoBar', 'Photo controls', 36)
        s = await pg.evaluate(BOX + "('*')"); check(s['seen'] >= 95 and s['wide'] >= 95, f"mech stays in view above the controls: {s['seen']}% tall, {s['wide']}% wide")
        await pg.select_option('#phBack', 'city'); await pg.select_option('#phMove', 'run')
        try:
            async with pg.expect_download(timeout=20000) as d: await tap('#phSave')
            dl = await d.value; path = '/tmp/phone_bot_photo.png'; await dl.save_as(path); size = os.path.getsize(path)
            check(size > 30000, f'Save picture makes a PNG ({size // 1024} KB)')
        except Exception as e: check(False, 'Save picture makes a PNG (' + str(e)[:60] + ')')
        await no_sideways('Photo'); await tap('#phDone'); await settle(1200)
        check(await pg.evaluate("!document.body.classList.contains('photo') && document.getElementById('bar').offsetParent !== null"), 'Done brings the normal buttons back')

        check(not errs, 'no page errors ' + (str(errs[:3]) if errs else ''))
        await b.close()
    print('\nPHONE BOT:', 'ALL OK' if not fails else f'{len(fails)} problem(s)')

asyncio.run(main())
