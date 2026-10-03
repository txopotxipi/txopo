// Inicializar AOS
AOS.init({offset:80,duration:700,easing:'ease-in-out'});

// Botón “Volver arriba”
const backToTop=document.getElementById('backToTop');
window.addEventListener('scroll',()=>{
  if(window.pageYOffset>300){
    backToTop.classList.add('show');
  }else{
    backToTop.classList.remove('show');
  }
});
backToTop.addEventListener('click',e=>{
  e.preventDefault();
  window.scrollTo({top:0,behavior:'smooth'});
});

// Poner año actual en footer
document.getElementById('year').textContent=new Date().getFullYear();

// Inicializar GLightbox si está disponible
if(typeof GLightbox!=='undefined'){
  GLightbox({selector:'.glightbox', touchNavigation:true, loop:true, autoplayVideos:false});
}

// Partículas en HERO con tsParticles
if(window.tsParticles){
  tsParticles.load('heroParticles',{
    background:{color:{value:'transparent'}},
    fullScreen:{enable:false},
    fpsLimit:60,
    interactivity:{
      events:{
        onHover:{enable:true,mode:'repulse'},
        onClick:{enable:true,mode:'push'},
        resize:true
      },
      modes:{
        repulse:{distance:80,duration:0.4},
        push:{quantity:3}
      }
    },
    particles:{
      color:{value:'#ffffff'},
      links:{enable:true,color:'#ffffff',distance:120,opacity:0.25,width:1},
      collisions:{enable:false},
      move:{enable:true,speed:1.2,direction:'none',random:false,straight:false,outModes:{default:'out'}},
      number:{density:{enable:true,area:800},value:45},
      opacity:{value:0.5},
      shape:{type:'circle'},
      size:{value:{min:1,max:3}}
    },
    detectRetina:true
  });
}

// Efecto tilt en tarjetas de galería
if(window.VanillaTilt){
  VanillaTilt.init(document.querySelectorAll('.gallery-item'),{max:8,speed:500,glare:true,'max-glare':0.2});
}

// Swiper carrusel destacado
if(window.Swiper){
  const swiper=new Swiper('.mySwiper',{
    slidesPerView:1,
    spaceBetween:10,
    loop:true,
    autoplay:{delay:2800,disableOnInteraction:false},
    pagination:{el:'.swiper-pagination',clickable:true},
    navigation:{nextEl:'.swiper-button-next',prevEl:'.swiper-button-prev'},
    breakpoints:{
      576:{slidesPerView:1},
      768:{slidesPerView:2},
      992:{slidesPerView:3}
    }
  });
}

// Contador regresivo al 31 de agosto
(function(){
  const el=document.getElementById('countdown');
  if(!el) return;
  const now=new Date();
  const targetYear= now.getMonth()>7 || (now.getMonth()===7 && now.getDate()>31) ? now.getFullYear()+1 : now.getFullYear();
  const target=new Date(targetYear,7,31,0,0,0,0); // 31 agosto
  function update(){
    const diff=target - new Date();
    if(diff<=0){ el.textContent='¡Es hoy!'; return; }
    const d=Math.floor(diff/86400000);
    const h=Math.floor((diff%86400000)/3600000);
    const m=Math.floor((diff%3600000)/60000);
    const s=Math.floor((diff%60000)/1000);
    el.textContent=`Faltan ${d}d ${h}h ${m}m ${s}s para el 31 de agosto`;
  }
  update();
  setInterval(update,1000);
})();

// Configuración dinámica de WhatsApp y horario
(function(){
  const wa=document.querySelector('.wa-float');
  if(!wa) return;
  const phone=wa.getAttribute('data-wa-phone')||'';
  const text=encodeURIComponent(wa.getAttribute('data-wa-text')||'Hola');
  const open=parseInt(wa.getAttribute('data-wa-open')||'9',10);
  const close=parseInt(wa.getAttribute('data-wa-close')||'21',10);
  const now=new Date();
  const hour=now.getHours();
  const inSchedule = hour>=open && hour<close;
  if(!inSchedule){
    wa.style.display='none';
    return;
  }
  wa.href=`https://wa.me/${phone}?text=${text}`;
})();

// Aviso de cookies (consentimiento simple)
(function(){
  const KEY='cookieConsentAccepted';
  const banner=document.getElementById('cookieBanner');
  const btn=document.getElementById('acceptCookies');
  if(!banner||!btn) return;
  try{
    const accepted=localStorage.getItem(KEY)==='1';
    if(!accepted){
      banner.classList.add('show');
    }
    btn.addEventListener('click',()=>{
      localStorage.setItem(KEY,'1');
      banner.classList.remove('show');
    });
  }catch(e){
    // Si localStorage falla, mostrar banner en cada visita
    banner.classList.add('show');
    btn.addEventListener('click',()=>{banner.classList.remove('show');});
  }
})();