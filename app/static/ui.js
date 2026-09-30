(()=>{const still=matchMedia('(prefers-reduced-motion:reduce)').matches;
const c=document.getElementById('orb');
if(c){const x=c.getContext('2d'),P=[],N=700,d=devicePixelRatio||1;let W,H,mx=0,my=0,t=0;
const rs=()=>{W=c.width=c.offsetWidth*d;H=c.height=c.offsetHeight*d};rs();addEventListener('resize',rs);
for(let i=0;i<N;i++){const a=Math.acos(1-2*(i+.5)/N),b=Math.PI*(1+5**.5)*i;P.push([Math.sin(a)*Math.cos(b),Math.cos(a),Math.sin(a)*Math.sin(b)])}
addEventListener('pointermove',e=>{mx=e.clientX/innerWidth-.5;my=e.clientY/innerHeight-.5});
(function f(){if(!still)t+=.004;x.clearRect(0,0,W,H);const R=Math.min(W,H)*.36,ry=t+mx*1.2,rx=my*.8+.3,pulse=1+.03*Math.sin(t*12);
const q=P.map(([a,b,e])=>{let X=a*Math.cos(ry)-e*Math.sin(ry),Z=a*Math.sin(ry)+e*Math.cos(ry);const Y=b*Math.cos(rx)-Z*Math.sin(rx);Z=b*Math.sin(rx)+Z*Math.cos(rx);return[X,Y,Z]}).sort((a,b)=>a[2]-b[2]);
for(const[X,Y,Z]of q){const s=1/(1.8-Z*.5);x.fillStyle=`hsla(${325+Z*25},100%,${62+Z*16}%,${.2+.6*(Z+1)/2})`;x.beginPath();x.arc(W/2+X*R*s*1.6*pulse,H/2+Y*R*s*1.6*pulse,(1.1+1.9*(Z+1))*d*s,0,7);x.fill()}
requestAnimationFrame(f)})()}
let cur;document.addEventListener('pointermove',e=>{const n=e.target.closest&&e.target.closest('.tilt');if(cur&&cur!==n)cur.style.transform='';cur=n;if(!n||still)return;const r=n.getBoundingClientRect(),X=(e.clientX-r.left)/r.width-.5,Y=(e.clientY-r.top)/r.height-.5;n.style.transform=`perspective(800px) rotateY(${X*10}deg) rotateX(${-Y*10}deg) translateZ(6px)`});
})();
