# Shoulder weapon bot (Nov 22 2026): every shoulder weapon on every shoulder pad. Checks nothing on the pad pokes into it,
# it sits on the real surface (ray down / sideways), and it clears the head, chest and backpack. Run: python3 tools/bot/shoulder_bot.py standard heavy
import asyncio, os, sys
from playwright.async_api import async_playwright
ROOT='/tmp/t/node_modules/three'
JS=r"""async ({preset})=>{const M=window.__mf,B=window.__bones,T=M.mech.position.constructor;
 await M.applyBuild(preset,'kit',{...window.MF_STARTERS[0].parts}); await new Promise(r=>setTimeout(r,500)); M.renderer.setAnimationLoop(null);
 const out=[]; const pads=window.MF_PARTS.shoulder.map(p=>p.id), mounts=window.MF_WEAPONS.shoulder.map(w=>w.id);
 const pts=h=>{const o=[],v=new T();h.traverse(m=>{if(m.isMesh){const p=m.geometry.attributes.position;for(let k=0;k<p.count;k++)o.push(v.fromBufferAttribute(p,k).applyMatrix4(m.matrixWorld).clone())}});return o};
 for(const pad of pads){await M.setPart('shoulder.R',pad); await M.setPart('shoulder.L',pad);
  for(const w of mounts){await M.setPart('mount.R',w); await new Promise(r=>setTimeout(r,20));
   M.mixer.stopAllAction(); for(const b of Object.values(B))if(b.userData.stdPos)b.position.copy(b.userData.stdPos); M.mixer.update(0);M.keepShape();M.mech.updateMatrixWorld(true);
   const h=M.held['mount.R'], P=M.held['shoulder.R']; const poke=M.pokes(P,h);
   const a=pts(h); const o=new T(); h.getWorldPosition(o); const dir=h.userData.side?new T(-1,0,0):new T(0,1,0); const oo=h.userData.side?o.clone().add(new T(0,(window.MF_WEAPONS.shoulder.find(x=>x.id===w).size[2])*h.children[0].scale.x*.5,0)):o; const sp=M.surfaceHit(P,dir,oo); const o2=oo; const d=sp?Math.abs(o2.distanceTo(sp)-(h.userData.gap||0)):9;
   // also head / chest / backpack: points of weapon inside those parts' own boxes
   let other=[]; for(const s of ['head','chest','back']){const X=M.held[s]; if(!X)continue; X.updateMatrixWorld(true); const inv=X.matrixWorld.clone().invert(); const lb=new THREE_.Box3();
     X.traverse(m=>{if(m.isMesh){const p=m.geometry.attributes.position,Mx=inv.clone().multiply(m.matrixWorld);for(let k=0;k<p.count;k++)lb.expandByPoint(new T().fromBufferAttribute(p,k).applyMatrix4(Mx))}});
     const c=lb.getCenter(new T()), e=lb.getSize(new T()).multiplyScalar(.42); lb.set(c.clone().sub(e),c.clone().add(e));
     if(a.some(v=>lb.containsPoint(v.clone().applyMatrix4(inv)))) other.push(s)}
   if(poke||d>.2||other.length) out.push(pad+' + '+w+(h.userData.side?' [side]':' [top]')+(poke?' POKED':'')+(d>.2?' FLOAT '+d.toFixed(2):'')+(other.length?' hits '+other:''));
   else out.push('ok '+pad+' '+(h.userData.side?'side':'top'));
  }}
 return out}"""
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--use-gl=swiftshader','--enable-unsafe-swiftshader'])
        for preset in sys.argv[1:]:
            pg = await (await b.new_context()).new_page()
            errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
            async def route(r): await r.fulfill(path=os.path.join(ROOT,r.request.url.split('three@0.170.0/')[1]), content_type='application/javascript')
            await pg.route('https://cdn.jsdelivr.net/**', route)
            await pg.goto('file:///home/claude/mythic-forge/index.html'); await pg.evaluate("localStorage.clear()"); await pg.reload(); await pg.wait_for_timeout(2500)
            await pg.add_script_tag(content="import('https://cdn.jsdelivr.net/npm/three@0.170.0/build/three.module.js').then(m=>window.THREE_=m)", type='module'); await pg.wait_for_timeout(500)
            r = await pg.evaluate(JS, {'preset':preset})
            bad=[x for x in r if not x.startswith('ok')]; from collections import Counter
            print(preset, len(r)-len(bad),'/',len(r),'ok', errs[:1], dict(Counter(x.split()[1]+':'+x.split()[2] for x in r if x.startswith('ok'))))
            for x in bad: print('   ',x)
            await pg.close()
        await b.close()
asyncio.run(main())
