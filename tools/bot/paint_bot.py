# Paint bot (Nov 23 2026): tries the paint page the way a phone does (real touch events, Galaxy S23 Ultra screen size).
# Checks: the mech fits above the panel, every paint control can be reached, every brush paints with a finger,
# skins / elements + bits / mark / decals / layers / undo work, everything comes back after a reload, no page errors.
# Run: python3 tools/bot/paint_bot.py [page]   (default test.html). Needs playwright + chrome; three.js served from ROOT.
import asyncio, os, sys, time
from playwright.async_api import async_playwright
ROOT = '/tmp/t/node_modules/three'
PAGE = sys.argv[1] if len(sys.argv) > 1 else 'test.html'
W, H = 384, 824   # Galaxy S23 Ultra in Chrome (CSS pixels)
COUNT = """(()=>{const o={};const all=MF_PAINT._all();for(const [s,h] of Object.entries(all))h.traverse(m=>{if(m.isMesh&&m.userData.pt){const p=m.userData.pt;let n=0;
  for(let i=3;i<p.pc.length;i+=4)n+=p.pc[i];for(const L of p.L)for(const v of L.m)n+=v;if(n>1)o[s]=(o[s]||0)+Math.round(n)}});return o})()"""
TOTAL = "(o=>Object.values(o).reduce((a,b)=>a+b,0))(" + COUNT + ")"
MID = """(s=>{const h=MF_PAINT._all()[s],T=window.__mf.mech.position.constructor,c=new T();let n=0;window.__mf.mech.updateMatrixWorld(true);
  h.traverse(m=>{if(m.isMesh&&m.userData.paintable){m.geometry.computeBoundingSphere();c.add(m.geometry.boundingSphere.center.clone().applyMatrix4(m.matrixWorld));n++}});
  c.multiplyScalar(1/n).project(window.__cam);return [(c.x+1)/2*innerWidth,(1-c.y)/2*innerHeight]})"""
SEE = """(()=>{const M=window.__mf,T=M.mech.position.constructor,c=window.__cam;M.mech.updateMatrixWorld(true);
  let x0=1e9,y0=1e9,x1=-1e9,y1=-1e9;const v=new T();M.mech.traverse(o=>{if(o.isMesh&&o.visible&&!o.userData.ui){o.geometry.computeBoundingBox();const b=o.geometry.boundingBox;
  for(const p of [[b.min.x,b.min.y,b.min.z],[b.max.x,b.max.y,b.max.z],[b.min.x,b.max.y,b.min.z],[b.max.x,b.min.y,b.max.z]]){v.set(...p).applyMatrix4(o.matrixWorld).project(c);
  const sx=(v.x+1)/2*innerWidth,sy=(1-v.y)/2*innerHeight;x0=Math.min(x0,sx);x1=Math.max(x1,sx);y0=Math.min(y0,sy);y1=Math.max(y1,sy)}}});
  const top=document.getElementById('paint').getBoundingClientRect().top;
  return {top:Math.round(y0),bottom:Math.round(y1),left:Math.round(x0),right:Math.round(x1),panel:Math.round(top),
    seen:Math.round(100*Math.max(0,Math.min(y1,top)-Math.max(y0,0))/Math.max(1,y1-y0)),wide:Math.round(100*Math.max(0,Math.min(x1,innerWidth)-Math.max(x0,0))/Math.max(1,x1-x0))}})()"""

async def main():
    fails = []
    def check(ok, what):
        print(('  ok   ' if ok else '  FAIL ') + what, flush=True)
        if not ok: fails.append(what)
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--use-gl=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': W, 'height': H}, is_mobile=True, has_touch=True, device_scale_factor=1)
        pg = await ctx.new_page()
        errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
        async def route(r): await r.fulfill(path=os.path.join(ROOT, r.request.url.split('three@0.170.0/')[1]), content_type='application/javascript')
        await pg.route('https://cdn.jsdelivr.net/**', route)
        url = 'file://' + os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', PAGE))
        await pg.goto(url); await pg.evaluate("localStorage.clear()"); await pg.reload(); await pg.wait_for_timeout(3000)
        cdp = await ctx.new_cdp_session(pg)
        async def finger(path):
            await cdp.send('Input.dispatchTouchEvent', {'type': 'touchStart', 'touchPoints': [{'x': path[0][0], 'y': path[0][1]}]})
            for x, y in path[1:]:
                await cdp.send('Input.dispatchTouchEvent', {'type': 'touchMove', 'touchPoints': [{'x': x, 'y': y}]}); await pg.wait_for_timeout(16)
            await cdp.send('Input.dispatchTouchEvent', {'type': 'touchEnd', 'touchPoints': []}); await pg.wait_for_timeout(300)
        async def poke(spot, dy=0):
            await pg.wait_for_timeout(500)       # let the page settle so a tap stays a quick tap
            x, y = await pg.evaluate(MID + f"('{spot}')")
            t0 = time.time()                    # a real finger tap is ~80 ms whatever the frame rate (software rendering here is slow)
            await cdp.send('Input.dispatchTouchEvent', {'type': 'touchStart', 'touchPoints': [{'x': x, 'y': y + dy}], 'timestamp': t0})
            await cdp.send('Input.dispatchTouchEvent', {'type': 'touchEnd', 'touchPoints': [], 'timestamp': t0 + .08}); await pg.wait_for_timeout(400)
        async def tap(sel):
            el = await pg.query_selector(sel); await el.scroll_into_view_if_needed(); await el.tap(); await pg.wait_for_timeout(150)
        async def drag(spot='chest', dy=0, n=14, dx=34):
            x, y = await pg.evaluate(MID + f"('{spot}')"); y += dy
            await finger([(x - dx + k * (2 * dx / n), y + (k % 2) * 4) for k in range(n + 1)])
        await pg.evaluate("(async()=>{await window.__mf.applyBuild('standard','kit',{...window.MF_STARTERS[0].parts})})()"); await pg.wait_for_timeout(800)

        print('1. Opening Paint on a phone screen', flush=True)
        await tap('#paintBtn'); await pg.wait_for_timeout(1500)
        bar = await pg.evaluate("document.getElementById('bar').getBoundingClientRect().height")
        check(bar < 76, f'bottom bar is one row ({bar:.0f}px tall)')
        see = await pg.evaluate(SEE)
        check(see['seen'] >= 95 and see['wide'] >= 95, f"whole mech on screen above the panel: {see['seen']}% tall, {see['wide']}% wide (mech {see['top']}-{see['bottom']}px, panel starts {see['panel']}px)")
        check(see['bottom'] - see['top'] >= 250, f"mech is big enough to paint ({see['bottom'] - see['top']}px tall)")

        print('2. Every paint control can be reached', flush=True)
        for tab in ['brush', 'skin', 'mark', 'decal', 'more']:
            await tap(f'#pTabs [data-pt="{tab}"]')
            if tab == 'brush': await tap('[data-pb="color"]')
            ids = await pg.evaluate("""document.querySelectorAll('[data-botid]').forEach(e=>delete e.dataset.botid),[...document.querySelectorAll('#paint button, #paint select, #paint input')].filter(e=>e.offsetParent!==null&&!e.closest('[hidden]')).map((e,i)=>{e.dataset.botid='b'+i;return 'b'+i})""")
            bad = []
            for i in ids:
                el = await pg.query_selector(f'[data-botid="{i}"]')
                try: await el.scroll_into_view_if_needed(timeout=1500)
                except Exception: bad.append(i); continue
                r = await el.bounding_box()
                if not r or r['y'] < 0 or r['y'] + r['height'] > H or r['x'] < -1 or r['x'] + r['width'] > W + 1: bad.append(i)
            check(not bad, f'{tab} tab: {len(ids) - len(bad)}/{len(ids)} controls reachable')
        await tap('#pTabs [data-pt="brush"]')

        print('3. Painting with a finger', flush=True)
        for brush, dy in [('color', 0), ('spray', 14), ('blotch', -12), ('blend', 0), ('erase', 14)]:
            before = await pg.evaluate(TOTAL); await tap(f'[data-pb="{brush}"]'); await drag('chest', dy); after = await pg.evaluate(TOTAL)
            check(after != before, f'{brush}: paint amount {before} -> {after}')
        await tap('[data-pb="wear"]')
        for kind in ['edge', 'dirt', 'rust', 'scorch']:
            before = await pg.evaluate(TOTAL); await tap(f'[data-wear="{kind}"]'); await drag('thigh.L' if kind != 'edge' else 'chest', 0); after = await pg.evaluate(TOTAL)
            check(after != before, f'wear ({kind}): {before} -> {after}')
        await tap('[data-pb="fill"]'); await pg.evaluate("MF_PAINT._test.setColour('#00ff00')")
        before = await pg.evaluate(TOTAL); await poke('shin.R'); after = await pg.evaluate(TOTAL)
        check(after > before, f'fill: {before} -> {after}')
        await tap('#pUndo'); undone = await pg.evaluate(TOTAL)
        check(undone == before, f'undo puts it back ({undone} == {before})')
        await poke('shin.R'); await pg.evaluate("MF_PAINT._test.setColour('#ff0000')"); await tap('[data-pb="pick"]'); await poke('shin.R')
        got = await pg.evaluate("document.getElementById('pbCol').value")
        check(got.lower() == '#00ff00', f'pick colour grabbed {got} (wanted #00ff00)')
        await tap('[data-pb="grad"]'); before = await pg.evaluate(TOTAL); await poke('forearm.R'); after = await pg.evaluate(TOTAL)
        check(after > before, f'gradient: {before} -> {after}')
        await tap('[data-pb="color"]'); await tap('#pWith'); await tap('#pTabs [data-pt="skin"]'); await pg.select_option('#pGroup', 'Scratches & Wear')
        await tap('#pSkins button:nth-child(4)'); await tap('#pTabs [data-pt="brush"]')
        await drag('chest', -6)
        layers = await pg.evaluate("(()=>{let n=0;Object.values(MF_PAINT._all()).forEach(h=>h.traverse(m=>{if(m.isMesh&&m.userData.pt)n+=m.userData.pt.L.filter(L=>L.m.some(v=>v>.05)).length}));return n})()")
        check(layers > 0, f'skin brush made {layers} brushed-skin layer(s)')
        check(await pg.evaluate("MF_PAINT.frozen"), 'mech holds still while a brush is on')

        print('4. Skins, elements, mark, layers', flush=True)
        await tap('[data-pb=""]'); await tap('#pTabs [data-pt="skin"]'); await pg.select_option('#pTarget', 'armor'); await pg.select_option('#pGroup', 'Metal')
        await tap('#pSkins button:nth-child(7)'); await pg.wait_for_timeout(1200)
        n = await pg.evaluate("(()=>{let n=0;Object.values(window.__mf.held).forEach(h=>h.traverse(m=>{if(m.isMesh&&m.userData.paintable&&m.material.userData.skin)n++}));return n})()")
        check(n > 5, f'skin on Whole mech: Main -> {n} pieces skinned')
        await poke('chest')
        check(await pg.evaluate("MF_PAINT._test.tapped()") == 'chest', 'tapping the chest picks it')
        await tap('#pTabs [data-pt="mark"]')
        rows = await pg.evaluate("document.querySelectorAll('#pLayers .plyr').length")
        check(rows >= 2, f'layer list shows {rows} layers on the chest')
        await tap('#pLayers .plyr button:last-child'); await pg.wait_for_timeout(900); rows2 = await pg.evaluate("document.querySelectorAll('#pLayers .plyr').length")
        check(rows2 == rows - 1, f'removing a layer: {rows} -> {rows2}')
        await poke('shin.L'); await tap('#pTabs [data-pt="more"]'); await pg.select_option('#pElem', 'Lava'); await pg.wait_for_timeout(600)
        el = await pg.evaluate("JSON.stringify(MF_PAINT._test.state().S.skins.part)")
        bits = await pg.evaluate("(()=>{let n=0;window.__mf.mech.traverse(o=>{if(o.userData.bit)n++});return n})()")
        check('lavarock' in el and bits > 5, f'Lava element on the picked part, {bits} lava rocks grown')
        await tap('#pNight'); await tap('#pNight')
        await tap('#pTabs [data-pt="mark"]'); await tap('#pMark')
        for spot in ['forearm.L', 'thigh.R']: await poke(spot)
        marked = await pg.evaluate("MF_PAINT._test.marks.size")
        check(marked == 2, f'mark: {marked}/2 parts marked by tapping')
        before = await pg.evaluate(TOTAL); await tap('#pFillMarked'); after = await pg.evaluate(TOTAL)
        check(after > before, f'fill marked: {before} -> {after}')
        await tap('#pMark')

        print('5. Decals', flush=True)
        await tap('#pTabs [data-pt="decal"]'); await tap('[data-dk="num"]'); await poke('chest')
        await tap('[data-dk="hazard"]'); await poke('thigh.L')
        nd = await pg.evaluate("MF_PAINT._test.state().S.decals.length"); nb = await pg.evaluate("MF_PAINT._test.decalBits()")
        check(nd == 2 and nb >= 2, f'{nd} decals stuck on ({nb} pieces on the surface)')

        print('6. Saved', flush=True)
        saved = await pg.evaluate(COUNT)
        await pg.reload(); await pg.wait_for_timeout(4000)
        back = await pg.evaluate(COUNT); nb2 = await pg.evaluate("MF_PAINT._test.decalBits()")
        bits2 = await pg.evaluate("(()=>{let n=0;window.__mf.mech.traverse(o=>{if(o.userData.bit)n++});return n})()")
        check(set(saved) == set(back), f'paint came back after reload on {len(back)}/{len(saved)} spots')
        check(nb2 >= 2, f'decals came back after reload ({nb2} pieces)')
        check(bits2 == bits, f'element bits came back after reload ({bits2})')
        check(not errs, 'no page errors ' + (str(errs[:3]) if errs else ''))
        await pg.screenshot(path='/tmp/pt/bot_end.png')
        await b.close()
    print('\nPAINT BOT:', 'ALL OK' if not fails else f'{len(fails)} problem(s)')

asyncio.run(main())
