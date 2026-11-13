const fs = require('node:fs');
const crypto = require('node:crypto');
const rough = require('../assets/vendor/rough.cjs');
const g = rough.generator();
const esc = (value) => String(value).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const seed = key => (crypto.createHash('sha256').update(key).digest().readUInt32BE() & 0x7fffffff) || 1;
function draw(kind, args, key, options = {}) {
  const shape = g[kind](...args, {seed:seed(key),roughness:1.25,bowing:1,stroke:'#49535b',strokeWidth:1.5,preserveVertices:true,...options});
  return g.toPaths(shape).map(p => `<path d="${p.d}" stroke="${p.stroke}" stroke-width="${p.strokeWidth}" fill="${p.fill || 'none'}"/>`).join('');
}
function wrap(text, width) {
  const lines = []; let line = '';
  const words=text.split(/\s+/).flatMap(word=>word.match(new RegExp(`.{1,${width}}`, 'gu')) || []);
  for (const word of words) {
    if (line && (line + ' ' + word).length > width) { lines.push(line); line = ''; }
    line += (line ? ' ' : '') + word;
  }
  if (line) lines.push(line);
  return lines;
}
function shapeOf(node) {
  return node.shape || (['store','cache','counter'].includes(node.role)?'ellipse':node.role==='decision'?'diamond':'rectangle');
}
function endpoint(node, toward) {
  const {width,height}=node;
  const cx=node.x+width/2, cy=node.y+height/2;
  const dx=toward.x+toward.width/2-cx, dy=toward.y+toward.height/2-cy;
  const length=Math.hypot(dx,dy), ux=dx/length, uy=dy/length;
  const layers=node.replicated?[0,8,16]:[0];
  function inside(distance) {
    return layers.some(offset=>{
      const nx=Math.abs(ux*distance+offset)/(width/2);
      const ny=Math.abs(uy*distance+offset)/(height/2);
      const shape=shapeOf(node);
      return shape==='ellipse'?nx*nx+ny*ny<=1:shape==='diamond'?nx+ny<=1:Math.max(nx,ny)<=1;
    });
  }
  let low=0, high=Math.hypot(width,height)+32;
  for(let i=0;i<40;i++) {const mid=(low+high)/2;if(inside(mid))low=mid;else high=mid;}
  return [cx+ux*(high+6),cy+uy*(high+6)];
}
function figure(diagram, id, extent) {
  const flow = diagram.type === 'flow';
  const bw = flow ? 208 : 240, bh = flow ? 100 : 150;
  const nodes = flow ? diagram.labels.map((label,i)=>({id:String(i),label,x:12+i*240,y:24,width:bw,height:bh})) : diagram.nodes.map(n=>{
    const width=n.role==='gateway'?110:bw, height=n.role==='gateway'?220:bh;
    return {...n,x:24+n.column*320+(bw-width)/2,y:64+n.row*280+(bh-height)/2,width,height};
  });
  const edges = flow ? nodes.slice(1).map((n,i)=>({from:String(i),to:n.id,label:'',kind:'sync'})) : diagram.edges;
  const width = flow ? 960 : extent?.width || Math.max(960,320*(1+Math.max(...nodes.map(n=>n.column))));
  const height = flow ? 160 : extent?.height || Math.max(...nodes.map(n=>n.y+n.height+138));
  const family = diagram.family || id, prefix = `figure-${id}`;
  const lookup = Object.fromEntries(nodes.map(n=>[n.id,n]));
  let paths = '', labels = '', boxes = '';
  const bounds=n=>{
    const stack=n.replicated?16:0;
    const lines=(n.annotation||[]).flatMap(t=>wrap('• '+t,27));
    const annotationX=n.x+(n.width-240)/2+4;
    const left=lines.length?Math.min(n.x-stack,annotationX):n.x-stack;
    const right=lines.length?Math.max(n.x+n.width,annotationX+Math.max(...lines.map(t=>t.length))*15*.65):n.x+n.width;
    return {x:left,y:n.y-stack,w:right-left,h:n.height+stack+(lines.length?24+lines.length*18:0)};
  };
  const occupied=nodes.map(bounds);
  const overlaps=(a,b)=>a.x<b.x+b.w+6 && a.x+a.w+6>b.x && a.y<b.y+b.h+6 && a.y+a.h+6>b.y;

  edges.forEach(e=>{
    const a=lookup[e.from], b=lookup[e.to];
    const points=[endpoint(a,b),endpoint(b,a)];
    const [[x1,y1],[x2,y2]]=points;
    let lx=(x1+x2)/2, ly=(y1+y2)/2-16;
    if(a.x+a.width/2===b.x+b.width/2) lx+=a.x>320?-96:96;
    else if(a.y+a.height/2===b.y+b.height/2) ly=Math.min(a.y,b.y)-16;
    const dash=e.kind==='async'?' stroke-dasharray="6 5"':'';
    paths+=`<g data-edge-from="${esc(e.from)}" data-edge-to="${esc(e.to)}" data-start="${x1},${y1}" data-end="${x2},${y2}"${dash}>${draw('linearPath',[points],`${family}/edge/${e.from}/${e.to}`,{disableMultiStroke:e.kind==='async',strokeWidth:e.kind==='async'?2:1.5})}</g>`;
    function head(tip,previous,key){
      const angle=Math.atan2(tip[1]-previous[1],tip[0]-previous[0]);
      const size=Math.min(12,Math.hypot(tip[0]-previous[0],tip[1]-previous[1])/2);
      const wings=[-0.5,0.5].map(d=>[tip[0]-size*Math.cos(angle+d),tip[1]-size*Math.sin(angle+d)]);
      return draw('linearPath',[[wings[0],tip,wings[1]]],key,{roughness:0.6});
    }
    const clean=points.filter((p,j)=>!j||p[0]!==points[j-1][0]||p[1]!==points[j-1][1]);
    paths+=`<g data-arrow="end">${head(clean.at(-1),clean.at(-2),`${family}/head/${e.from}/${e.to}`)}</g>`;
    if(e.direction==='both') paths+=`<g data-arrow="start">${head(clean[0],clean[1],`${family}/start/${e.from}/${e.to}`)}</g>`;
    if(e.label.trim()){
      const lines=wrap(e.label,18), size=Math.max(...lines.map(l=>l.length))*9+12;
      const labelHeight=lines.length*18+6;
      const anchors=[[lx,ly],[lx,(y1+y2)/2],[a.x+a.width/2,(y1+y2)/2],[b.x+b.width/2,(y1+y2)/2],[b.x+b.width/2,b.y-16],[a.x+a.width/2,a.y-16],[lx,Math.max(y1,y2)+labelHeight+16]];
      for(const node of [a,b]) {
        const box=bounds(node), center=node.x+node.width/2;
        anchors.push([center,box.y-12],[center,box.y+box.h+labelHeight+16]);
      }
      for(let offset=40;offset<=160;offset+=40) anchors.push([lx,ly-offset],[lx,ly+offset]);
      const candidates=anchors.map(([x,y])=>({x:x-size/2,y:y-(lines.length-1)*18-17,w:size,h:labelHeight,lx:x,ly:y}));
      const chosen=candidates.find(c=>c.x>=0&&c.y>=0&&c.x+c.w<=width&&c.y+c.h<=height&&!occupied.some(o=>overlaps(c,o)));
      if(!chosen) throw Error(`No clear edge-label position for ${id}: ${e.from} -> ${e.to}; shorten the label or split the diagram`);
      occupied.push(chosen);lx=chosen.lx;ly=chosen.ly;
      labels+=`<rect x="${chosen.x}" y="${chosen.y}" width="${size}" height="${labelHeight}" fill="white"/>`;
      lines.forEach((line,j)=>labels+=`<text x="${lx}" y="${ly-(lines.length-1-j)*18}" text-anchor="middle" font-size="16">${esc(line)}</text>`);
    }
  });
  nodes.forEach(n=>{
    const bw=n.width, bh=n.height;
    const key=`${family}/${n.id}`;
    const shape=shapeOf(n);
    function outlineAt(offset) {
      const x=n.x-offset, y=n.y-offset;
      const options={fill:'white',fillStyle:'solid'};
      const layerKey=offset?`${key}/layer/${offset}`:key;
      if(shape==='ellipse') return draw('ellipse',[x+bw/2,y+bh/2,bw,bh],layerKey,{...options,curveFitting:1});
      if(shape==='diamond') return draw('polygon',[[[x+bw/2,y],[x+bw,y+bh/2],[x+bw/2,y+bh],[x,y+bh/2]]],layerKey,options);
      const r=18;
      return draw('path',[`M${x+r} ${y} H${x+bw-r} Q${x+bw} ${y} ${x+bw} ${y+r} V${y+bh-r} Q${x+bw} ${y+bh} ${x+bw-r} ${y+bh} H${x+r} Q${x} ${y+bh} ${x} ${y+bh-r} V${y+r} Q${x} ${y} ${x+r} ${y} Z`],layerKey,options);
    }
    const outline=(n.replicated?[16,8,0]:[0]).map(offset=>`<g data-replica-layer="${offset}">${outlineAt(offset)}</g>`).join('');
    const lines=wrap(n.label,shape==='diamond'?14:Math.min(19,Math.floor(bw/14)));
    const bullets=(n.bullets||[]).flatMap(t=>wrap('• '+t,Math.min(24,Math.floor(bw/10))));
    const textHeight=lines.length*24+bullets.length*19;
    const contentWidth=shape==='rectangle'?bw-24:bw*(shape==='ellipse'?.75:.65);
    const contentHeight=shape==='rectangle'?bh-24:bh*(shape==='ellipse'?.7:.5);
    const measuredWidth=Math.max(...lines.map(t=>t.length*22*.65),...bullets.map(t=>t.length*16*.65));
    const textScale=Math.min(1,contentWidth/measuredWidth,contentHeight/textHeight);
    let y=n.y+(bh-textHeight*textScale)/2+19*textScale;
    boxes+=`<g data-node-id="${esc(n.id)}" data-shape="${shape}">${outline}`;
    lines.forEach(line=>{boxes+=`<text x="${n.x+bw/2}" y="${y}" text-anchor="middle" font-size="${22*textScale}">${esc(line)}</text>`;y+=24*textScale;});
    bullets.forEach(line=>{boxes+=`<text x="${n.x+bw/2}" y="${y}" text-anchor="middle" font-size="${16*textScale}">${esc(line)}</text>`;y+=19*textScale;});
    boxes+='</g>';
    if(n.annotation){
      let ay=n.y+bh+24;
      boxes+=`<g data-annotation-for="${esc(n.id)}">`;
      n.annotation.forEach(t=>wrap('• '+t,27).forEach(line=>{boxes+=`<text x="${n.x+(bw-240)/2+4}" y="${ay}" font-size="15">${esc(line)}</text>`;ay+=18;}));
      boxes+='</g>';
    }
  });
  return `<figure><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${width} ${height}" role="img" aria-labelledby="${prefix}-title ${prefix}-desc"><title id="${prefix}-title">Design for ${esc(id)}</title><desc id="${prefix}-desc">${esc(diagram.description)}</desc>${paths}${labels}${boxes}</svg></figure>`;
}
const input=JSON.parse(fs.readFileSync(0,'utf8'));
if(input.kind==='outline') process.stdout.write(draw('rectangle',[4,4,492,592],input.id,{fill:'#eff7fc',fillStyle:'solid',stroke:'#7197ad'}));
else process.stdout.write(figure(input.diagram,input.id,input.extent));
