# Weapon clip bot (Nov 22 2026): plays every move on a body and checks each weapon never goes into a body part or the floor.
# Run: python3 tools/bot/weapon_bot.py standard:0 squat:7   (preset:starter number). Needs playwright + chrome; three.js served from a local copy (ROOT).
# Checks: no weapon point inside any body part (boxes that turn with each part), none below the floor, and each weapon's grip sits on its hand / forearm / shoulder (no floating).
import asyncio, os, sys, json
from playwright.async_api import async_playwright
ROOT='/tmp/t/node_modules/three'
JS = r"""async ({preset})=>{
 const M=window.__mf,B=window.__bones,T=M.mech.position.constructor,W=window.MF_WEAPONS;
 await M.applyBuild(preset,'kit',{...window.MF_STARTERS[+(new URLSearchParams(location.search).get('s')||0)].parts}); await new Promise(r=>setTimeout(r,500)); const nHeld=Object.keys(M.held).length;
 M.renderer.setAnimationLoop(null);
 const pts=h=>{const out=[],v=new T();h.traverse(m=>{if(m.isMesh){const p=m.geometry.attributes.position;const st=Math.max(1,Math.floor(p.count/250));for(let k=0;k<p.count;k+=st)out.push(v.fromBufferAttribute(p,k).applyMatrix4(m.matrixWorld).clone())}});return out};
 const boxOf=h=>{const mn=new T(1e9,1e9,1e9),mx=new T(-1e9,-1e9,-1e9);h.traverse(m=>{if(m.isMesh){m.geometry.computeBoundingBox();const g=m.geometry.boundingBox.clone().applyMatrix4(m.matrixWorld);mn.min(g.min);mx.max(g.max)}});const c=mn.clone().add(mx).multiplyScalar(.5),e=mx.clone().sub(mn).multiplyScalar(.42);return [c.clone().sub(e),c.clone().add(e)]};
 const res={}; const THREE_BOX=function(h){const mn=new T(1e9,1e9,1e9),mx=new T(-1e9,-1e9,-1e9);h.traverse(m=>{if(m.isMesh){m.geometry.computeBoundingBox();const g=m.geometry.boundingBox.clone().applyMatrix4(m.matrixWorld);mn.min(g.min);mx.max(g.max)}});this.inside=p=>p.x>mn.x-.1&&p.x<mx.x+.1&&p.y>mn.y-.1&&p.y<mx.y+.1&&p.z>mn.z-.1&&p.z<mx.z+.1};
 const test=async(spot,w,own)=>{await M.setPart(spot,w.id); await new Promise(r=>setTimeout(r,30)); const hits={};
  {M.mixer.stopAllAction();for(const b of Object.values(B))if(b.userData.stdPos)b.position.copy(b.userData.stdPos);M.mixer.update(0);M.keepShape();M.mech.updateMatrixWorld(true);
   const kind=w.kind, holder=M.held[kind==='shield'?'forearm.R':kind==='mount'?'shoulder.R':'hand.R'];
   if(holder){const o=new T();M.held[spot].getWorldPosition(o);const b2=pts(holder);let d=9;for(const q of b2)d=Math.min(d,o.distanceTo(q));
    if(kind==='mount'){const wp=pts(M.held[spot]);for(const q of wp)for(const r of b2)d=Math.min(d,q.distanceTo(r))}   // shoulder weapons on a stand: the stand's feet touch the pad
    const bx=new THREE_BOX(holder); if(!bx.inside(o) && d>.2) hits['FLOATING grip '+d.toFixed(2)]=1}}
  for(const [name,act] of Object.entries(M.moves)){M.mixer.stopAllAction();act.reset();act.play();const dur=act.getClip().duration;
   for(let f=0;f<=12;f++){for(const b of Object.values(B))if(b.userData.stdPos)b.position.copy(b.userData.stdPos);
    act.time=dur*f/12;M.mixer.update(0);M.keepShape();M.mech.updateMatrixWorld(true);
    const P=pts(M.held[spot]);
    for(const [s,h] of Object.entries(M.held)){if(s===spot||own.includes(s)||/^(weapon|mount)/.test(s))continue;
     h.updateMatrixWorld(true);const inv=h.matrixWorld.clone().invert();
     if(!h.userData._lb){const lb={mn:new T(1e9,1e9,1e9),mx:new T(-1e9,-1e9,-1e9)},v=new T();h.traverse(m=>{if(m.isMesh){const p=m.geometry.attributes.position,Mx=inv.clone().multiply(m.matrixWorld);for(let k=0;k<p.count;k++){v.fromBufferAttribute(p,k).applyMatrix4(Mx);lb.mn.min(v);lb.mx.max(v)}}});
      const c=lb.mn.clone().add(lb.mx).multiplyScalar(.5),e=lb.mx.clone().sub(lb.mn).multiplyScalar(.42);h.userData._lb=[c.clone().sub(e),c.clone().add(e)]}
     const [a,b]=h.userData._lb,u=new T();
     if(P.some(v=>{u.copy(v).applyMatrix4(inv);return u.x>a.x&&u.x<b.x&&u.y>a.y&&u.y<b.y&&u.z>a.z&&u.z<b.z})){const k=name+':'+s;hits[k]=(hits[k]||0)+1}}
    if(P.some(v=>v.y<-.05)){const k=name+':floor';hits[k]=(hits[k]||0)+1}}}
  await M.setPart(spot,null); return hits};
 for(const w of W.hand) res[w.id]=await test('weapon.R',w,['hand.R','forearm.R']);
 for(const w of W.shoulder) res[w.id]=await test('mount.R',w,['shoulder.R']);
 res._held=nHeld; return res}"""
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--use-gl=swiftshader','--enable-unsafe-swiftshader'])
        for arg in sys.argv[1:]:
            preset, si = arg.split(':')
            pg = await (await b.new_context(viewport={'width':412,'height':915})).new_page()
            errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
            async def route(r): await r.fulfill(path=os.path.join(ROOT,r.request.url.split('three@0.170.0/')[1]), content_type='application/javascript')
            await pg.route('https://cdn.jsdelivr.net/**', route)
            await pg.goto('file:///home/claude/mythic-forge/index.html?s='+si); await pg.evaluate("localStorage.clear()"); await pg.reload(); await pg.wait_for_timeout(2500)
            r = await pg.evaluate(JS, {'preset':preset})
            n=r.pop("_held"); bad={k:v for k,v in r.items() if v}; print("parts on body:",n)
            print(arg, f"{len(r)-len(bad)}/{len(r)} clean", errs[:2])
            for k,v in bad.items(): print('   ',k, v)
            await pg.close()
        await b.close()
asyncio.run(main())
