(()=>{
  const reduced=matchMedia('(prefers-reduced-motion: reduce)').matches;
  const nav=document.getElementById('siteNav'),toggle=document.getElementById('navToggle');
  if(nav&&toggle)toggle.addEventListener('click',()=>nav.classList.toggle('open'));
  document.querySelectorAll('#navLinks a').forEach(a=>a.addEventListener('click',()=>nav?.classList.remove('open')));

  const items=[...document.querySelectorAll('.reveal')];
  if(reduced){items.forEach(x=>x.classList.add('in'))}
  else if('IntersectionObserver'in window){
    const io=new IntersectionObserver(entries=>entries.forEach(e=>{if(e.isIntersecting){e.target.classList.add('in');io.unobserve(e.target)}}),{threshold:.12});
    items.forEach(x=>io.observe(x));
  }else items.forEach(x=>x.classList.add('in'));

  if(!reduced){
    document.addEventListener('pointermove',e=>{
      const card=e.target.closest?.('.tilt');if(!card)return;
      const r=card.getBoundingClientRect(),x=(e.clientX-r.left)/r.width-.5,y=(e.clientY-r.top)/r.height-.5;
      card.style.transform=`perspective(900px) rotateY(${x*5}deg) rotateX(${-y*5}deg) translateY(-2px)`;
    });
    document.addEventListener('pointerout',e=>{const card=e.target.closest?.('.tilt');if(card)card.style.transform=''})
  }
})();
