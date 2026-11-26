// Story previews load only while visible; the underlying photo is always available.
const storyPreviewState=(()=>{
 const motion=window.matchMedia('(prefers-reduced-motion: reduce)');
 const saving=Boolean(navigator.connection&&navigator.connection.saveData);
 const videos=new Set(),visible=new Set();let userPaused=false;
 const labels={ko:['썸네일 영상 일시정지','썸네일 영상 재생'],en:['Pause thumbnail videos','Play thumbnail videos'],ja:['サムネイル動画を一時停止','サムネイル動画を再生'],'zh-Hans':['暂停缩略图视频','播放缩略图视频']};
 const text=labels[document.documentElement.lang]||labels.en;
 function allowed(){return !motion.matches&&!saving&&!userPaused&&!document.hidden;}
 function syncControls(){
  document.querySelectorAll('.story-preview-toggle').forEach(button=>{
   button.hidden=motion.matches||saving;
   button.textContent=userPaused?text[1]:text[0];
   button.setAttribute('aria-pressed',String(userPaused));
  });
 }
 function stop(video){video.pause();video.classList.remove('is-playing');}
 async function play(video){
  if(!allowed()||!visible.has(video)||video.dataset.failed)return stop(video);
  if(!video.getAttribute('src')){video.src=video.dataset.src;video.load();}
  try{await video.play();if(allowed()&&visible.has(video)){video.classList.add('is-playing');}else{stop(video);}}
  catch{stop(video);}
 }
 function refresh(){for(const video of videos){if(!video.isConnected){stop(video);observer?.unobserve(video);videos.delete(video);visible.delete(video);}else{play(video);}}syncControls();}
 const observer='IntersectionObserver' in window?new IntersectionObserver(entries=>{
  for(const entry of entries){if(entry.isIntersecting&&entry.intersectionRatio>=0.15){visible.add(entry.target);play(entry.target);}else{visible.delete(entry.target);stop(entry.target);}}
 },{threshold:[0,0.15]}):null;
 function register(scope){
  refresh();
  scope.querySelectorAll('video.story-preview').forEach(video=>{
   if(videos.has(video))return;
   videos.add(video);video.muted=true;
   video.addEventListener('error',()=>{video.dataset.failed='true';stop(video);});
   if(observer)observer.observe(video);
  });syncControls();
 }
 motion.addEventListener('change',refresh);
 document.addEventListener('visibilitychange',refresh);
 return {register};
})();
function syncStoryPreviews(scope=document){storyPreviewState.register(scope);}
const heroVideo=document.querySelector('#hero-video');
const toggleVideo=document.querySelector('#video-toggle');
if(heroVideo&&toggleVideo){
 const motionPreference=window.matchMedia('(prefers-reduced-motion: reduce)');let userPaused=false;
 function syncHeroVideo(){const paused=heroVideo.paused;const label=paused?(toggleVideo.dataset.playLabel||'영상 재생'):(toggleVideo.dataset.pauseLabel||'영상 일시정지');toggleVideo.setAttribute('aria-label',label);toggleVideo.setAttribute('aria-pressed',String(paused));const icon=document.createElement('span');icon.setAttribute('aria-hidden','true');icon.textContent=paused?'▶':'Ⅱ';toggleVideo.replaceChildren(icon,document.createTextNode(' '+label));}
 async function playHero(){try{await heroVideo.play();}catch{}syncHeroVideo();}
 heroVideo.addEventListener('play',syncHeroVideo);heroVideo.addEventListener('pause',syncHeroVideo);
 toggleVideo.addEventListener('click',()=>{if(heroVideo.paused){userPaused=false;playHero();}else{userPaused=true;heroVideo.pause();}syncHeroVideo();});
 motionPreference.addEventListener('change',()=>{if(motionPreference.matches){heroVideo.autoplay=false;heroVideo.pause();}else if(!userPaused){heroVideo.autoplay=true;playHero();}});
 if(!motionPreference.matches){heroVideo.autoplay=true;playHero();}else{heroVideo.pause();syncHeroVideo();}
}
const postData=document.querySelector('#posts-data'),grid=document.querySelector('#story-grid');
if(postData&&grid){const posts=JSON.parse(postData.textContent);let category='전체';
 function renderPosts(){const selected=posts.filter(post=>category==='전체'||post.category===category);const visible=grid.dataset.all==='true'||category!=='전체'?selected:selected.slice(0,3);grid.replaceChildren();
  for(const post of visible){const link=document.createElement('a');link.className='story-card';link.href=post.url;const cat=document.createElement('span');cat.className='category';cat.textContent=post.category;const title=document.createElement('h3');title.textContent=post.title;const summary=document.createElement('p');summary.textContent=post.summary;if(post.thumbnail){
   const photo=document.createElement('img');
   photo.className='story-thumbnail';
   photo.src=post.thumbnail;
   photo.alt='';
   photo.loading='lazy';
   photo.decoding='async';
   if(post.preview){
    const media=document.createElement('span');media.className='story-media';
    const video=document.createElement('video');video.className='story-preview';
    video.muted=true;video.loop=true;video.playsInline=true;video.preload='none';
    video.poster=post.thumbnail;video.dataset.src=post.preview;
    video.setAttribute('aria-hidden','true');video.tabIndex=-1;
    media.append(photo,video);link.append(media);
   }else{link.append(photo);}
  }
  link.append(cat,title,summary);grid.append(link);}
  syncStoryPreviews(grid);
  const status=document.querySelector('#story-status');if(status)status.textContent=`${category} 글 ${visible.length}개 표시`;
 }
 for(const filter of document.querySelectorAll('[data-filter]'))filter.addEventListener('click',()=>{category=filter.dataset.filter;for(const button of document.querySelectorAll('[data-filter]')){const active=button===filter;button.classList.toggle('active',active);button.setAttribute('aria-pressed',String(active));}renderPosts();});renderPosts();
}

syncStoryPreviews();
