// Original Basata scene kinds (v1 geometry + motion), now rendered through engine v2.
export function buildOld(K, ctx){
const {THREE,S,P,o,scene,add,box,ext,mat,A,cl,eo,eio,seg,drop,rnd,RoundedBoxGeometry}=ctx;
function archShape(w,h,t) { // outer rect with semicircle opening
  const s=new THREE.Shape(); s.moveTo(-w/2,0); s.lineTo(w/2,0); s.lineTo(w/2,h); s.lineTo(-w/2,h); s.lineTo(-w/2,0);
  const ow=w/2-t, oh=h-t-ow; const hole=new THREE.Path(); hole.moveTo(-ow,0); hole.lineTo(-ow,oh); hole.absarc(0,oh,ow,Math.PI,0,true); hole.lineTo(ow,0); hole.lineTo(-ow,0);
  s.holes.push(hole); return s; }
if (K==='arches') {           // colonnade receding
  const n=o.n??7;
  for (let i=0;i<n;i++){ const a=ext(archShape(2.2,3.6,.28),.35, (o.accent===i)?'b':'a'); a.position.set(o.x??-1.2, 0, -i*2.4); a.rotation.y=Math.PI/2; }
  S.sweep=S.sweep??.5;
} else if (K==='arch') {      // single arch, glow behind
  const a=ext(archShape(o.w??3.2,o.h??4.6,.45),.6,'a'); a.position.set(0,0,-.3);
  if (o.glow) { const g=new THREE.Mesh(new THREE.PlaneGeometry(2.2,3.4), new THREE.MeshBasicMaterial({color:P.b})); g.position.set(0,1.7,-.6); scene.add(g); const c0=new THREE.Color(P.bg), c1=new THREE.Color(P.b); A.push(t=>{g.material.color.copy(c0).lerp(c1,eo(seg(t,.05,.6)))}); }
  if (o.obj) { const ob=box(.5,.5,.5,'b',0,null,1.4,.06); A.push(t=>{ob.position.z=1.4+2.5*(1-eio(seg(t,.1,.7)))}); }
} else if (K==='stairs') {
  const n=o.n??9, sw=o.w??2.4;
  for (let i=0;i<n;i++) box(sw,.28*(i+1),.55,(o.top&&i===n-1)?'b':'a', o.x??0,null,-i*.55,.01);
  if (o.obj||S.anim) { const s=add(new THREE.SphereGeometry(.22,64,48),'b'); s.position.set(o.x??0,.28*n+.22,-(n-1)*.55); s.visible=!!o.obj;
    A.push(t=>{ s.visible=true; const u=seg(t,.08,.78)*(n-1); const k=Math.floor(u), f=u-k; const st=Math.min(k+ (f>.5?1:0), n-1);
      const z0=-k*.55, z1=-Math.min(k+1,n-1)*.55, y0=.28*(k+1), y1=.28*(Math.min(k+1,n-1)+1); const ef=eio(f);
      s.position.z=z0+(z1-z0)*ef; s.position.y=y0+(y1-y0)*ef+.22+Math.sin(f*Math.PI)*.22; if(u>=n-1){s.position.z=-(n-1)*.55;s.position.y=.28*n+.22;} }); }
} else if (K==='monolith') {
  box(o.w??1.1,o.h??4.2,o.d??.45,o.k??'c',o.x??.6,null,0,.02); S.sweep=S.sweep??.7;
  if (o.small) { const sm=box(.35,.35,.35,'b',-1.6,null,1.2,.04); A.push(t=>{const u=eio(seg(t,.1,.75)); sm.position.x=-1.6-2.2*(1-u); sm.rotation.y=(1-u)*1.2;}); }
} else if (K==='bars') {
  const hs=o.hs??[.6,1.0,1.5,2.1,2.9,3.8];
  hs.forEach((h,i)=>{ const m=box(.62,h,.62,(i===hs.length-1||o.accent===i)?'b':'a', (i-(hs.length-1)/2)*.95, null, 0, .03);
    A.push(t=>{ const u=Math.max(.02,eo(seg(t,.06+i*.09,.42+i*.09))); m.scale.y=u; m.position.y=h*u/2; }); });
} else if (K==='cairn') {
  let y=0; const rs=o.rs??[1.0,.82,.66,.52,.38];
  rs.forEach((r,i)=>{ const g=new THREE.SphereGeometry(r,96,64); const m=add(g,(o.topb&&i===rs.length-1)?'b':(o.k??'a')); const sy=.42; m.scale.set(1,sy,1); m.position.set((rnd()-.5)*.12,y+r*sy,0); m.rotation.y=rnd()*3; const y0=m.position.y; A.push(t=>{ const u=seg(t,.04+i*.13,.04+i*.13+.24); m.visible=u>0; m.position.y=y0+drop(u)*2.4; }); y+=r*sy*2*.96; });
} else if (K==='door') {
  const f=new THREE.Shape(); const w=o.w??1.8,h=o.h??3.6,t=.22; f.moveTo(-w/2,0);f.lineTo(w/2,0);f.lineTo(w/2,h);f.lineTo(-w/2,h);f.lineTo(-w/2,0);
  const hp=new THREE.Path(); hp.moveTo(-w/2+t,0);hp.lineTo(w/2-t,0);hp.lineTo(w/2-t,h-t);hp.lineTo(-w/2+t,h-t);hp.lineTo(-w/2+t,0); f.holes.push(hp);
  const d=ext(f,.3,o.k??'a'); d.position.set(0,0,0);
  if (o.glow) { const g=new THREE.Mesh(new THREE.PlaneGeometry(w-2*t,h-t), new THREE.MeshBasicMaterial({color:P.b})); g.position.set(0,(h-t)/2,.05); scene.add(g);
    if (S.anim) { const piv=new THREE.Group(); piv.position.set(-w/2+t,0,.25); scene.add(piv); const lf=new THREE.Mesh(new RoundedBoxGeometry(w-2*t-.02,h-t-.02,.08,4,.02),mat(o.k??'a')); lf.castShadow=true; lf.position.set((w-2*t)/2,(h-t)/2,0); piv.add(lf);
      A.push(tt=>{ const u=eio(seg(tt,.12,.8)); piv.rotation.y=-u*1.75; lf.visible=u<.995; }); } }
  if (o.wall) { const wl=box(14,5,.3,'a',0,null,-.25,.0); }
} else if (K==='window') {    // wall with opening, light patch on floor
  const s=new THREE.Shape(); s.moveTo(-9,0);s.lineTo(9,0);s.lineTo(9,7);s.lineTo(-9,7);s.lineTo(-9,0);
  const cols=o.cols??1; for(let i=0;i<cols;i++){ const cx=(i-(cols-1)/2)*1.6; const hp=new THREE.Path(); hp.moveTo(cx-.55,1.6);hp.lineTo(cx+.55,1.6);hp.lineTo(cx+.55,4.2);hp.absarc(cx,4.2,.55,0,Math.PI,false);hp.lineTo(cx-.55,1.6); s.holes.push(hp); }
  const wl=ext(s,.4,'a'); wl.position.set(0,0,-3);
  if (o.obj) box(.6,.6,.6,'b',o.ox??1.2,null,-1.2,.05);
  S.sweepX=1.6;
} else if (K==='path') {
  const p=new THREE.Mesh(new THREE.PlaneGeometry(.18,60), new THREE.MeshStandardMaterial({color:P.b, roughness:.9})); p.rotation.x=-Math.PI/2; p.position.set(o.px??0,.004,-26); p.receiveShadow=true; scene.add(p);
  const pm=box(.7,1.6,.7,o.k??'c',o.px??0,null,-14,.03); A.push(t=>{pm.position.z=-14-5*(1-eio(seg(t,.05,.85)));});
} else if (K==='grid') {      // cubes, one different
  const n=o.n??5, sp=.9;
  for(let i=0;i<n;i++)for(let j=0;j<n;j++){ const odd=(i===(o.oi??2)&&j===(o.oj??1)); if(o.missing&&odd) continue;
    const h=odd&&!o.missing?.9:.5; const m=box(.56,h,.56,odd?'b':'a',(i-(n-1)/2)*sp,null,(j-(n-1)/2)*sp-1,.04);
    const dly=(i+j)*.035; A.push(t=>{ const w=Math.sin(cl((t-.05-dly)/.25)*Math.PI)*.12; if(odd){ const u=eo(seg(t,.45,.8)); m.scale.y=(0.5+(h-.5)*u)/h; m.position.y=m.scale.y*h/2+w*.5; } else m.position.y=h/2+w; }); }
} else if (K==='ring') {
  const t=add(new THREE.TorusGeometry(o.R??1.5,o.tube??.16,64,220),o.k??'a'); t.position.set(o.rx??0,(o.R??1.5)+(o.tube??.16),0); A.push(tt=>{t.rotation.y=-(1-eio(seg(tt,0,.9)))*1.1;});
  if (o.obj) { const s=add(new THREE.SphereGeometry(.3,64,48),'b'); s.position.set(0,.3,1.6); A.push(tt=>{const u=eio(seg(tt,.15,.8)); s.position.x=-3*(1-u); s.rotation.z=3*(1-u)/.3;}); }
} else if (K==='balance') {
  const tri=new THREE.Shape(); tri.moveTo(-.5,0);tri.lineTo(.5,0);tri.lineTo(0,.8);tri.lineTo(-.5,0);
  const f=ext(tri,.5,'c'); f.position.set(0,0,-.25);
  const ang=o.ang??.12; const piv=new THREE.Group(); piv.position.set(0,.86,0); scene.add(piv);
  const plank=new THREE.Mesh(new RoundedBoxGeometry(5,.12,.7,6,.02),mat('a')); plank.castShadow=plank.receiveShadow=true; piv.add(plank);
  const b1=new THREE.Mesh(new RoundedBoxGeometry(.7,.7,.7,6,.05),mat('b')); b1.castShadow=true; b1.position.set(-1.9,.41,0); piv.add(b1);
  const s=new THREE.Mesh(new THREE.SphereGeometry(.22,64,48),mat('a')); s.castShadow=true; s.position.set(1.9,.28,0); piv.add(s);
  piv.rotation.z=ang; A.push(t=>{ const u=seg(t,.05,.85); piv.rotation.z=ang+(-.32-ang)*Math.cos(u*Math.PI*2.5)*Math.pow(1-u,1.6); });
} else if (K==='maze') {
  const walls=o.walls??[[-3,-3,6,0],[-3,-3,0,6],[3,-3,0,4],[-1.5,-1.5,4.5,0],[-1.5,-1.5,0,3],[-3,3,4.5,0],[0,0,3,0],[1.5,0,0,3],[-1.5,1.5,1.5,0]];
  walls.forEach(([x,z,dx,dz])=>{ const len=Math.max(Math.abs(dx),Math.abs(dz))+.2; const b=box(dx?len:.2,.5,dz?len:.2,'a',x+dx/2,null,z+dz/2,.02); });
  const s=add(new THREE.SphereGeometry(.25,64,48),'b'); s.position.set(-.75,.25,-.75);
  const wp=[[-2.25,2.25],[-2.25,-2.25],[.75,-2.25],[.75,-.75],[-.75,-.75]]; A.push(t=>{ const u=eio(seg(t,.05,.85))*(wp.length-1); const k=Math.min(Math.floor(u),wp.length-2), f=u-k; s.position.x=wp[k][0]+(wp[k+1][0]-wp[k][0])*f; s.position.z=wp[k][1]+(wp[k+1][1]-wp[k][1])*f; });
} else if (K==='prism') {
  box(1.6,.9,1.6,'a',0,null,0,.04);
  const g=new THREE.CylinderGeometry(.75,.75,1.6,3); const p=add(g,'glass'); p.position.set(0,.9+.8,0); p.rotation.y=.4;
  const beam=new THREE.Mesh(new THREE.PlaneGeometry(6,.25), new THREE.MeshBasicMaterial({color:P.b, transparent:true, opacity:.85})); beam.rotation.x=-Math.PI/2; beam.position.set(3.2,.005,1.2); beam.rotation.z=-.35; scene.add(beam);
  A.push(t=>{ p.rotation.y=.4-(1-eio(seg(t,0,.7)))*.9; const u=eo(seg(t,.55,.9)); beam.material.opacity=.85*u; beam.scale.x=Math.max(.01,u); beam.position.x=.2+3*u; });
} else if (K==='bridge') {
  box(3,1.2,3,'a',-3.6,null,0,.03); box(3,1.2,3,'a',3.6,null,0,.03);
  const curve=new THREE.EllipseCurve(0,1.2,2.4,1.1,0,Math.PI,false); const pts=curve.getPoints(80).map(p=>new THREE.Vector3(p.x,p.y,0));
  const tube=add(new THREE.TubeGeometry(new THREE.CatmullRomCurve3(pts),120,.07,16,false),'b'); const nI=tube.geometry.index.count;
  A.push(t=>{ const u=eio(seg(t,.12,.8)); tube.geometry.setDrawRange(0, Math.max(6,Math.floor(nI*u/6)*6)); });
} else if (K==='trio') {
  box(1.1,1.2,1.1,'a',-1.7,null,0,.03); box(1.1,1.9,1.1,'a',0,null,-.4,.03); box(1.1,.8,1.1,'a',1.7,null,.2,.03);
  const cube=box(.5,.5,.5,'c',-1.7,1.2+.25,0,.05); cube.rotation.y=.5;
  const cy=add(new THREE.CylinderGeometry(.28,.28,.6,64),'b'); cy.position.set(0,1.9+.3,-.4);
  const co=add(new THREE.ConeGeometry(.32,.7,64),'a'); co.position.set(1.7,.8+.35,.2);
  [cube,cy,co].forEach((m,i)=>{ const y0=m.position.y; A.push(t=>{ const u=seg(t,.1+i*.17,.1+i*.17+.3); m.visible=u>0; m.position.y=y0+drop(u)*2.2; }); });
} else if (K==='ribbon') {
  const pts=[]; for(let i=0;i<=60;i++){ const t=i/60; pts.push(new THREE.Vector3(-3+6*t, 1.4+Math.sin(t*Math.PI*2)*.8, Math.cos(t*Math.PI*2)*.9)); }
  const tube=add(new THREE.TubeGeometry(new THREE.CatmullRomCurve3(pts),300,.22,48,false),o.k??'b'); tube.scale.set(1,1,.35); A.push(t=>{ tube.rotation.x=(1-eio(seg(t,0,.9)))*.7; tube.rotation.y=(1-eio(seg(t,0,.9)))*-.25; });
} else if (K==='slabs') {     // leaning panels
  const n=o.n??5; for(let i=0;i<n;i++){ const s=box(1.6,3.2,.12,(o.accent===i)?'b':'a',(i-(n-1)/2)*1.05,null,-i*.2,.02); s.rotation.y=.5; const x0=s.position.x;
    A.push(t=>{ const u=eo(seg(t,.06+i*.1,.5+i*.1)); s.rotation.y=.5+(1-u)*1.07; s.position.y=1.6; s.visible=u>0; }); }
} else if (K==='seed') {      // tiny object, vast field
  const s=box(o.s??.3,o.s??.3,o.s??.3,o.k??'b',o.x??0,null,o.z??0,.04); const sy0=s.position.y; A.push(t=>{ const u=seg(t,.15,.5); s.visible=u>0; s.position.y=sy0+drop(u)*3; s.rotation.y=(1-cl(u))*.8; });
} else if (K==='sphere') {
  const sp=add(new THREE.SphereGeometry(o.r??.5,96,64),o.k??'b'); sp.position.set(o.x??0,o.r??.5,o.z??0);
} else if (K==='cube') {
  const cb=box(o.s??.8,o.s??.8,o.s??.8,o.k??'b',o.x??0,null,o.z??0,.04); cb.rotation.y=o.ry??.5;
} else if (K==='columns') {
  const n=o.n??6; for(let i=0;i<n;i++){ const cy=add(new THREE.CylinderGeometry(.32,.32,o.h??4,64), (o.accent===i)?'b':'a'); cy.position.set(o.x??-1.4, (o.h??4)/2, -i*2); const cy2=add(new THREE.CylinderGeometry(.32,.32,o.h??4,64),'a'); cy2.position.set(-(o.x??-1.4),(o.h??4)/2,-i*2); }
  const beam=box(3.4,.3,(n-1)*2+1,'a',0,(o.h??4)+.15,-(n-1),.02); S.dolly=S.dolly??.14;
}
}
