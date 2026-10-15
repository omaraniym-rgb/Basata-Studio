// Basata scene kinds, set 2. Each object means something; each moves with meaning when animated.
export function buildNew(K, ctx){
const {THREE,S,P,o,scene,add,box,sph,cyl,lathe,tube,ext,mat,A,cl,eo,eio,seg,drop,rnd,RoundedBoxGeometry}=ctx;
const V3=(x,y,z)=>new THREE.Vector3(x,y,z);
const grp=(x=0,y=0,z=0)=>{const g=new THREE.Group(); g.position.set(x,y,z); scene.add(g); return g;};
const meshIn=(g,geo,k)=>{const m=new THREE.Mesh(geo,mat(k)); m.castShadow=m.receiveShadow=true; g.add(m); return m;};
const lerp=(a,b,u)=>a+(b-a)*u;

switch(K){

case 'keystone': { // arch of stones; the orange keystone drops in last: what holds it all
  const n=o.n??11, R=o.R??2.2, th=o.th??.62, d=o.d??.9; const blocks=[];
  for(let i=0;i<n;i++){ const a0=Math.PI*i/n, a1=Math.PI*(i+1)/n, gap=.012;
    const sh=new THREE.Shape(); const pts=[[R,a0+gap],[R+th,a0+gap],[R+th,a1-gap],[R,a1-gap]];
    sh.moveTo(Math.cos(a0+gap)*R,Math.sin(a0+gap)*R);
    for(let k=0;k<=8;k++){const a=a0+gap+(a1-a0-2*gap)*k/8; sh.lineTo(Math.cos(a)*(R+th),Math.sin(a)*(R+th));}
    for(let k=8;k>=0;k--){const a=a0+gap+(a1-a0-2*gap)*k/8; sh.lineTo(Math.cos(a)*R,Math.sin(a)*R);}
    const mid=i===Math.floor(n/2); const m=ext(sh,d,mid?'b':'a',.015); m.position.set(0,o.lift??.0,-d/2); blocks.push([m,mid]); }
  box(R*2+th*2+.6,.0001,.0001,'a',0,-5); // no-op spacer
  const pier=(x)=>box(th+.02,o.pier??.0001,d,'a',x,null,0,.02); if(o.pier) { pier(-(R+th/2)); pier(R+th/2); blocks.forEach(([m])=>m.position.y=o.pier); }
  blocks.forEach(([m,mid],i)=>{ const y0=m.position.y; A.push(t=>{ if(mid){ const u=seg(t,.55,.9); m.position.y=y0+drop(u)*3.2; m.visible=u>0; } else { const u=eo(seg(t,.02+i*.035,.3+i*.035)); m.position.y=y0+(1-u)*.0; m.scale.set(1,1,Math.max(.001,u)); } }); });
  S.sweep=S.sweep??.25; break; }

case 'untangle': { // a knot relaxing into one clean line
  const N=220; const knot=(u)=>{ const a=u*Math.PI*2*1; const p=2,q=3, r=Math.cos(q*a)+2.2; return [r*Math.cos(p*a)*.55, (Math.sin(q*a)*.6)+1.6, r*Math.sin(p*a)*.55]; };
  const line=(u)=>[lerp(-3.2,3.2,u), 1.6+Math.sin(u*Math.PI)*.0, 0];
  let m=null; const build=(k)=>{ const pts=[]; for(let i=0;i<=N;i++){ const u=i/N; const a=knot(u), b=line(u); pts.push(V3(lerp(a[0],b[0],k),lerp(a[1],b[1],k),lerp(a[2],b[2],k))); }
    const g=new THREE.TubeGeometry(new THREE.CatmullRomCurve3(pts,false),600,o.r??.11,24,false); if(m){ m.geometry.dispose(); m.geometry=g; } else { m=new THREE.Mesh(g,mat(o.k??'b')); m.castShadow=true; scene.add(m);} };
  build(S.anim?0:(o.state??.42)); A.push(t=>build(S.anim?eio(seg(t,.1,.9)):(o.state??.42))); break; }

case 'domino': { // a chain: the first push moves everything
  const n=o.n??9, gap=o.gap??.62; const tiles=[];
  for(let i=0;i<n;i++){ const piv=grp(-((n-1)*gap)/2+i*gap,0,0); piv.position.z=Math.sin(i*.5)*.0; const m=meshIn(piv,new RoundedBoxGeometry(.16,1.2,.7,4,.02),(i===n-1&&o.lastb)?'b':(i===0?'b':'a')); m.position.set(.08,.6,0); tiles.push(piv); }
  const fall=(u)=>-Math.min(1.16, u*1.16);
  tiles.forEach((p,i)=>{ A.push(t=>{ const st=o.state??(S.anim?t:.62); const u=cl((st*1.15-i*.1)/.12); p.rotation.z=(i===n-1&&o.lastb)?0:fall(eio(u))*(i<n-1?1:1); }); });
  break; }

case 'cradle': { // newton's cradle: energy passes through, nothing wasted
  const n=5, r=.3, top=2.6; const frame=(x,z)=>cyl(.04,.04,top,'m',x,null,z,24);
  [-1.2,1.2].forEach(x=>{frame(x*1.4,-.7); frame(x*1.4,.7);}); const bar=(z)=>{ const b=cyl(.04,.04,3.4,'m',0,top,z,24); b.rotation.z=Math.PI/2; }; bar(-.7); bar(.7);
  const balls=[]; for(let i=0;i<n;i++){ const g=grp((i-(n-1)/2)*r*2.02,top,0); const rope=new THREE.BufferGeometry().setFromPoints([V3(0,0,-.7),V3(0,-1.7,0),V3(0,0,.7)]);
    const ln=new THREE.Line(rope,new THREE.LineBasicMaterial({color:0x8a857d})); g.add(ln); const b=meshIn(g,new THREE.SphereGeometry(r,96,64),i===0?'b':'m'); b.position.y=-1.7-r*.0; balls.push(g); }
  balls[0].rotation.z=-(o.lift??.55);
  A.push(t=>{ const ph=t*2.2*Math.PI; const s=Math.sin(ph); balls[0].rotation.z=s<0? s*(o.lift??.55):0; balls[n-1].rotation.z=s>0? s*(o.lift??.55):0; });
  break; }

case 'hourglass': { // time: what lasts is built slowly
  const prof=[]; for(let i=0;i<=40;i++){ const u=i/40, y=u*3; const w=.12+.9*Math.pow(Math.abs(u-.5)*2,1.6); prof.push([w,y]); }
  const glass=lathe(prof,'glass',0,.18,0); glass.castShadow=false;
  cyl(1.25,1.25,.18,o.wood?'w':'c',0,.09); cyl(1.25,1.25,.18,o.wood?'w':'c',0,3.27);
  [0,1,2,3].forEach(i=>{ const a=i*Math.PI/2+Math.PI/4; cyl(.05,.05,3,o.wood?'w':'c',Math.cos(a)*1.08,1.68,Math.sin(a)*1.08,24); });
  const sandTop=lathe([[0,0],[.8,0],[.12,-.0]],'b'); const top=grp(0,1.68,0); const topCone=meshIn(top,new THREE.ConeGeometry(.75,1.0,96),'b'); topCone.rotation.x=Math.PI; topCone.position.y=.62;
  const bot=meshIn(grp(0,.18,0),new THREE.ConeGeometry(.85,.7,96),'b'); bot.position.y=.35; sandTop.visible=false;
  const stream=cyl(.025,.025,1.4,'b',0,.9);
  A.push(t=>{ const u=S.anim?t:(o.state??.55); topCone.scale.set(1-u*.75,1-u*.85,1-u*.75); topCone.position.y=.62-u*.4; bot.scale.set(.35+u*.65,.25+u*.75,.35+u*.65); bot.position.y=.35*(.25+u*.75); stream.visible=u<.98; });
  break; }

case 'lens': { // focus: one thing, seen clearly
  const n=o.n??7, sp=.42; for(let i=0;i<n;i++)for(let j=0;j<n;j++){ const odd=i===(o.oi??4)&&j===(o.oj??3); box(.26,.26,.26,odd?'b':'a',(i-(n-1)/2)*sp,null,(j-(n-1)/2)*sp,.03); }
  const g=grp(0,1.3,0); const ring=meshIn(g,new THREE.TorusGeometry(.95,.07,32,160),'m'); ring.rotation.x=Math.PI/2;
  const disc=meshIn(g,new THREE.CylinderGeometry(.92,.92,.08,96),'glass'); disc.castShadow=false;
  const handle=meshIn(g,new THREE.CylinderGeometry(.08,.09,1.7,32),'c'); handle.rotation.z=Math.PI/2; handle.position.set(1.85,0,0); handle.rotation.y=-.5; handle.position.z=.75;
  const tx=((o.oi??4)-(n-1)/2)*sp, tz=((o.oj??3)-(n-1)/2)*sp;
  A.push(t=>{ const u=eio(seg(t,.05,.85)); g.position.x=lerp(-1.8,tx,u); g.position.z=lerp(1.2,tz,u); g.position.y=lerp(1.6,1.15,u); }); break; }

case 'spotlight': { // one chosen among many
  const n=o.n??9; for(let i=0;i<n;i++){ const a=i/n*Math.PI*2, r=2.3+((i*7)%3)*.35; const isB=i===0; if(!isB) sph(.26,'a',Math.cos(a)*r,null,Math.sin(a)*r-1); }
  const star=sph(.42,'b',0,null,-1);
  const sp=new THREE.SpotLight(0xfff0dc, 40, 0, .23, .35, 0); sp.position.set(0,9,-.2); sp.target=star; sp.castShadow=true; sp.shadow.mapSize.set(2048,2048); scene.add(sp);
  const cone=new THREE.Mesh(new THREE.ConeGeometry(2.1,9,64,1,true), new THREE.MeshBasicMaterial({color:0xfff2e0, transparent:true, opacity:.06, depthWrite:false, side:THREE.DoubleSide})); cone.position.set(0,4.5,-1); scene.add(cone);
  A.push(t=>{ const u=eo(seg(t,.1,.6)); sp.intensity=40*u; cone.material.opacity=.06*u; }); break; }

case 'fork': { // a choice: two roads, one taken
  const w=.55; const road=(pts,k)=>{ const sh=new THREE.Shape(); const L=pts.length; const left=[], right=[];
    for(let i=0;i<L;i++){ const p=pts[i], q=pts[Math.min(i+1,L-1)], pp=pts[Math.max(i-1,0)]; const dx=q[0]-pp[0], dz=q[1]-pp[1], ln=Math.hypot(dx,dz)||1; left.push([p[0]-dz/ln*w/2,p[1]+dx/ln*w/2]); right.push([p[0]+dz/ln*w/2,p[1]-dx/ln*w/2]); }
    sh.moveTo(...left[0]); left.forEach(p=>sh.lineTo(...p)); right.reverse().forEach(p=>sh.lineTo(...p));
    const m=add(new THREE.ExtrudeGeometry(sh,{depth:.06,bevelEnabled:false}),k); m.rotation.x=Math.PI/2; m.position.y=.06; return m; };
  const stem=[]; for(let i=0;i<=10;i++) stem.push([0,6-i*.6]);
  const L1=[], R1=[]; for(let i=0;i<=20;i++){ const u=i/20; L1.push([-Math.pow(u,1.6)*3.4, -u*7]); R1.push([Math.pow(u,1.6)*3.4, -u*7]); }
  road(stem,'a'); road(L1,o.pick==='L'?'b':'a'); road(R1,o.pick==='L'?'a':'b');
  const ball=sph(.22,'c',0,.28,4); const path=[...stem.map(p=>[p[0],p[1]]), ...(o.pick==='L'?L1:R1).slice(1).map(p=>[p[0],p[1]])];
  A.push(t=>{ const u=eio(seg(t,.05,.95))*(path.length-1)*(S.anim?1:(o.state??.42)); const k=Math.min(Math.floor(u),path.length-2), f=u-k; ball.position.x=lerp(path[k][0],path[k+1][0],f); ball.position.z=-lerp(path[k][1],path[k+1][1],f); });
  break; }

case 'target': { // aim: everything points to one centre
  const rings=o.rings??5; for(let i=rings;i>=1;i--){ const r=i*.62; const m=cyl(r,r,.08+(rings-i)*.07,(i%2)?'a':(o.alt??'a'),0,null,0,128); m.material=mat((i%2)?'a':'t'); }
  const ball=sph(.28,'b',0,.08+(rings-1)*.07+.28,0); const y0=ball.position.y;
  A.push(t=>{ const u=seg(t,.15,.6); ball.visible=u>0; ball.position.y=y0+drop(u)*3; }); break; }

case 'sculpt': { // remove until only the essential is left
  const n=o.n??7, s=.36, R=(n-1)/2*s; const cubes=[]; const core=sph(R*.92,'b',0,R+s/2+.02,0);
  for(let i=0;i<n;i++)for(let j=0;j<n;j++)for(let k=0;k<n;k++){ const x=(i-(n-1)/2)*s, y=(j)*s+s/2+.02, z=(k-(n-1)/2)*s; const d=Math.hypot(x,y-(R+s/2),z); if(d<R*.62) continue;
    const m=box(s*.96,s*.96,s*.96,'a',x,y,z,.02); cubes.push([m,d, rnd()]); }
  cubes.forEach(([m,d,r])=>{ const y0=m.position.y; const when=.15+(1-(d/(R*1.8)))*.0+r*.55; A.push(t=>{ const st=S.anim?t:(o.state??.6); const u=cl((st-when)/.18); m.visible=u<1; m.position.y=y0-u*0; m.scale.setScalar(Math.max(.001,1-eio(u))); }); });
  break; }

case 'pages': { // one page, lifted from the pile: the plan that fits
  for(let i=0;i<(o.n??14);i++){ const m=box(2.1,.022,2.9,'p',(rnd()-.5)*.06,.011+i*.024,(rnd()-.5)*.06,.004); m.rotation.y=(rnd()-.5)*.05; }
  const g=new THREE.PlaneGeometry(2.1,2.9,30,40); const pos=g.attributes.position; const flat=pos.array.slice();
  const sheet=new THREE.Mesh(g,mat('p')); sheet.material.side=THREE.DoubleSide; sheet.castShadow=true; sheet.rotation.x=-Math.PI/2; scene.add(sheet);
  const line=box(1.2,.004,.06,'b',0,0,0,.002); line.visible=!!o.mark;
  const curl=(u)=>{ for(let i=0;i<pos.count;i++){ const x=flat[i*3], y=flat[i*3+1]; pos.setZ(i, Math.pow((y+1.45)/2.9,2)*.55*u); } pos.needsUpdate=true; g.computeVertexNormals(); };
  A.push(t=>{ const u=S.anim?eio(seg(t,.1,.8)):(o.state??.6); const h=lerp(.36,1.4+(o.h??0),u); sheet.position.set(lerp(0,.6,u),h,lerp(0,.4,u)); sheet.rotation.z=lerp(0,-.35,u); sheet.rotation.x=-Math.PI/2+lerp(0,.22,u); curl(u); line.position.set(sheet.position.x,h+.05,sheet.position.z+.6); line.visible=!!o.mark&&u>.9; });
  break; }

case 'tunnel': { // nested frames, one point at the end
  const n=o.n??8; for(let i=0;i<n;i++){ const s=3.6-i*.0, z=-i*1.5; const sh=new THREE.Shape(); sh.moveTo(-s/2,0);sh.lineTo(s/2,0);sh.lineTo(s/2,s);sh.lineTo(-s/2,s);sh.lineTo(-s/2,0);
    const h=new THREE.Path(), t2=.18; h.moveTo(-s/2+t2,t2);h.lineTo(s/2-t2,t2);h.lineTo(s/2-t2,s-t2);h.lineTo(-s/2+t2,s-t2);h.lineTo(-s/2+t2,t2); sh.holes.push(h);
    const m=ext(sh,.18,'a'); m.position.set(0,0,z); }
  const b=sph(.3,'b',0,null,-(n-1)*1.5-.8); A.push(t=>{ const u=eio(seg(t,.05,.9)); b.position.z=lerp(-(n-1)*1.5-4,-(n-1)*1.5-.8,u); }); S.dolly=S.dolly??.22; break; }

case 'bricks': { // consistency: every brick the same, one carrying the colour
  const rows=o.rows??9, cols=o.cols??7, bw=.84, bh=.36, bd=.42; let pick=null;
  for(let r=0;r<rows;r++)for(let c=0;c<cols;c++){ const off=(r%2)*bw/2; const x=(c-(cols-1)/2)*bw+off-bw/4, y=bh/2+r*bh;
    const isB=(r===(o.pr??5)&&c===(o.pc??3)); const m=box(bw-.035,bh-.035,bd,isB?'b':'a',x,y,0,.02); if(isB) pick=m; }
  A.push(t=>{ const u=eio(seg(t,.2,.85)); pick.position.z=u*(o.push??.3); }); break; }

case 'jenga': { // one piece moved, the tower still stands
  const lv=o.lv??10, L=1.8, w=.56, h=.34; let pull=null;
  for(let l=0;l<lv;l++)for(let i=0;i<3;i++){ const isP=(l===(o.pl??4)&&i===1); if(o.gap && l===o.pl && i===0) continue;
    const m=box(l%2?w:L,h-.02,l%2?L:w,isP?'b':'a',l%2?(i-1)*w*1.02:0,h/2+l*h,l%2?0:(i-1)*w*1.02,.02); if(isP) pull=m; }
  A.push(t=>{ const u=eio(seg(t,.15,.85)); if((o.pl??4)%2) pull.position.z=u*1.3; else pull.position.x=u*1.3; }); break; }

case 'vase': { // one stem: less, chosen well
  const prof=[[0,0],[.42,0],[.5,.08],[.62,.6],[.66,1.2],[.5,1.8],[.24,2.2],[.2,2.5],[.26,2.62],[.22,2.62]];
  const v=lathe(prof,o.vk??'a',o.x??0,o.y??0,o.z??0);
  if (o.plinth) { box(1.6,o.plinth,1.6,'t',o.x??0,null,o.z??0,.02); v.position.y=o.plinth; }
  const base=v.position.y+2.5; const pts=[[0,0,0],[.06,.8,.02],[.18,1.6,.05],[.42,2.3,.1],[.7,2.8,.16]].map(p=>[p[0]+(o.x??0),p[1]+base,p[2]+(o.z??0)]);
  const stem=tube(pts,.018,'c'); const bud=sph(.11,'b',pts[4][0],pts[4][1],pts[4][2]);
  A.push(t=>{ const u=eo(seg(t,.2,.8)); stem.scale.y=1; bud.scale.setScalar(Math.max(.01,u)); }); break; }

case 'bowl': { // contentment: one thing, held
  const prof=[]; for(let i=0;i<=30;i++){ const a=i/30*Math.PI/2; prof.push([Math.sin(a)*1.6, (1-Math.cos(a))*.9]); } for(let i=30;i>=0;i--){ const a=i/30*Math.PI/2; prof.push([Math.sin(a)*1.5+.0, (1-Math.cos(a))*.9+.08]); }
  lathe(prof,o.bk??'a',0,.0,0); const b=sph(.36,'b',.0,.46,0); const y0=b.position.y;
  A.push(t=>{ const u=seg(t,.1,.7); b.visible=u>0; b.position.y=y0+drop(u)*2.6; b.position.x=Math.sin(u*9)*(1-u)*.25; }); break; }

case 'chair': { // a single chair in a room full of light: space to think
  const g=grp(o.x??.4,0,o.z??-.6); g.rotation.y=o.ry??-.5; const k=o.ck??'w';
  const leg=(x,z,h)=>{ const m=meshIn(g,new RoundedBoxGeometry(.07,h,.07,3,.015),k); m.position.set(x,h/2,z); };
  leg(-.42,-.42,.92); leg(.42,-.42,.92); leg(-.42,.42,1.9); leg(.42,.42,1.9);
  const seat=meshIn(g,new RoundedBoxGeometry(.95,.07,.95,3,.02),k); seat.position.y=.95;
  [1.3,1.55,1.8].forEach(y=>{ const r=meshIn(g,new RoundedBoxGeometry(.9,.06,.05,3,.015),k); r.position.set(0,y,.42); });
  if (o.ball) { const b=sph(.18,'b',(o.x??.4)-1.2,null,(o.z??-.6)+.6); A.push(t=>{ b.position.x=(o.x??.4)-1.2-(1-eio(seg(t,.1,.8)))*2; b.rotation.z=(1-eio(seg(t,.1,.8)))*11; }); }
  break; }

case 'frame': { // empty frame: room for the picture you choose
  const fw=o.fw??2.0, fh=o.fh??2.6, t2=.12; const sh=new THREE.Shape(); sh.moveTo(-fw/2,0);sh.lineTo(fw/2,0);sh.lineTo(fw/2,fh);sh.lineTo(-fw/2,fh);sh.lineTo(-fw/2,0);
  const h=new THREE.Path(); h.moveTo(-fw/2+t2,t2);h.lineTo(fw/2-t2,t2);h.lineTo(fw/2-t2,fh-t2);h.lineTo(-fw/2+t2,fh-t2);h.lineTo(-fw/2+t2,t2); sh.holes.push(h);
  const f=ext(sh,.08,o.fk??'w'); f.position.set(o.x??-.5,o.y??1.4,(S.back??-3.2)+.04);
  if (o.lean) { f.position.set(o.x??-.5,0,(S.back??-3.2)+.5); f.rotation.x=-.12; }
  if (o.obj) { box(.34,.34,.34,'b',(o.x??-.5)+1.7,null,(S.back??-3.2)+.7,.04); }
  break; }

case 'sundial': { // time passes; the shape stays
  cyl(1.7,1.8,.3,o.dk??'t',0,null,0,128); for(let i=0;i<12;i++){ const a=i/12*Math.PI*2; box(.04,.012,.26,'c',Math.cos(a)*1.45,.306,Math.sin(a)*1.45,.004).rotation.y=-a+Math.PI/2; }
  const gn=new THREE.Shape(); gn.moveTo(0,0); gn.lineTo(1.2,0); gn.lineTo(0,1.1); gn.lineTo(0,0); const m=ext(gn,.06,'b',.01); m.position.set(-.5,.3,-.03);
  S.sweep=S.sweep??.9; break; }

case 'shelf': { // curation: one object earns the space
  const sh=box(o.sw??3.2,.08,.5,o.sk??'w',o.x??0,o.y??1.6,(S.back??-3.2)+.27,.01);
  const y=(o.y??1.6)+.04; const objs=o.objs??['vase'];
  if (objs.includes('vase')) lathe([[0,0],[.18,0],[.24,.25],[.22,.5],[.12,.7],[.1,.8],[.13,.84]],'a',(o.x??0)+.7,y,(S.back??-3.2)+.27);
  if (objs.includes('ball')) sph(.16,'b',(o.x??0)-.6,y+.16,(S.back??-3.2)+.27);
  if (objs.includes('book')) { box(.12,.7,.5,'c',(o.x??0)-1.1,y+.35,(S.back??-3.2)+.27,.01); }
  break; }

case 'ripple': { // one action, felt across the surface
  const g=new THREE.PlaneGeometry(40,40,280,280); const pos=g.attributes.position;
  const water=new THREE.Mesh(g,new THREE.MeshPhysicalMaterial({color:o.wcol??P.gr, roughness:.12, clearcoat:1, clearcoatRoughness:.05, metalness:0})); water.rotation.x=-Math.PI/2; water.position.y=.02; water.receiveShadow=true; scene.add(water);
  const b=sph(.3,'b',0,.3,0);
  const wave=(u)=>{ const R=u*9; for(let i=0;i<pos.count;i++){ const x=pos.getX(i), y=pos.getY(i); const d=Math.hypot(x,y); const k=d-R; pos.setZ(i, Math.exp(-k*k*.25)*Math.cos(k*3.2)*.09*(1-u*.6)*(d<R+1.5?1:0)); } pos.needsUpdate=true; g.computeVertexNormals(); };
  wave(S.anim?0:(o.state??.4)); A.push(t=>{ if(!S.anim){ wave(o.state??.4); b.position.y=.06; return; } const u=seg(t,.05,.35); b.position.y=.0+drop(u)*3+.06; wave(seg(t,.3,1)*.9+.08); }); break; }

case 'growth': { // steady growth: each step a little bigger
  const n=o.n??6; for(let i=0;i<n;i++){ const r=.14+i*.11, x=(i-(n-1)/2)*.95+(i*i*.012); const m=sph(r,i===n-1?'b':'a',x,null,0); const y0=m.position.y; A.push(t=>{ const u=eo(seg(t,.05+i*.1,.4+i*.1)); m.scale.setScalar(Math.max(.001,u)); m.position.y=r*u; }); }
  break; }

case 'glasscube': { // transparency: nothing hidden
  const g=box(o.s??1.8,o.s??1.8,o.s??1.8,'frost',0,null,0,.06); g.castShadow=true;
  const b=sph(.36,'b',0,(o.s??1.8)/2,0); A.push(t=>{ b.position.y=(o.s??1.8)/2+Math.sin(t*Math.PI*2)*.06; g.rotation.y=(1-eio(t))*.4; }); break; }

case 'tightrope': { // balance: focus on the line
  const pole=(x)=>{ cyl(.05,.06,2.4,'c',x,null,0,32); }; pole(-3.2); pole(3.2);
  const rope=tube([[-3.2,2.38,0],[0,2.2,0],[3.2,2.38,0]],.018,'c');
  const b=sph(.22,'b',0,2.2+.04+.22,0); A.push(t=>{ const u=eio(seg(t,.05,.9)); b.position.x=lerp(-2.6,0,u); b.rotation.z=-lerp(-2.6,0,u)/.22; b.position.y=2.2+.24+Math.abs(lerp(-2.6,0,u))*.02; }); break; }

case 'cord': { // connection: two points, one line
  box(.9,1.0,.9,'a',-2.4,null,0,.04); box(.9,1.6,.9,'a',2.4,null,-.4,.04);
  const pts=[]; for(let i=0;i<=20;i++){ const u=i/20; pts.push([lerp(-2.4,2.4,u), lerp(1.0,1.6,u)-Math.sin(u*Math.PI)*.9+.02, lerp(0,-.4,u)]); }
  const m=tube(pts,.05,'b'); const nI=m.geometry.index.count; A.push(t=>{ const u=eio(seg(t,.1,.85)); m.geometry.setDrawRange(0, Math.max(6,Math.floor(nI*u/6)*6)); }); break; }

case 'unfold': { // structure, opened up: see how it is made
  const s=1.0, th=.05; const base=box(s,th,s,'a',0,th/2,0,.01); const faces=[];
  const mk=(axis,sign,k)=>{ const piv=grp(axis==='x'?sign*s/2:0,th,axis==='z'?sign*s/2:0); const m=meshIn(piv,new RoundedBoxGeometry(s,th,s,3,.01),k);
    m.position.set(axis==='x'?sign*s/2:0,0,axis==='z'?sign*s/2:0); faces.push([piv,axis,sign]); return piv; };
  mk('x',1,'a'); mk('x',-1,'a'); mk('z',1,'a'); const back=mk('z',-1,'a');
  const lidP=new THREE.Group(); lidP.position.set(0,0,-s); back.add(lidP); const lid=new THREE.Mesh(new RoundedBoxGeometry(s,th,s,3,.01),mat('b')); lid.castShadow=lid.receiveShadow=true; lid.position.set(0,0,-s/2); lidP.add(lid);
  A.push(t=>{ const st=S.anim?(1-t):(o.state??.35); const a=eio(cl(st))*Math.PI/2; faces.forEach(([p,ax,sg])=>{ if(ax==='x') p.rotation.z=sg*a; else p.rotation.x=-sg*a; }); lidP.rotation.x=a; });
  break; }

case 'dune': { // patience: a long walk, a clear mark
  const m=box(o.w??.5,o.h??2.6,o.w??.5,o.k??'c',o.x??1.2,null,o.z??-6,.02); m.position.y=(o.h??2.6)/2-.4;
  if (o.ball) { const b=sph(.16,'b',(o.x??1.2)-1.1,null,(o.z??-6)+1.2); b.position.y=-.15; }
  S.sweep=S.sweep??.15; break; }

case 'beacon': { // a light that guides, turning slowly
  cyl(.45,.62,3.2,'a',0,null,0,96); cyl(.5,.5,.12,'c',0,3.26,0); const lamp=cyl(.36,.36,.5,'glass',0,3.57,0); const cap=new THREE.Mesh(new THREE.ConeGeometry(.5,.45,96),mat('b')); cap.position.y=4.05; cap.castShadow=true; scene.add(cap);
  const bulb=new THREE.PointLight(0xffb070,6,0,0); bulb.position.y=3.57; scene.add(bulb);
  const beam=new THREE.Mesh(new THREE.ConeGeometry(1.6,14,48,1,true),new THREE.MeshBasicMaterial({color:0xffd9b0,transparent:true,opacity:.07,depthWrite:false,side:THREE.DoubleSide})); beam.rotation.z=Math.PI/2; beam.position.set(7,3.57,0); const bg=grp(0,0,0); bg.add(beam);
  A.push(t=>{ bg.rotation.y=(o.rot??-.6)+t*1.2; }); bg.rotation.y=o.rot??-.6; break; }

case 'spiral': { // proportion: growth that keeps its shape
  const pts=[]; const phi=1.618; for(let i=0;i<=260;i++){ const a=i/260*Math.PI*4.2; const r=.06*Math.pow(phi,a*2/Math.PI); pts.push([Math.cos(a)*r, .06, Math.sin(a)*r]); }
  const m=tube(pts,.05,o.k??'b'); const b=sph(.1,'c',pts[0][0],.1,pts[0][2]);
  const nI=m.geometry.index.count; A.push(t=>{ const u=eio(seg(t,.05,.9)); m.geometry.setDrawRange(0,Math.max(6,Math.floor(nI*u/6)*6)); }); break; }

case 'keyhole': { // access: the way in is small and exact
  const s=new THREE.Shape(); s.moveTo(-8,0);s.lineTo(8,0);s.lineTo(8,7);s.lineTo(-8,7);s.lineTo(-8,0);
  const h=new THREE.Path(); h.moveTo(-.22,1.4); h.lineTo(.22,1.4); h.lineTo(.14,2.4); h.absarc(0,2.65,.36,-1.18,Math.PI+1.18,false); h.lineTo(-.22,1.4); s.holes.push(h);
  const w=ext(s,.5,'a'); w.position.set(0,0,-1.5); const glow=new THREE.Mesh(new THREE.PlaneGeometry(1.4,2.2),new THREE.MeshBasicMaterial({color:P.b})); glow.position.set(0,2.2,-1.6); scene.add(glow);
  const k=grp(-.0,0,1.2); const ring=meshIn(k,new THREE.TorusGeometry(.22,.06,24,64),'b'); ring.rotation.x=Math.PI/2; ring.position.set(0,.06,0); const shaft=meshIn(k,new RoundedBoxGeometry(.9,.08,.1,3,.02),'b'); shaft.position.set(.6,.06,0); const bit=meshIn(k,new RoundedBoxGeometry(.1,.08,.24,3,.02),'b'); bit.position.set(.98,.06,.1);
  k.rotation.y=o.kr??.6; A.push(t=>{ k.position.x=lerp(-1.5,-.4,eio(seg(t,.1,.8))); }); break; }

case 'ladder': { // step by step toward the light
  const g=grp(o.x??.6,0,(S.back??-3.2)+.9); g.rotation.x=-.28; const k=o.lk??'w';
  [-.38,.38].forEach(x=>{ const r=meshIn(g,new RoundedBoxGeometry(.07,4.2,.07,3,.015),k); r.position.set(x,2.1,0); });
  for(let i=0;i<9;i++){ const s=meshIn(g,new RoundedBoxGeometry(.76,.05,.06,3,.015),i===8?'b':k); s.position.set(0,.35+i*.45,0); } break; }

case 'compass': { // direction: settle on one heading
  cyl(1.5,1.55,.22,o.ck??'t',0,null,0,128); cyl(1.32,1.32,.03,'p',0,.235,0,128);
  for(let i=0;i<4;i++){ const a=i*Math.PI/2; box(.05,.01,.22,'c',Math.cos(a)*1.12,.255,Math.sin(a)*1.12,.004).rotation.y=-a+Math.PI/2; }
  const g=grp(0,.29,0); const nShape=new THREE.Shape(); nShape.moveTo(0,-1); nShape.lineTo(.09,0); nShape.lineTo(0,1); nShape.lineTo(-.09,0); nShape.lineTo(0,-1);
  const nd=new THREE.Mesh(new THREE.ExtrudeGeometry(nShape,{depth:.03,bevelEnabled:false}),mat('b')); nd.rotation.x=-Math.PI/2; nd.castShadow=true; g.add(nd); cyl(.06,.06,.06,'m',0,.31,0,32);
  const fin=o.head??.7; A.push(t=>{ const u=seg(t,.0,.9); g.rotation.y=fin+Math.cos(u*Math.PI*4)*Math.pow(1-u,1.5)*1.2; }); g.rotation.y=fin; break; }

case 'sort': { // chaos on one side, order on the other
  const shapes=[]; for(let i=0;i<12;i++){ const x=-2.2+(rnd()-.5)*1.6, z=(rnd()-.5)*1.6; const t=i%3; let m; if(t===0) m=box(.42,.42,.42,'a',x,null,z,.04); else if(t===1) m=sph(.23,'a',x,null,z); else m=cyl(.2,.2,.45,'a',x,null,z,48); m.rotation.y=rnd()*3; if(t===0){ m.rotation.z=rnd()*.6; m.position.y=.3; } shapes.push(m); }
  for(let i=0;i<5;i++){ const m=box(.42,.42,.42,i===4?'b':'a',.9+i*.52,null,0,.04); }
  break; }

case 'ziggurat': { // a wide base: built to last
  const tiers=o.tiers??5; for(let i=0;i<tiers;i++){ const w=3.6-i*.62; box(w,.42,w,i===tiers-1&&o.topb?'b':'a',0,.21+i*.42,0,.02); }
  if (o.ball) sph(.2,'b',0,tiers*.42+.2,0); break; }

case 'pillars': { // three pillars carry everything above them
  const n=o.n??3, h=o.h??2.8; for(let i=0;i<n;i++){ const x=(i-(n-1)/2)*1.25; cyl(.26,.3,h,i===(o.pb??1)?'b':'a',x,null,0,96); }
  box((n-1)*1.25+1.1,.3,1.1,'a',0,h+.15,0,.02); box((n-1)*1.25+1.4,.18,1.4,'a',0,.09,0,.02); break; }

case 'plane': { // an idea, launched
  const g=grp(o.x??0,o.y??2.2,o.z??0); const geo=new THREE.BufferGeometry();
  const v=[0,0,1.4, -.9,0,-.7, 0,-.02,-.6,   0,0,1.4, 0,-.02,-.6, .9,0,-.7,   0,0,1.4, 0,-.02,-.6, 0,-.32,-.55,  0,0,1.4, 0,-.32,-.55, 0,-.02,-.6];
  geo.setAttribute('position',new THREE.Float32BufferAttribute(v,3)); geo.computeVertexNormals(); const m=new THREE.Mesh(geo,mat(o.k??'p')); m.material.side=THREE.DoubleSide; m.castShadow=true; g.add(m);
  g.rotation.set(o.rx??-.12,o.ry??.7,o.rz??.18); g.scale.setScalar(o.sc??2.2);
  A.push(t=>{ const u=eio(seg(t,0,1)); g.position.x=(o.x??0)+lerp(-3,0,u); g.position.y=(o.y??2.2)+Math.sin(u*Math.PI)*.4; g.position.z=(o.z??0)+lerp(2,0,u); }); break; }

case 'orbit': { // a clear centre, everything else in its orbit
  const c=sph(o.R??.7,'b',0,(o.y??1.8),0); c.position.y=o.y??1.8; c.castShadow=true;
  const rings=[1.6,2.4]; rings.forEach((r,i)=>{ const t=add(new THREE.TorusGeometry(r,.012,16,256),'c'); t.position.y=o.y??1.8; t.rotation.x=Math.PI/2+(i?.18:-.1); });
  const s1=sph(.14,'a',0,o.y??1.8,0), s2=sph(.2,'a',0,o.y??1.8,0);
  A.push(t=>{ const a=t*Math.PI*1.2+(o.ph??.8); s1.position.set(Math.cos(a)*1.6,(o.y??1.8)+Math.sin(a)*1.6*Math.sin(-.1),Math.sin(a)*1.6*Math.cos(-.1)); const b=-t*Math.PI*.7+2.4; s2.position.set(Math.cos(b)*2.4,(o.y??1.8)+Math.sin(b)*2.4*Math.sin(.18),Math.sin(b)*2.4*Math.cos(.18)); }); break; }

case 'precarious': { // one decision, holding everything
  const c=box(1.2,1.2,1.2,'a',0,null,0,.03); const g=grp(0,1.2,0); const t=meshIn(g,new RoundedBoxGeometry(2.8,.08,.6,3,.02),o.tk??'w'); t.position.y=.04; const b=new THREE.Mesh(new THREE.SphereGeometry(.24,64,48),mat('b')); b.castShadow=true; b.position.set(1.15,.32,0); g.add(b); const b2=new THREE.Mesh(new RoundedBoxGeometry(.5,.5,.5,4,.04),mat('a')); b2.castShadow=true; b2.position.set(-1.0,.33,0); g.add(b2);
  A.push(tt=>{ const u=seg(tt,.05,.9); g.rotation.z=Math.sin(u*Math.PI*3)*Math.pow(1-u,1.5)*.08; }); break; }

case 'monument': { // a single tall form, light moving across it
  const m=box(o.w??1.2,o.h??4.4,o.d??1.2,o.k??'a',o.x??0,null,o.z??0,.02); m.rotation.y=o.ry??.6;
  if(o.ball) sph(.18,'b',(o.x??0)+1.3,null,(o.z??0)+.9);
  S.sweep=S.sweep??.6; break; }

case 'stepping': { // stepping stones across still water
  const water=new THREE.Mesh(new THREE.PlaneGeometry(60,60),new THREE.MeshPhysicalMaterial({color:o.wcol??0xbfc6c2, roughness:.08, clearcoat:1})); water.rotation.x=-Math.PI/2; water.position.y=.0; water.receiveShadow=true; scene.add(water);
  const pts=[[-2.4,3],[-1.5,1.8],[-.4,.8],[.4,-.4],[1.3,-1.6],[1.6,-3]]; pts.forEach((p,i)=>{ const m=cyl(.48-i*.02,.52-i*.02,.18,i===pts.length-1?'b':(o.sk??'t'),p[0],.06,p[1],96); const y0=m.position.y; A.push(t=>{ const u=eo(seg(t,.05+i*.12,.3+i*.12)); m.position.y=lerp(-.3,y0,u); }); });
  break; }

default: return false;
}
return true;
}
