(async () => {
  const $ = id => document.getElementById(id);
  const board = $('board'), viewport = $('viewport'), question = $('question');
  const stages = [...document.querySelectorAll('[data-step]')];
  const revealItems = [...document.querySelectorAll('[data-reveal]')];
  const leftCards = [...document.querySelectorAll('[data-from]')];
  let step = 0, scale = 1, tx = 0, ty = 0, notes = true, panelOpen = false;
  let drag = null;
  const clamp = (v, a, b) => Math.max(a, Math.min(b, v));
  const isolated = target => target.closest('.question,.study-content,button,select,input,textarea,a,summary,[contenteditable]');
  function renderCamera() {
    board.style.transform = `translate(${tx}px,${ty}px) scale(${scale})`;
    $('zoom-label').textContent = `${Math.round(scale * 100)}%`;
  }
  function available() {
    const top = document.querySelector('.topbar').getBoundingClientRect().bottom + 16;
    return {w: viewport.clientWidth - (panelOpen ? question.getBoundingClientRect().width : 0), h: viewport.clientHeight - top, top};
  }
  function boardBounds(el) {
    let rect = el.getBoundingClientRect();
    const origin = board.getBoundingClientRect();
    if(el.matches('li')) {
      const walker = document.createTreeWalker(el, NodeFilter.SHOW_TEXT), range = document.createRange(), rects = [];
      while(walker.nextNode()) {
        if(!walker.currentNode.textContent.trim()) continue;
        range.selectNodeContents(walker.currentNode);
        rects.push(...range.getClientRects());
      }
      if(rects.length) {
        const left = Math.min(...rects.map(r=>r.left)), top = Math.min(...rects.map(r=>r.top));
        rect = {left,top,width:Math.max(...rects.map(r=>r.right))-left,height:Math.max(...rects.map(r=>r.bottom))-top};
      }
    }
    return {x:(rect.left-origin.left)/scale, y:(rect.top-origin.top)/scale, w:rect.width/scale, h:rect.height/scale};
  }
  function placeNote(index) {
    const stage = stages[index], note = stage.querySelector('.study');
    if(!note) return;
    const key = stage.dataset.noteTarget;
    let anchor = key === 'reveal' ? [...document.querySelectorAll(`[data-reveal="${index}"]`)].at(-1) : null;
    if(key?.startsWith('entity:')) anchor = board.querySelector(`[data-entity-id="${key.slice(7)}"] [data-model-from="${index}"] li:last-child`);
    if(key?.startsWith('node:')) anchor = stage.querySelector(`[data-node-id="${key.slice(5)}"]`);
    if(!anchor && stage.classList.contains('pre-design')) anchor = [...document.querySelectorAll('[data-reveal]')].filter(el => Number(el.dataset.reveal) <= index).sort((a,b)=>Number(a.dataset.reveal)-Number(b.dataset.reveal)).at(-1);
    if(anchor?.matches('[data-entity-id]')) {
      const version = [...anchor.querySelectorAll('[data-model-from]')].find(el => Number(el.dataset.modelFrom) <= index && index < Number(el.dataset.modelUntil));
      anchor = version?.querySelector('li:last-child') || anchor.querySelector('strong');
    }
    anchor ||= stage.querySelector('figure') || stage.querySelector('h2');
    if(anchor.matches('[data-node-id]')) anchor = anchor.querySelector('[data-replica-layer="0"]') || anchor;
    const a = boardBounds(anchor), parent = boardBounds(stage), n = boardBounds(note);
    const cards = leftCards.filter(card => Number(card.dataset.from) <= index);
    const early = stage.classList.contains('pre-design');
    const main = stage.querySelector('.stage-main');
    const obstacles = cards.map(boardBounds);
    if(!early) obstacles.push(boardBounds(main));
    const right = Math.max(0, ...obstacles.map(r=>r.x+r.w));
    const gap = 40;
    const candidates = [
      {x:a.x+a.w+gap,y:a.y},
      {x:a.x-n.w-gap,y:a.y},
      {x:a.x+(a.w-n.w)/2,y:a.y+a.h+gap},
      {x:a.x+(a.w-n.w)/2,y:a.y-n.h-gap},
      {x:right+gap,y:a.y+(a.h-n.h)/2},
    ].map(c=>({...c,x:Math.max(40,c.x),y:Math.max(40,c.y),w:n.w,h:n.h}));
    const overlaps = (c,r) => c.x < r.x+r.w+16 && c.x+c.w+16 > r.x && c.y < r.y+r.h+16 && c.y+c.h+16 > r.y;
    const score = c => Math.hypot(c.x+c.w/2-a.x-a.w/2,c.y+c.h/2-a.y-a.h/2) + Math.max(0,(c.y+c.h-40)*16/9-Math.max(right,c.x+c.w))*2;
    const choices = candidates.filter(c=>!obstacles.some(r=>overlaps(c,r))).sort((a,b)=>score(a)-score(b));
    const chosen = choices[0] || {x:right+gap,y:Math.max(40,a.y),w:n.w,h:n.h};
    note.style.left = `${chosen.x-parent.x}px`;
    note.style.top = `${chosen.y-parent.y}px`;
    const noteRight = chosen.x >= a.x+a.w;
    const noteLeft = chosen.x+chosen.w <= a.x;
    const targetGap = 12;
    let start, end, bend;
    if(noteRight || noteLeft) {
      start = {x:noteRight?a.x+a.w+targetGap:a.x-targetGap,y:a.y+a.h/2};
      end = {x:noteRight?chosen.x:chosen.x+chosen.w,y:clamp(start.y,chosen.y+20,chosen.y+chosen.h-20)};
      bend = {x:(start.x+end.x)/2,y:start.y};
    } else {
      const below = chosen.y >= a.y+a.h;
      start = {x:a.x+a.w/2,y:below?a.y+a.h+targetGap:a.y-targetGap};
      end = {x:clamp(start.x,chosen.x+20,chosen.x+chosen.w-20),y:below?chosen.y:chosen.y+chosen.h};
      bend = {x:start.x,y:(start.y+end.y)/2};
    }
    const point = p => `${p.x-parent.x} ${p.y-parent.y}`;
    const horizontal = noteRight || noteLeft;
    let route = horizontal
      ? `M${point(start)} C${point(bend)} ${point({x:bend.x,y:end.y})} ${point(end)}`
      : `M${point(start)} C${point(bend)} ${point({x:end.x,y:bend.y})} ${point(end)}`;
    const blocking = key?.startsWith('node:') ? [...stage.querySelectorAll('[data-node-id]')]
      .filter(el=>!el.contains(anchor)).map(boardBounds)
      .filter(r=>r.x+r.w > Math.min(start.x,end.x) && r.x < Math.max(start.x,end.x)
        && r.y < Math.max(start.y,end.y)+12 && r.y+r.h > Math.min(start.y,end.y)-12) : [];
    if(horizontal && blocking.length) {
      const upper = Math.min(start.y,end.y,...blocking.map(r=>r.y))-32;
      const lower = Math.max(start.y,end.y,...blocking.map(r=>r.y+r.h))+32;
      const laneY = Math.abs(upper-start.y)+Math.abs(upper-end.y) < Math.abs(lower-start.y)+Math.abs(lower-end.y) ? upper : lower;
      const sign = noteRight ? 1 : -1;
      const points = [start,{x:start.x+16*sign,y:start.y},{x:start.x+16*sign,y:laneY},
        {x:end.x-24*sign,y:laneY},{x:end.x-24*sign,y:end.y},end];
      route = `M${point(start)}`;
      for(let i=1;i<points.length-1;i++) {
        const prev=points[i-1], at=points[i], next=points[i+1];
        const before=Math.hypot(at.x-prev.x,at.y-prev.y), after=Math.hypot(next.x-at.x,next.y-at.y);
        const radius=Math.min(24,before/2,after/2);
        if(!radius) continue;
        const enter={x:at.x+(prev.x-at.x)*radius/before,y:at.y+(prev.y-at.y)*radius/before};
        const leave={x:at.x+(next.x-at.x)*radius/after,y:at.y+(next.y-at.y)*radius/after};
        route += ` L${point(enter)} Q${point(at)} ${point(leave)}`;
      }
      route += ` L${point(end)}`;
    }
    stage.querySelector('.note-shaft').setAttribute('d',route);
  }
  function fitTargets(index) {
    const stage = stages[index];
    const targets = [...leftCards.filter(el=>!el.hidden)];
    if(!stage.classList.contains('pre-design')) targets.push(stage);
    const note = stage.querySelector('.study');
    if(notes && note) targets.push(note);
    return targets;
  }

  function fit(elements) {
    const bounds = elements.map(boardBounds);
    const minX = Math.min(...bounds.map(b => b.x)), minY = Math.min(...bounds.map(b => b.y));
    const maxX = Math.max(...bounds.map(b => b.x + b.w)), maxY = Math.max(...bounds.map(b => b.y + b.h));
    const {w, h, top} = available();
    scale = clamp(Math.min((w - 48) / (maxX - minX), (h - 40) / (maxY - minY)), .12, 1.1);
    tx = (w - (maxX-minX)*scale)/2 - minX*scale;
    ty = top + (h - (maxY-minY)*scale)/2 - minY*scale;
    renderCamera();
  }
  function focusStep() {
    const section = stages[step].dataset.focus;
    const target = section ? leftCards.find(card => card.dataset.section === section) : stages[step];
    fit(notes && stages[step].querySelector('.study') ? [target, stages[step].querySelector('.study')] : [target]);
    if(section) return;
    const {w, top} = available();
    const readingScale = Math.min(.85, (w - 48) / 1000);
    if(scale < readingScale) {
      scale = readingScale;
      tx = 24 - stages[step].offsetLeft * scale;
      ty = top + 20 - stages[step].offsetTop * scale;
      renderCamera();
      $('status').textContent = 'Focused at readable size. Pan to read more; Fit all shows the overview.';
    }
  }
  function fragmentStep() {
    return /^#\d+$/.test(location.hash) ? clamp(Number(location.hash.slice(1))-1,0,stages.length-1) : 0;
  }
  function setStep(value) {
    step = clamp(value, 0, stages.length - 1);
    stages.forEach((el, i) => { el.hidden = i !== step; el.inert = i !== step; });
    leftCards.forEach(el => {el.hidden = Number(el.dataset.from) > step; el.inert = el.hidden;});
    revealItems.forEach(el => {
      const unrevealed = Number(el.dataset.reveal) > step;
      el.classList.toggle('unrevealed', unrevealed);
      el.inert = unrevealed;
      el.setAttribute('aria-hidden', String(unrevealed));
    });
    board.querySelectorAll('[data-model-from]').forEach(el => {
      const active = Number(el.dataset.modelFrom) <= step && step < Number(el.dataset.modelUntil);
      el.classList.toggle('unrevealed', !active);
      el.inert = !active;
      el.setAttribute('aria-hidden', String(!active));
    });
    placeNote(step);
    $('previous').disabled = step === 0;
    $('next').disabled = step === stages.length - 1;
    $('step-select').value = String(step);
    $('counter').textContent = `${String(step+1).padStart(2,'0')} / ${stages.length}`;
    const fragment = `#${step+1}`;
    if(location.hash !== fragment) history.replaceState(null,'',fragment);
  }
  function zoom(factor, x, y) {
    const next = clamp(scale * factor, .12, 2.5);
    const ratio = next / scale;
    tx = x - (x-tx)*ratio; ty = y - (y-ty)*ratio; scale = next;
    renderCamera();
  }
  function zoomCenter(factor) { const {w,h,top} = available(); zoom(factor,w/2,top+h/2); }
  function toggleQuestion(open) {
    panelOpen = open;
    question.classList.toggle('open', open);
    question.inert = !open;
    question.setAttribute('aria-hidden', String(!open));
    $('question-toggle').setAttribute('aria-expanded', String(open));
    document.body.classList.toggle('footer-question-open', open);
    if(open) requestAnimationFrame(() => { if(panelOpen) $('question-label').focus({preventScroll:true}); });
    else $('question-toggle').focus({preventScroll:true});
  }
  $('next').onclick = () => setStep(step + 1);
  $('previous').onclick = () => setStep(step - 1);
  $('step-select').onchange = event => setStep(Number(event.target.value));
  $('focus-step').onclick = focusStep;
  $('fit-all').onclick = () => fit(fitTargets(step));
  $('zoom-in').onclick = () => zoomCenter(1.2);
  $('zoom-out').onclick = () => zoomCenter(1/1.2);
  $('notes-toggle').onclick = () => {
    notes = !notes; board.classList.toggle('notes-off', !notes);
    board.querySelectorAll('.study').forEach(el => {el.inert = !notes;});
    $('notes-toggle').setAttribute('aria-pressed', String(notes));
  };
  $('question-toggle').onclick = () => toggleQuestion(!panelOpen);
  $('question-close').onclick = () => toggleQuestion(false);
  question.addEventListener('keydown', event => {
    if(event.key === 'Escape') {event.preventDefault(); toggleQuestion(false);}
    event.stopPropagation();
  });
  question.addEventListener('wheel', event => event.stopPropagation());
  board.querySelectorAll('.study-content').forEach(content => {
    let scrolling = null;
    const finish = () => {
      const id = scrolling?.id;
      scrolling = null;
      content.classList.remove('scroll-dragging');
      if(id !== undefined && content.hasPointerCapture(id)) content.releasePointerCapture(id);
    };
    content.addEventListener('pointerdown', event => {
      if(event.button !== 0 || event.target.closest('a,button,input,textarea,select,summary')) return;
      const rect = content.getBoundingClientRect();
      if((event.clientX-rect.left)/scale >= content.clientWidth) return;
      event.preventDefault();
      content.focus({preventScroll:true});
      scrolling = {id:event.pointerId,y:event.clientY};
      content.setPointerCapture(event.pointerId);
      content.classList.add('scroll-dragging');
    });
    content.addEventListener('pointermove', event => {
      if(!scrolling || scrolling.id !== event.pointerId) return;
      content.scrollTop -= (event.clientY-scrolling.y)/scale;
      scrolling.y = event.clientY;
    });
    content.addEventListener('pointerup',finish);
    content.addEventListener('pointercancel',finish);
    content.addEventListener('lostpointercapture',finish);
    window.addEventListener('blur',finish);
  });
  $('fullscreen').onclick = async () => {
    try { if(document.fullscreenElement) await document.exitFullscreen(); else await document.documentElement.requestFullscreen(); }
    catch { $('status').textContent = 'Full screen is unavailable. The board still fills this browser window.'; }
  };
  document.addEventListener('fullscreenchange', () => {
    $('fullscreen').textContent = document.fullscreenElement ? 'Exit full screen' : 'Full screen';
    $('fullscreen').setAttribute('aria-label', $('fullscreen').textContent);
  });
  document.addEventListener('wheel', event => {
    if(event.ctrlKey || event.metaKey) event.preventDefault();
  }, {capture:true, passive:false});
  viewport.addEventListener('wheel', event => {
    if(isolated(event.target)) return;
    event.preventDefault();
    const unit = event.deltaMode === 1 ? 16 : event.deltaMode === 2 ? viewport.clientHeight : 1;
    const delta = (event.deltaY || event.deltaX) * unit;
    const box = viewport.getBoundingClientRect();
    zoom(Math.exp(-delta * .002),event.clientX-box.left,event.clientY-box.top);
  }, {passive:false});
  viewport.addEventListener('mousedown', event => {
    if(event.button === 1 && !isolated(event.target)) event.preventDefault();
  });
  viewport.addEventListener('pointerdown', event => {
    if((event.button !== 0 && event.button !== 1) || isolated(event.target)) return;
    event.preventDefault(); drag = {id:event.pointerId,x:event.clientX,y:event.clientY};
    viewport.setPointerCapture(event.pointerId); viewport.classList.add('dragging');
  });
  viewport.addEventListener('pointermove', event => {
    if(!drag || event.pointerId !== drag.id) return;
    tx += event.clientX - drag.x; ty += event.clientY - drag.y;
    drag.x = event.clientX; drag.y = event.clientY; renderCamera();
  });
  function endDrag() {drag=null;viewport.classList.remove('dragging');}
  viewport.addEventListener('pointerup',endDrag);
  viewport.addEventListener('pointercancel',endDrag);
  viewport.addEventListener('lostpointercapture',endDrag);
  document.addEventListener('keydown', event => {
    if(event.target.closest('.question,.study-content,select,input,textarea,summary,[contenteditable]') || event.ctrlKey || event.metaKey || event.altKey) return;
    if(event.shiftKey && event.key.startsWith('Arrow')) {
      const shifts = {ArrowLeft:[100,0],ArrowRight:[-100,0],ArrowUp:[0,100],ArrowDown:[0,-100]};
      const shift = shifts[event.key];
      if(shift) {event.preventDefault(); tx+=shift[0]; ty+=shift[1]; renderCamera(); return;}
    }
    if(event.key === 'ArrowRight') {event.preventDefault();setStep(step+1);}
    if(event.key === 'ArrowLeft') {event.preventDefault();setStep(step-1);}
    if(event.code === 'Space' && !event.target.closest('button,a')) {event.preventDefault();}
  });
  window.addEventListener('blur', () => {endDrag();});
  window.addEventListener('resize', renderCamera);
  await document.fonts.ready;
  document.documentElement.classList.add('js');
  const columnTops = {requirements:40, model:40};
  leftCards.forEach(card => {
    const column = ['entities','interfaces'].includes(card.dataset.section) ? 'model' : 'requirements';
    card.style.top = `${columnTops[column]}px`;
    columnTops[column] += card.offsetHeight + 18;
  });
  question.inert = true; question.setAttribute('aria-hidden','true');
  stages.forEach((_, index) => placeNote(index));
  fit([...stages, ...leftCards, ...board.querySelectorAll('.study')]);
  setStep(fragmentStep());
  window.addEventListener('hashchange', () => setStep(fragmentStep()));
  requestAnimationFrame(() => requestAnimationFrame(() => document.documentElement.classList.add('ready')));
})();
