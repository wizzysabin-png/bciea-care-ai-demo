(()=>{const R=matchMedia('(prefers-reduced-motion:reduce)').matches,$=s=>[...document.querySelectorAll(s)],B=document.body;
const bar=Object.assign(document.createElement('div'),{className:'u-bar'}),gl=Object.assign(document.createElement('div'),{className:'u-glow'});B.append(bar,gl);
if(!R)addEventListener('pointermove',e=>gl.style.transform=`translate(${e.clientX}px,${e.clientY}px)`,{passive:true});
const FX=[['.category-card,.mini-media,.impact-item','flip'],['.step','left'],['.media-main,.video-shell,.cta','zoom']];
$('.reveal').forEach(el=>{const i=[...el.parentElement.children].indexOf(el);el.style.setProperty('--d',Math.min(i,8)*80+'ms');for(const[s,f]of FX)if(el.matches(s))el.dataset.fx=f});
const io=new IntersectionObserver(es=>es.forEach(e=>{if(!e.isIntersecting)return;io.unobserve(e.target);const t=e.target;
 if(t.classList.contains('u-gem'))t.classList.add('in');else setTimeout(()=>t.style.setProperty('--d','0ms'),1500);
 const n=t.querySelector&&t.querySelector('.impact-item strong');if(n&&!R)$('.impact-item strong').forEach(c=>{const m=c.textContent.match(/^(\d+)$/);if(!m)return;const T=+m[1],t0=performance.now();(function f(n){const p=Math.min((n-t0)/1400,1);c.textContent=Math.round(T*(1-Math.pow(1-p,3)));if(p<1)requestAnimationFrame(f)})(t0)})}),{threshold:.15});
$('.reveal').forEach(x=>io.observe(x));
/* floating gems on the public site */
const gems=[['.hero',{right:'4%',top:'14%'},46,.09],['#support',{left:'2%',top:'12%'},38,.12],['#media',{right:'3%',top:'30%'},58,.07],['#how',{left:'46%',top:'8%'},34,.14],['#safety',{left:'5%',top:'20%'},44,.1],['.u-map',{right:'5%',bottom:'8%'},52,.08]].map(([s,pos,z,k])=>{const h=document.querySelector(s);if(!h||!document.querySelector('.hero'))return;h.classList.add('u-host');
 const g=document.createElement('div');g.className='u-gem';g.style.setProperty('--z',z+'px');Object.assign(g.style,pos);g.innerHTML='<b>'+'<i></i>'.repeat(6)+'</b>';h.prepend(g);io.observe(g);return{g,h,k}}).filter(Boolean);
const PX=[['.hero-frame',-.04],['.float-a',-.08],['.float-b',-.13],['.float-c',-.06]].map(([s,k])=>[document.querySelector(s),k]).filter(a=>a[0]);
const nav=document.getElementById('siteNav');let tk=0;
const up=()=>{tk=0;const y=scrollY,m=document.documentElement.scrollHeight-innerHeight;bar.style.transform=`scaleX(${m>0?y/m:0})`;nav&&nav.classList.toggle('u-scrolled',y>20);if(R)return;
 PX.forEach(([e,k])=>e.style.translate=`0 ${y*k}px`);gems.forEach(({g,h,k})=>{const r=h.getBoundingClientRect();g.style.translate=`0 ${(r.top+r.height/2-innerHeight/2)*k}px`})};
addEventListener('scroll',()=>{if(!tk)tk=requestAnimationFrame(up)},{passive:true});up();
})();
