// Editor UI for /journal/write. Plain HTML + JS, no build step.
import { esc } from './md.js';

const MARK = '<svg viewBox="-23 -163 976 887" aria-hidden="true"><path fill="currentColor" d="M795.96-142.13C802.24-149.77 813.15-151.71 821.66-146.67 863.52-121.88 891.82-97.34 908.9-67.87 927.98-34.98 948.79 8.16 934.46 58.78 917.67 118.05 895.76 151.55 828.89 204.18 799.18 227.55 533.28 416.1 216.38 466.4 150.39 476.88 86.45 482.3 17.88 470.14 8.29 467.59 0.63 461.39-3.99 453.43-8.61 445.47-10.19 435.75-7.64 426.15-5.09 416.55 0.52 407.68 9.08 404.28 46.24 389.52 301.91 291.63 442.91 184.7 649.27 28.2 762.62-101.53 795.96-142.13Z"/><circle fill="#ff6600" cx="766" cy="536" r="168"/></svg>';

const BASE_CSS = String.raw`
:root{--bg:#f7f6f2;--fg:#111110;--fg-2:#6b6963;--line:rgba(17,17,16,.12);--card:#fff;--soft:#efede8;--orange:#ff6600;
--sans:"Instrument Sans",ui-sans-serif,system-ui,-apple-system,"Segoe UI",sans-serif;--mono:"Geist Mono",ui-monospace,"SF Mono",Menlo,monospace;--disp:"Archivo","Instrument Sans",system-ui,sans-serif;--ease:cubic-bezier(.23,1,.32,1)}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#121211;--fg:#eceae6;--fg-2:#9a968f;--line:#2a2927;--card:#1a1918;--soft:#201f1d;color-scheme:dark}}
:root[data-theme="dark"]{--bg:#121211;--fg:#eceae6;--fg-2:#9a968f;--line:#2a2927;--card:#1a1918;--soft:#201f1d;color-scheme:dark}
*{box-sizing:border-box}html,body{height:100%}
body{margin:0;background:var(--bg);color:var(--fg);font:400 15px/1.5 var(--sans);-webkit-font-smoothing:antialiased}
a{color:inherit}button{font:inherit;color:inherit}
:focus-visible{outline:2px solid var(--orange);outline-offset:2px;border-radius:4px}
.bb{display:inline-flex;align-items:center;gap:10px;height:42px;padding:0 16px 0 18px;border:1.5px solid var(--fg);border-radius:12px;background:var(--fg);color:var(--bg);font:600 14px/1 var(--sans);cursor:pointer;white-space:nowrap;transition:background .2s var(--ease),color .2s var(--ease),transform .18s var(--ease)}
.bb::after{content:"";width:7px;height:7px;border-radius:50%;background:var(--orange);flex:0 0 auto}
.bb:hover{background:transparent;color:var(--fg)}.bb:active{transform:scale(.98)}.bb:disabled{opacity:.45;cursor:default}
.bg{display:inline-flex;align-items:center;gap:8px;height:42px;padding:0 14px;border:1px solid var(--line);border-radius:12px;background:transparent;cursor:pointer;font-weight:500;font-size:14px;white-space:nowrap;text-decoration:none}
.bg:hover{border-color:var(--fg)}.bg:disabled{opacity:.45;cursor:default}
.mark{width:34px;height:auto;display:block;color:var(--fg)}
[hidden]{display:none!important}
`;

export function loginPage(msg = '') {
  return `<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><meta name="robots" content="noindex">
<title>Journal editor — Basata</title><link rel="icon" href="/favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="/fonts/fonts.css">
<style>${BASE_CSS}
.box{min-height:100%;display:grid;place-items:center;padding:24px 16px}
.card{width:100%;max-width:420px}
h1{font:700 clamp(30px,6vw,40px)/1.02 var(--disp);letter-spacing:-.04em;margin:28px 0 10px}
p{color:var(--fg-2);margin:0 0 28px;font-size:16px}
form{display:grid;gap:12px}
input{height:50px;border:1px solid var(--line);border-radius:12px;padding:0 16px;font:400 16px var(--sans);background:var(--card);color:var(--fg)}
.bb{height:50px;justify-content:center}
.ok{min-height:1.4em;font:400 13px/1.5 var(--mono);color:var(--fg-2);margin-top:6px}
</style></head><body><div class="box"><div class="card">
<div class="mark">${MARK}</div>
<h1>Journal editor</h1>
<p>${msg ? esc(msg) : 'Enter your email. We send you a link that signs you in.'}</p>
<form id="f"><input type="email" name="email" required placeholder="you@basata.studio" autocomplete="email" aria-label="Email"><button class="bb" type="submit">Send me a link</button></form>
<div class="ok" id="ok" aria-live="polite"></div>
</div></div>
<script>
var f=document.getElementById('f'),ok=document.getElementById('ok');
f.addEventListener('submit',function(e){e.preventDefault();var b=f.querySelector('button');b.disabled=true;
fetch('/journal/write/login',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email:f.email.value})})
.then(function(){ok.textContent='If this email can edit the Journal, a link is on its way. Check your inbox (and Updates or Junk).';})
.catch(function(){ok.textContent='Could not send. Try again.';b.disabled=false;});});
</script></body></html>`;
}

export function editorPage(me) {
  return String.raw`<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><meta name="robots" content="noindex">
<title>Journal editor — Basata</title><link rel="icon" href="/favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="/fonts/fonts.css">
<style>${BASE_CSS}
.app{display:grid;grid-template-columns:280px minmax(0,1fr);height:100%}
aside{border-right:1px solid var(--line);display:flex;flex-direction:column;min-height:0;background:var(--bg)}
.side-top{display:flex;align-items:center;justify-content:space-between;padding:18px 18px 14px}
.side-top b{font:700 18px/1 var(--disp);letter-spacing:-.03em;display:flex;align-items:center;gap:10px}
.new{margin:0 18px 14px}.new .bb{width:100%;justify-content:center}
.list{flex:1;overflow:auto;padding:0 10px 18px}
.grp{font:400 11px/1 var(--mono);letter-spacing:.1em;text-transform:uppercase;color:var(--fg-2);padding:16px 10px 8px}
.it{display:block;width:100%;text-align:left;border:0;background:none;padding:10px 10px;border-radius:10px;cursor:pointer}
.it:hover{background:var(--soft)}.it.on{background:var(--card);box-shadow:0 0 0 1px var(--line)}
.it span{display:block;font-weight:600;font-size:14px;line-height:1.3;overflow:hidden;text-overflow:ellipsis;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical}
.it small{display:flex;align-items:center;gap:6px;margin-top:4px;font:400 11px/1 var(--mono);color:var(--fg-2)}
.dot{width:7px;height:7px;border-radius:50%;background:var(--fg-2);opacity:.5}.dot.live{background:var(--orange);opacity:1}
.side-foot{border-top:1px solid var(--line);padding:12px 18px;font:400 12px/1.4 var(--mono);color:var(--fg-2);display:flex;justify-content:space-between;gap:8px;align-items:center}
.side-foot button{border:0;background:none;cursor:pointer;color:var(--fg-2);font:inherit;text-decoration:underline}
main{display:flex;flex-direction:column;min-width:0;min-height:0}
.bar{display:flex;align-items:center;gap:10px;flex-wrap:wrap;padding:12px clamp(16px,3vw,32px);border-bottom:1px solid var(--line);background:var(--bg);position:sticky;top:0;z-index:5}
.pill{display:inline-flex;align-items:center;gap:7px;height:28px;padding:0 11px;border-radius:99px;background:var(--soft);font:500 12px/1 var(--mono);letter-spacing:.04em}
.pill.live{background:#ff66001a;color:var(--orange)}
.saved{font:400 12px/1 var(--mono);color:var(--fg-2);margin-right:auto}
.tabs{display:inline-flex;border:1px solid var(--line);border-radius:12px;padding:3px;gap:2px}
.tabs button{border:0;background:none;height:34px;padding:0 14px;border-radius:9px;cursor:pointer;font-weight:500;font-size:14px}
.tabs button.on{background:var(--fg);color:var(--bg)}
.menu-btn{display:none}
.scroll{flex:1;overflow:auto}
.doc{max-width:760px;margin:0 auto;padding:clamp(28px,5vw,56px) clamp(16px,3vw,32px) 120px}
.t{width:100%;border:0;background:none;resize:none;overflow:hidden;color:var(--fg);padding:0;outline:none}
.t::placeholder{color:var(--fg-2);opacity:.6}
#title{font:700 clamp(32px,4.6vw,56px)/1.04 var(--disp);letter-spacing:-.04em}
#dek{margin-top:16px;font:500 clamp(18px,1.7vw,21px)/1.4 var(--sans);letter-spacing:-.01em}
.cover{margin-top:28px;border:1.5px dashed var(--line);border-radius:14px;min-height:120px;display:grid;place-items:center;cursor:pointer;position:relative;overflow:hidden;background:var(--card);transition:border-color .2s}
.cover:hover,.cover.drag{border-color:var(--orange)}
.cover img{display:block;width:100%;height:auto;max-height:420px;object-fit:cover}
.cover .ph{text-align:center;color:var(--fg-2);padding:24px;font-size:14px}.cover .ph b{display:block;color:var(--fg);font-size:15px;margin-bottom:4px}
.cover .x{position:absolute;top:10px;right:10px;height:32px;padding:0 12px;border-radius:9px;border:0;background:rgba(17,17,16,.75);color:#fff;font-size:13px;cursor:pointer}
.tools{position:sticky;top:0;z-index:3;display:flex;gap:4px;flex-wrap:wrap;margin:32px 0 0;padding:8px;border:1px solid var(--line);border-radius:12px;background:var(--card)}
.tools button{height:34px;min-width:36px;padding:0 10px;border:0;border-radius:8px;background:none;cursor:pointer;font-weight:600;font-size:14px;color:var(--fg)}
.tools button:hover{background:var(--soft)}.tools .sep{width:1px;background:var(--line);margin:4px 4px}
.tools .help{margin-left:auto;font-weight:500;color:var(--fg-2)}
#body{display:block;min-height:60vh;margin-top:14px;font:400 17px/1.75 var(--sans);tab-size:2}
#body.drag{outline:2px dashed var(--orange);outline-offset:8px;border-radius:6px}
details{margin-top:40px;border-top:1px solid var(--line);padding-top:18px}
summary{cursor:pointer;font:400 12px/1 var(--mono);letter-spacing:.08em;text-transform:uppercase;color:var(--fg-2)}
.f{display:grid;gap:6px;margin-top:18px}.f label{font:400 12px/1 var(--mono);color:var(--fg-2)}
.f input,.f textarea{width:100%;border:1px solid var(--line);border-radius:10px;padding:12px 14px;font:400 15px/1.5 var(--sans);background:var(--card);color:var(--fg)}
.f textarea{min-height:90px;font-family:var(--mono);font-size:13px}
.addr{display:flex;align-items:center;border:1px solid var(--line);border-radius:10px;background:var(--card);overflow:hidden}
.addr span{padding:0 0 0 14px;color:var(--fg-2);font:400 14px var(--mono);white-space:nowrap}.addr input{border:0;border-radius:0;padding-left:2px;font:400 14px var(--mono)}
.cheat{display:grid;grid-template-columns:auto 1fr;gap:8px 18px;margin-top:16px;font-size:14px}.cheat code{font:400 13px var(--mono);background:var(--soft);padding:2px 7px;border-radius:6px;white-space:nowrap}
#pv{display:none;flex:1;border:0;width:100%;background:var(--bg)}
.prev #pv{display:block}.prev .scroll{display:none}
.toast{position:fixed;left:50%;bottom:24px;translate:-50% 0;background:var(--fg);color:var(--bg);padding:12px 18px;border-radius:12px;font-size:14px;opacity:0;pointer-events:none;transition:opacity .25s;z-index:20}
.toast.on{opacity:1}
.empty{display:grid;place-items:center;height:100%;color:var(--fg-2);text-align:center;padding:24px}.empty b{display:block;color:var(--fg);font:700 26px/1.1 var(--disp);letter-spacing:-.03em;margin-bottom:8px}
.ask{position:fixed;inset:0;background:rgba(0,0,0,.35);display:none;place-items:center;z-index:30;padding:16px}.ask.on{display:grid}
.ask div{background:var(--bg);border-radius:16px;padding:24px;max-width:380px;width:100%}.ask p{margin:0 0 18px;font-size:16px}.ask .r{display:flex;gap:10px;justify-content:flex-end}
@media (max-width:900px){.app{grid-template-columns:1fr}aside{position:fixed;inset:0 auto 0 0;width:min(86vw,320px);z-index:25;translate:-100% 0;transition:translate .3s var(--ease);box-shadow:0 0 40px rgba(0,0,0,.2)}.app.menu aside{translate:0 0}.menu-btn{display:inline-flex}.saved{display:none}.bar{gap:8px;padding:10px 12px}.bar .bg,.bar .bb{height:38px;padding:0 12px}.tabs button{height:30px;padding:0 10px}#view{display:none!important}}
</style></head><body>
<div class="app" id="app">
<aside>
  <div class="side-top"><b><span class="mark">${MARK}</span>Journal</b><a class="bg" href="/journal/" target="_blank" rel="noopener" style="height:34px">View ↗</a></div>
  <div class="new"><button class="bb" id="new">New article</button></div>
  <div class="list" id="list"></div>
  <div class="side-foot"><span>${esc(me)}</span><button id="out">Sign out</button></div>
</aside>
<main id="main">
  <div class="bar">
    <button class="bg menu-btn" id="menu">Articles</button>
    <span class="pill" id="pill">Draft</span>
    <span class="saved" id="saved"></span>
    <div class="tabs"><button class="on" id="tw">Write</button><button id="tp">Preview</button></div>
    <button class="bg" id="save">Save</button>
    <a class="bg" id="view" target="_blank" rel="noopener" hidden>Open live ↗</a>
    <button class="bg" id="unpub" hidden>Unpublish</button>
    <button class="bb" id="pub">Publish</button>
  </div>
  <div class="scroll" id="scroll">
    <div class="doc">
      <textarea class="t" id="title" rows="1" placeholder="Title"></textarea>
      <textarea class="t" id="dek" rows="1" placeholder="One line under the title"></textarea>
      <div class="cover" id="cover" tabindex="0" role="button" aria-label="Cover image"><div class="ph"><b>Add a cover image</b>Click or drop an image. It shows on the Journal page and when the link is shared.</div></div>
      <input type="file" id="coverfile" accept="image/*" hidden>
      <div class="tools" role="toolbar" aria-label="Formatting">
        <button data-a="h2" title="Heading">H</button><button data-a="h3" title="Small heading" style="font-size:12px">H</button>
        <span class="sep"></span>
        <button data-a="b" title="Bold (Ctrl/⌘ B)"><b>B</b></button><button data-a="i" title="Italic (Ctrl/⌘ I)"><i>I</i></button><button data-a="link" title="Link">Link</button>
        <span class="sep"></span>
        <button data-a="quote" title="Pull quote">“ ”</button><button data-a="list" title="List">• List</button><button data-a="hr" title="Divider">—</button>
        <span class="sep"></span>
        <button data-a="img" title="Image">Image</button>
        <button class="help" data-a="help">How to write</button>
      </div>
      <input type="file" id="imgfile" accept="image/*" multiple hidden>
      <textarea class="t" id="body" placeholder="Start writing. Leave an empty line between paragraphs. Drop images anywhere."></textarea>
      <details id="more">
        <summary>Details</summary>
        <div class="f"><label for="slug">Address</label><div class="addr"><span>basata.studio/journal/</span><input id="slug" placeholder="made-from-the-title"></div></div>
        <div class="f"><label for="desc">Google description (optional, defaults to the line under the title)</label><input id="desc" maxlength="300"></div>
        <div class="f"><label for="hero">Custom hero HTML (optional, replaces the cover at the top of the article)</label><textarea id="hero"></textarea></div>
      </details>
      <details id="cheat">
        <summary>How to write</summary>
        <div class="cheat">
          <code>## Heading</code><span>Section heading</span>
          <code>### Small heading</code><span>Smaller heading</span>
          <code>**bold**</code><span><b>bold</b></span>
          <code>*italic*</code><span><i>italic</i></span>
          <code>&gt; A line</code><span>Big pull quote</span>
          <code>- item</code><span>List with orange dots</span>
          <code>[words](https://…)</code><span>Link</span>
          <code>---</code><span>Divider line</span>
          <code>![what it shows](image)</code><span>Image. Drop or paste one and this is written for you</span>
          <code>empty line</code><span>New paragraph</span>
        </div>
      </details>
    </div>
  </div>
  <iframe id="pv" title="Preview"></iframe>
</main>
</div>
<div class="toast" id="toast" role="status"></div>
<div class="ask" id="ask"><div><p id="askq"></p><div class="r"><button class="bg" id="askn">Cancel</button><button class="bb" id="asky">Yes</button></div></div></div>
<script>
(function(){
var $=function(i){return document.getElementById(i)};
var F={title:$('title'),dek:$('dek'),body:$('body'),slug:$('slug'),desc:$('desc'),hero:$('hero')};
var cur=null, cover='', dirty=false, timer=null, saving=false;
function api(p,o){return fetch('/journal/write/api/'+p,o).then(function(r){if(r.status===401){location.reload();throw 0}return r})}
function post(p,b){return api(p,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(b)}).then(function(r){return r.json()})}
function toast(t){var e=$('toast');e.textContent=t;e.classList.add('on');clearTimeout(e._t);e._t=setTimeout(function(){e.classList.remove('on')},2200)}
function ask(q){return new Promise(function(res){$('askq').textContent=q;$('ask').classList.add('on');$('asky').onclick=function(){$('ask').classList.remove('on');res(true)};$('askn').onclick=function(){$('ask').classList.remove('on');res(false)}})}
function grow(t){t.style.height='auto';t.style.height=t.scrollHeight+'px'}
['title','dek','body'].forEach(function(k){F[k].addEventListener('input',function(){grow(F[k])})});
function ago(iso){if(!iso)return '';var s=(Date.now()-new Date(iso))/1000;if(s<50)return 'just now';if(s<3600)return Math.round(s/60)+' min ago';if(s<86400)return Math.round(s/3600)+' h ago';return new Date(iso).toLocaleDateString('en-GB',{day:'numeric',month:'short'})}
var MON=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
function d(iso){var x=new Date(iso);return x.getDate()+' '+MON[x.getMonth()]+' '+x.getFullYear()}

/* list */
var items=[];
function loadList(){return api('articles').then(function(r){return r.json()}).then(function(j){items=j.articles||[];drawList()})}
function drawList(){var L=$('list');L.innerHTML='';var drafts=items.filter(function(a){return a.status!=='published'}),live=items.filter(function(a){return a.status==='published'});
 function grp(name,arr){if(!arr.length)return;var h=document.createElement('div');h.className='grp';h.textContent=name;L.appendChild(h);arr.forEach(function(a){var b=document.createElement('button');b.className='it'+(cur&&cur.id===a.id?' on':'');var s=document.createElement('span');s.textContent=a.title||'Untitled';var m=document.createElement('small');m.innerHTML='<i class="dot'+(a.status==='published'?' live':'')+'"></i>';m.appendChild(document.createTextNode(a.status==='published'?d(a.published_at):'Edited '+ago(a.updated_at)));b.appendChild(s);b.appendChild(m);b.onclick=function(){open(a.id)};L.appendChild(b)})}
 grp('Drafts',drafts);grp('Published',live);
 if(!items.length){L.innerHTML='<div class="grp">No articles yet</div>'}}

/* state */
function setState(){var live=cur&&cur.status==='published';$('pill').textContent=live?'● Live':'Draft';$('pill').className='pill'+(live?' live':'');
 $('pub').textContent=live?'Update':'Publish';$('unpub').hidden=!live;$('view').hidden=!live;if(live)$('view').href='/journal/'+cur.slug+'/';
 F.slug.disabled=!!live;$('save').hidden=!!live;
 $('saved').textContent=dirty?(live?'Changes not live yet':'Unsaved'):(cur&&cur.updated_at?'Saved '+ago(cur.updated_at):'')}
function fill(a){cur=a;F.title.value=a.title||'';F.dek.value=a.dek||'';F.body.value=a.body||'';F.slug.value=a.slug||'';F.desc.value=a.description||'';F.hero.value=a.hero||'';setCover(a.cover||'');dirty=false;
 ['title','dek','body'].forEach(function(k){grow(F[k])});setState();drawList();showWrite()}
function open(id){if(dirty&&!confirmLeave())return;api('article?id='+id).then(function(r){return r.json()}).then(function(j){fill(j.article);history.replaceState(null,'','#'+id);$('app').classList.remove('menu')})}
function confirmLeave(){return !dirty||window.confirm('Leave without saving?')}
function blank(){fill({title:'',dek:'',body:'',slug:'',description:'',hero:'',cover:'',status:'draft'});cur=null;history.replaceState(null,'','#');setState();F.title.focus()}
function data(){return {id:cur&&cur.id,title:F.title.value,dek:F.dek.value,body:F.body.value,slug:F.slug.value,description:F.desc.value,hero:F.hero.value,cover:cover}}
function save(quiet){if(saving)return Promise.resolve();if(!F.title.value.trim()&&!F.body.value.trim())return Promise.resolve();saving=true;
 return post('save',data()).then(function(j){saving=false;if(!j.ok){toast('Could not save');return}var was=cur&&cur.status;cur=Object.assign(cur||{},{id:j.id,slug:j.slug,updated_at:j.updated_at,status:was||'draft'});F.slug.value=j.slug;dirty=false;setState();loadList();history.replaceState(null,'','#'+j.id);if(!quiet)toast(was==='published'?'Live article updated':'Saved')}).catch(function(){saving=false;toast('Could not save. Check your connection.')})}
function changed(){dirty=true;setState();clearTimeout(timer);if(!(cur&&cur.status==='published'))timer=setTimeout(function(){save(true)},2500)}
Object.keys(F).forEach(function(k){F[k].addEventListener('input',changed)});
$('save').onclick=function(){save()};
$('pub').onclick=function(){var live=cur&&cur.status==='published';if(!F.title.value.trim()){toast('Add a title first');F.title.focus();return}
 save(true).then(function(){if(live){toast('Live article updated');return}return ask('Publish this article on basata.studio/journal now?').then(function(y){if(!y)return;return post('status',{id:cur.id,status:'published'}).then(function(j){cur.status=j.status;cur.published_at=j.published_at;cur.slug=j.slug;setState();loadList();toast('Published')})})})};
$('unpub').onclick=function(){ask('Take this article off the website? It stays here as a draft.').then(function(y){if(!y)return;post('status',{id:cur.id,status:'draft'}).then(function(j){cur.status=j.status;setState();loadList();toast('Unpublished. Now a draft.')})})};
$('new').onclick=function(){if(confirmLeave())blank();$('app').classList.remove('menu')};
$('menu').onclick=function(){$('app').classList.toggle('menu')};
$('out').onclick=function(){fetch('/journal/write/logout',{method:'POST'}).then(function(){location.reload()})};
document.addEventListener('keydown',function(e){if((e.metaKey||e.ctrlKey)&&e.key==='s'){e.preventDefault();save()}
 if(document.activeElement===F.body&&(e.metaKey||e.ctrlKey)&&(e.key==='b'||e.key==='i')){e.preventDefault();act(e.key)}});
window.addEventListener('beforeunload',function(e){if(dirty){e.preventDefault();e.returnValue=''}});

/* preview */
function showWrite(){$('main').classList.remove('prev');$('tw').className='on';$('tp').className=''}
$('tw').onclick=showWrite;
$('tp').onclick=function(){$('main').classList.add('prev');$('tp').className='on';$('tw').className='';
 api('preview',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(data())}).then(function(r){return r.text()}).then(function(h){$('pv').srcdoc=h})};

/* editing helpers */
function wrap(a,b,ph){var t=F.body,s=t.selectionStart,e=t.selectionEnd,sel=t.value.slice(s,e)||ph;t.setRangeText(a+sel+b,s,e,'end');if(sel===ph){t.selectionStart=s+a.length;t.selectionEnd=s+a.length+ph.length}t.focus();grow(t);changed()}
function line(pre,ph){var t=F.body,s=t.selectionStart,e=t.selectionEnd,v=t.value,ls=v.lastIndexOf('\n',s-1)+1,le=v.indexOf('\n',e);if(le<0)le=v.length;
 var chunk=v.slice(ls,le)||ph;var out=chunk.split('\n').map(function(l){return pre+l.replace(/^(#{2,3} |> |- )/,'')}).join('\n');
 var before=v.slice(0,ls),after=v.slice(le);if(before&&!/\n\n$/.test(before))out=(/\n$/.test(before)?'\n':'\n\n')+out;if(after&&!/^\n\n/.test(after))out=out+(/^\n/.test(after)?'\n':'\n\n');
 t.setRangeText(out,ls,le,'end');t.focus();grow(t);changed()}
function insertBlock(txt){var t=F.body,s=t.selectionStart,v=t.value,pre=v.slice(0,s),post=v.slice(t.selectionEnd);
 var lead=!pre?'':/\n\n$/.test(pre)?'':/\n$/.test(pre)?'\n':'\n\n',tail=!post?'\n\n':/^\n\n/.test(post)?'':/^\n/.test(post)?'\n':'\n\n';
 t.setRangeText(lead+txt+tail,s,t.selectionEnd,'end');grow(t);changed()}
function act(a){if(a==='b')wrap('**','**','bold words');else if(a==='i')wrap('*','*','italic words');
 else if(a==='h2')line('## ','Heading');else if(a==='h3')line('### ','Small heading');else if(a==='quote')line('> ','A line worth repeating');
 else if(a==='list')line('- ','Item');else if(a==='hr')insertBlock('---');else if(a==='img')$('imgfile').click();
 else if(a==='help'){$('cheat').open=true;$('cheat').scrollIntoView({behavior:'smooth'})}
 else if(a==='link'){wrap('[','](https://)','link words')}}
document.querySelector('.tools').addEventListener('click',function(e){var b=e.target.closest('button');if(b)act(b.dataset.a)});

/* images */
function prep(file){return new Promise(function(res){if(/gif|svg/.test(file.type)){res({blob:file,type:file.type,cut:false});return}
 var img=new Image();img.onload=function(){var max=2000,w=img.naturalWidth,h=img.naturalHeight,k=Math.min(1,max/w);var c=document.createElement('canvas');c.width=Math.round(w*k);c.height=Math.round(h*k);var x=c.getContext('2d');x.drawImage(img,0,0,c.width,c.height);
  var cut=false;try{var px=x.getImageData(0,0,c.width,c.height).data;for(var i=3;i<px.length;i+=4*97){if(px[i]<250){cut=true;break}}}catch(err){}
  c.toBlob(function(b){res({blob:b||file,type:b?'image/webp':file.type,cut:cut})},'image/webp',.86)};img.onerror=function(){res({blob:file,type:file.type,cut:false})};img.src=URL.createObjectURL(file)})}
function upload(file){return prep(file).then(function(p){return api('upload',{method:'POST',headers:{'Content-Type':p.type},body:p.blob}).then(function(r){return r.json()}).then(function(j){if(!j.ok)throw 0;return {url:j.url,cut:p.cut}})})}
function addImages(files){[].slice.call(files).filter(function(f){return /^image\//.test(f.type)}).forEach(function(f){var alt=f.name.replace(/\.[^.]+$/,'').replace(/[-_]+/g,' ');var mark='![Uploading '+alt+'…]()';insertBlock(mark);toast('Uploading image…');
 upload(f).then(function(r){F.body.value=F.body.value.replace(mark,'!['+alt+']('+r.url+(r.cut?' "cutout"':'')+')');grow(F.body);changed();toast('Image added. Edit the words in [ ] to describe it.')}).catch(function(){F.body.value=F.body.value.replace(mark,'');toast('Upload failed')})})}
$('imgfile').onchange=function(){addImages(this.files);this.value=''};
F.body.addEventListener('dragover',function(e){e.preventDefault();F.body.classList.add('drag')});
F.body.addEventListener('dragleave',function(){F.body.classList.remove('drag')});
F.body.addEventListener('drop',function(e){F.body.classList.remove('drag');if(e.dataTransfer.files.length){e.preventDefault();addImages(e.dataTransfer.files)}});
F.body.addEventListener('paste',function(e){var fs=e.clipboardData&&e.clipboardData.files;if(fs&&fs.length){e.preventDefault();addImages(fs)}});

/* cover */
function setCover(u){cover=u;var c=$('cover');if(u){c.innerHTML='<img alt="" src="'+u.replace(/"/g,'')+'"><button class="x" type="button">Remove</button>';c.querySelector('.x').onclick=function(ev){ev.stopPropagation();setCover('');changed()}}
 else c.innerHTML='<div class="ph"><b>Add a cover image</b>Click or drop an image. It shows on the Journal page and when the link is shared.</div>'}
function coverFile(f){toast('Uploading cover…');upload(f).then(function(r){setCover(r.url);changed();toast('Cover added')}).catch(function(){toast('Upload failed')})}
$('cover').onclick=function(){$('coverfile').click()};$('cover').onkeydown=function(e){if(e.key==='Enter')$('coverfile').click()};
$('coverfile').onchange=function(){if(this.files[0])coverFile(this.files[0]);this.value=''};
$('cover').addEventListener('dragover',function(e){e.preventDefault();this.classList.add('drag')});
$('cover').addEventListener('dragleave',function(){this.classList.remove('drag')});
$('cover').addEventListener('drop',function(e){e.preventDefault();this.classList.remove('drag');if(e.dataTransfer.files[0])coverFile(e.dataTransfer.files[0])});

setInterval(setState,30000);
loadList().then(function(){var id=+location.hash.slice(1);if(id)open(id);else if(items.length)open(items[0].id);else blank()});
})();
</script></body></html>`;
}
