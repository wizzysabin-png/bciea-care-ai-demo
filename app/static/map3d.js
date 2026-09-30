/* Rotating 3D Rwanda network map: village -> sector -> district hub -> AI core (Kigali).
   Outline & hub positions are STYLISED approximations; villages/traffic are an illustrative simulation, not patient data. */
(()=>{
const OUT=[[29.26,-1.70],[29.58,-1.39],[29.73,-1.39],[30.07,-1.43],[30.47,-1.06],[30.65,-1.25],[30.83,-1.55],[30.89,-1.95],[30.80,-2.35],[30.55,-2.41],[30.30,-2.38],[30.12,-2.42],[29.95,-2.62],[29.60,-2.81],[29.30,-2.84],[29.05,-2.73],[28.90,-2.50],[29.10,-2.35],[29.25,-2.15],[29.36,-2.05],[29.30,-1.85]].map(p=>[p[0]-29.9,p[1]+1.95]);
const HUBS=[["Kigali",30.06,-1.95],["Musanze",29.63,-1.50],["Rubavu",29.32,-1.72],["Gicumbi",30.10,-1.58],["Nyagatare",30.33,-1.30],["Rwamagana",30.43,-1.95],["Bugesera",30.25,-2.17],["Muhanga",29.75,-2.08],["Karongi",29.42,-2.05],["Huye",29.74,-2.60],["Rusizi",29.05,-2.50]].map(h=>[h[1]-29.9,h[2]+1.95,h[0]]);
let s=7;const rnd=()=>{s|=0;s=s+0x6D2B79F5|0;let t=Math.imul(s^s>>>15,1|s);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296};
const inside=(x,y)=>{let c=0;for(let i=0,j=OUT.length-1;i<OUT.length;j=i++){const[a,b]=OUT[i],[d,e]=OUT[j];if((b>y)!=(e>y)&&x<(d-a)*(y-b)/(e-b)+a)c=!c}return c};
const near=(p,L)=>L.reduce((m,q)=>Math.hypot(p[0]-q[0],p[1]-q[1])<Math.hypot(p[0]-m[0],p[1]-m[1])?q:m);
const V=[];while(V.length<260){const p=[rnd()*2.1-.75,rnd()*2-1.1];if(inside(p[0],p[1]))V.push(p)}
const SEC=V.filter((_,i)=>i%7==0);
const PATH=v=>{const sc=near(v,SEC),h=near(sc,HUBS);return h===HUBS[0]?[v,sc,h]:[v,sc,h,HUBS[0]]};
const LV={education:'#5ee6a8',needs_assessment:'#ffd166',urgent:'#ff9a5c',emergency:'#ff5d6c'};
const maps=[],GC=[];let total=0;
const count=()=>document.querySelectorAll('[data-rw-count]').forEach(e=>e.textContent=total.toLocaleString());
window.rwPing=lv=>{maps.forEach(m=>m.spawn(LV[lv]||'#ffd0e6',true))};
function init(cv){
 const x=cv.getContext('2d'),mini=cv.dataset.compact!=null,st={ang:.5,drag:0,vis:true,P:[],t:0,last:0};let W=0,H=0,D=1;
 const rs=()=>{D=Math.min(devicePixelRatio||1,2);W=cv.width=cv.clientWidth*D;H=cv.height=cv.clientHeight*D};
 const pj=(p,z=0)=>{const c=Math.cos(st.ang),n=Math.sin(st.ang),a=p[0]*c-p[1]*n,b=p[0]*n+p[1]*c,pt=.98,dp=b*Math.cos(pt)-z*Math.sin(pt),k=1/(1+dp*.17),U=Math.min(W/2.3,H/1.35);
  return[W/2+a*U*k,H*.56-(b*Math.sin(pt)+z*Math.cos(pt))*U*k,dp,k]};
 cv.style.touchAction='pan-y';let lx=0;
 cv.onpointerdown=e=>{st.drag=1;lx=e.clientX;cv.setPointerCapture(e.pointerId)};cv.onpointerup=()=>st.drag=0;
 cv.onpointermove=e=>{if(st.drag){st.ang+=(e.clientX-lx)*.008;lx=e.clientX}};
 new IntersectionObserver(e=>st.vis=e[0].isIntersecting).observe(cv);
 const still=matchMedia('(prefers-reduced-motion:reduce)').matches;
 const lift=(a,b,f,h)=>[a[0]+(b[0]-a[0])*f,a[1]+(b[1]-a[1])*f,.03+Math.sin(f*Math.PI)*h];
 const H3=[.16,.3,.5],lp=(a,b,f,h)=>{const q=lift(a,b,f,h);return pj([q[0],q[1]],q[2])};
 const m={spawn(col,big){if(st.P.length>40)return;st.P.push({p:PATH(V[rnd()*V.length|0]),t:0,col:col||'#ffd0e6',big})},
 draw(dt){if(cv.clientWidth*D!==W||cv.clientHeight*D!==H)rs();if(!W||!st.vis)return;
  if(!st.drag&&!still)st.ang+=dt*.00022;st.t+=dt;st.last+=dt;
  if(st.last>(mini?1800:420)&&!still){st.last=0;m.spawn(['#ffd0e6','#ffd0e6','#ff77b6','#5ee6a8'][rnd()*4|0])}
  x.clearRect(0,0,W,H);
  const g=x.createRadialGradient(W/2,H*.66,0,W/2,H*.66,W*.42);g.addColorStop(0,'rgba(255,47,146,.22)');g.addColorStop(1,'transparent');x.fillStyle=g;x.fillRect(0,0,W,H);
  const top=OUT.map(p=>pj(p,0)),walls=OUT.map((a,i)=>{const b=OUT[(i+1)%OUT.length];return{q:[pj(a,0),pj(b,0),pj(b,-.16),pj(a,-.16)],d:(pj(a)[2]+pj(b)[2])/2,sh:.5+.5*Math.sin(Math.atan2(b[1]-a[1],b[0]-a[0])-st.ang)}}).sort((a,b)=>b.d-a.d);
  for(const w of walls){x.beginPath();w.q.forEach((p,i)=>i?x.lineTo(p[0],p[1]):x.moveTo(p[0],p[1]));x.closePath();x.fillStyle=`rgba(${120+w.sh*80|0},16,${90+w.sh*40|0},${.35+.4*w.sh})`;x.fill()}
  x.beginPath();top.forEach((p,i)=>i?x.lineTo(p[0],p[1]):x.moveTo(p[0],p[1]));x.closePath();
  const f=x.createLinearGradient(0,H*.2,0,H*.85);f.addColorStop(0,'rgba(255,119,182,.34)');f.addColorStop(1,'rgba(111,69,214,.30)');x.fillStyle=f;x.fill();
  x.shadowColor='#ff2f92';x.shadowBlur=18*D;x.strokeStyle='#ff9ccb';x.lineWidth=2*D;x.stroke();x.shadowBlur=0;
  x.lineWidth=D;const core=HUBS[0];
  for(const h of HUBS.slice(1)){x.beginPath();for(let i=0;i<=16;i++){const q=lp(h,core,i/16,.5);i?x.lineTo(q[0],q[1]):x.moveTo(q[0],q[1])}x.strokeStyle='rgba(255,180,220,.22)';x.stroke()}
  for(const v of V){const q=pj(v,.02);x.fillStyle='rgba(255,215,235,.55)';x.beginPath();x.arc(q[0],q[1],(mini?1:1.5)*D*q[3],0,7);x.fill()}
  for(const v of SEC){const q=pj(v,.03);x.fillStyle='#ff77b6';x.beginPath();x.arc(q[0],q[1],(mini?2:3)*D*q[3],0,7);x.fill()}
  for(const h of HUBS.slice(1)){const q=pj(h,.04);x.strokeStyle='#fff';x.lineWidth=1.6*D;x.beginPath();x.arc(q[0],q[1],(mini?4:6)*D*q[3],0,7);x.stroke();
   if(!mini){x.fillStyle='rgba(255,255,255,.85)';x.font=`${11*D}px Inter,sans-serif`;x.fillText(h[2],q[0]+9*D,q[1]+4*D)}}
  for(let i=st.P.length-1;i>=0;i--){const o=st.P[i];o.t+=dt*.0011;const seg=o.t|0,n=o.p.length-1;if(seg>=n){st.P.splice(i,1);if(o.p.length){total++;count()}continue}
   const f=o.t-seg,hh=H3[seg],q=lp(o.p[seg],o.p[seg+1],f,hh),b=lp(o.p[seg],o.p[seg+1],Math.max(0,f-.14),hh);
   x.strokeStyle=o.col;x.lineWidth=2*D;x.shadowColor=o.col;x.shadowBlur=10*D;x.beginPath();x.moveTo(b[0],b[1]);x.lineTo(q[0],q[1]);x.stroke();x.fillStyle='#fff';x.beginPath();x.arc(q[0],q[1],(o.big?4:2.4)*D,0,7);x.fill();x.shadowBlur=0}
  const c=pj(core,.05),r=(mini?7:11)*D,ph=(st.t/700)%1;
  for(const k of[0,.5]){const p=(ph+k)%1;x.strokeStyle=`rgba(255,47,146,${.6*(1-p)})`;x.lineWidth=2*D;x.beginPath();x.arc(c[0],c[1],r*(1+p*3.2),0,7);x.stroke()}
  x.shadowColor='#ff2f92';x.shadowBlur=26*D;x.fillStyle='#ff2f92';x.beginPath();x.arc(c[0],c[1],r,0,7);x.fill();x.shadowBlur=0;x.fillStyle='#fff';x.beginPath();x.arc(c[0],c[1],r*.4,0,7);x.fill();
  if(!mini){x.fillStyle='#fff';x.font=`700 ${12*D}px Inter,sans-serif`;x.fillText('AI CORE · KIGALI',c[0]+r+8*D,c[1]-r)}}};
 maps.push(m);rs();for(let i=0;i<6;i++)m.spawn();
}
document.querySelectorAll('canvas.rwmap').forEach(init);
let lt=performance.now();(function f(n){const dt=Math.min(n-lt,50);lt=n;maps.forEach(m=>m.draw(dt));requestAnimationFrame(f)})(lt);
const of=window.fetch;window.fetch=function(...a){const p=of.apply(this,a);if(String(a[0]).includes('/api/chat'))p.then(r=>r.clone().json()).then(j=>window.rwPing(j.triage_level)).catch(()=>{});return p};
})();
