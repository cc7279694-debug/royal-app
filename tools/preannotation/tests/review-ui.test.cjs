/* Executes the real UI and model with controlled image-load events. No private media. */
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

function harness() {
  const images=[];
  class ImageSurface { constructor(){images.push(this);} }
  class Element {
    constructor(){this.value='';this.checked=false;this.disabled=false;this.hidden=false;this.children=[];this.width=300;this.height=150;this.textContent='';}
    append(child){this.children.push(child);}
    replaceChildren(){this.children=[];}
    querySelectorAll(){return controls;}
    getContext(){return {drawImage(){},strokeRect(){},fillText(){},clearRect(){}};}
    getBoundingClientRect(){return {left:0,top:0,width:100,height:200};}
    setPointerCapture(){}
  }
  const nodes=new Map(), element=id=>{if(!nodes.has(id))nodes.set(id,new Element());return nodes.get(id);};
  const controls=['visual-class','canonical','x1','y1','x2','y2','owner','form','origin','visibility','uncertainty','appearance','note','missing','save-missing'].map(element);
  const bundle={schema:'preannotation_bundle_v1',bundle_sha256:'a'.repeat(64),recording_id:'natural_match_01',source_recording:'synthetic.mp4',synthetic:true,
    frames:[0,1,2].map(i=>({frame_id:`f${i}`,raw_pts:i,time_base:'1/2',source_relative_seconds:i/2,width:100,height:200,image:`images/f${i}.png`,
      proposals:[{proposal_id:`p${i}`,bbox_xyxy:[10,20,30,40],status:'pending',raw_teacher:{class:'witch',confidence:.9,owner_prediction:'opponent'}}]}))};
  const context=vm.createContext({Image:ImageSurface,PREANNOTATION_BUNDLE:bundle,document:{getElementById:element,
    querySelector:element,createElement:()=>new Element()},setTimeout(){},Blob:class{},URL:{createObjectURL(){return 'blob:synthetic';},revokeObjectURL(){}}});
  const dir=path.join(__dirname,'..');
  vm.runInContext(fs.readFileSync(path.join(dir,'reviewer.js'),'utf8'),context);
  let state;
  const realCreate=context.PreannotationReview.create;
  context.PreannotationReview.create=(...args)=>{state=realCreate(...args);return state;};
  vm.runInContext(fs.readFileSync(path.join(dir,'review-ui.js'),'utf8'),context);
  return {images,element,state,controls};
}
function fields(h){
  for(const [id,value] of Object.entries({'visual-class':'visual.unit.witch',canonical:'unit.witch',appearance:'witch-a',
    owner:'unknown',form:'unknown',origin:'unknown',visibility:'visible',uncertainty:'none',x1:10,y1:20,x2:30,y2:40})) h.element(id).value=String(value);
}
function submit(h){h.element('edit-form').onsubmit({preventDefault(){},submitter:{dataset:{action:'accept'}}});}
function select(h){h.element('proposal-list').children[0].onclick();fields(h);}

test('transition clears previous pixels/drag and blocks edit/missing/coverage until active source image loads',()=>{
  const h=harness();
  h.images[0].onload();select(h);
  h.element('missing').onclick();
  h.element('image').onpointerdown({clientX:10,clientY:20,pointerId:1});
  h.element('next').onclick();
  assert.equal(h.element('image').width,0,'old frame canvas pixels must be cleared');
  assert.equal(h.element('image').height,0);
  assert.equal(h.element('missing').disabled,true);
  assert.equal(h.element('save-coverage').disabled,true);
  h.element('proposal-list').children[0].onclick();fields(h);
  submit(h);
  assert.equal(h.state.frames[1].decisions.length,0);
  h.element('missing').onclick();
  assert.equal(h.element('save-missing').hidden,true);
  h.element('coverage-class').value='visual.unit.witch';h.element('exhaustive').checked=true;h.element('unresolved').checked=false;
  h.element('save-coverage').onclick();
  assert.equal(h.state.frames[1].coverage.length,0);
  h.element('image').onpointerup({clientX:90,clientY:190,pointerId:1});
  assert.equal(h.element('x1').value,'10','previous drag cannot alter new source coordinates');
  h.images[1].onload();
  assert.equal(h.element('image').width,100);
  assert.equal(h.element('image').height,200);
  assert.equal(h.element('missing').disabled,false);
  select(h);submit(h);
  assert.equal(h.state.frames[1].decisions.length,1);
});

test('active image failure is visible and remains uneditable; later successful source restores controls',()=>{
  const h=harness();h.images[0].onload();h.element('next').onclick();
  assert.equal(typeof h.images[1].onerror,'function','active source failures need explicit handling');
  h.images[1].onerror();
  assert.match(h.element('image-status').textContent,/失败/);
  assert.equal(h.element('image').width,0);
  assert.equal(h.element('missing').disabled,true);
  h.element('proposal-list').children[0].onclick();fields(h);submit(h);
  assert.equal(h.state.frames[1].decisions.length,0);
  h.element('next').onclick();h.images[2].onload();
  assert.equal(h.element('missing').disabled,false);
  select(h);submit(h);
  assert.equal(h.state.frames[2].decisions.length,1);
});

test('reversed callbacks including a revisit to the same frame cannot reopen stale review state',()=>{
  const h=harness();
  h.element('next').onclick();h.element('previous').onclick();
  h.images[0].onload();
  assert.equal(h.element('image').width,0,'old same-frame request must be ignored after a new generation');
  assert.equal(h.element('missing').disabled,true);
  h.images[1].onload();
  assert.equal(h.element('image').width,0);
  h.images[2].onload();
  assert.equal(h.element('missing').disabled,false);
  assert.match(h.element('image-status').textContent,/已加载/);
  h.images[1].onerror();
  assert.equal(h.element('missing').disabled,false);
  assert.match(h.element('image-status').textContent,/已加载/);
  select(h);submit(h);assert.equal(h.state.frames[0].decisions.length,1);
});
