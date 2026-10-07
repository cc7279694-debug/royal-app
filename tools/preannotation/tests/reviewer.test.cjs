const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

function model() {
  const file = path.join(__dirname, '..', 'reviewer.js');
  assert.ok(fs.existsSync(file), 'reviewer behavior is not implemented');
  const context = vm.createContext({});
  vm.runInContext(fs.readFileSync(file, 'utf8'), context);
  return context.PreannotationReview;
}
function fixture() {
  return { bundle_sha256: 'a'.repeat(64), frames: [{frame_id:'f1', width:100, height:200,
    proposals: [{proposal_id:'p1', bbox_xyxy:[10,20,30,40], status:'pending',
      raw_teacher:{class:'witch', confidence:.9, owner_prediction:'opponent'}}]}] };
}
const fields = {visual_class:'visual.unit.witch', canonical_mapping:'unit.witch',
  bbox_xyxy:[10,20,30,40], owner:'unknown', form:'unknown', origin:'spawned',
  appearance_id:'same-witch', visibility:'visible', uncertainty:'none', note:''};

test('five edits are retained separately, raw teachers stay immutable and defaults stay unreviewed', () => {
  const api = model(), bundle = fixture(), before = JSON.stringify(bundle);
  const state = api.create(bundle);
  assert.equal(state.frames[0].coverage.length, 0);
  assert.equal(state.frames[0].decisions.length, 0);
  for (const action of ['accept','reject','relabel','bbox-correct']) {
    api.edit(bundle, state, 'f1', 'p1', action, fields);
    assert.equal(state.frames[0].decisions[0].action, action);
    assert.equal(state.frames[0].decisions[0].decision, action === 'reject' ? 'rejected' : 'accepted');
  }
  api.edit(bundle, state, 'f1', null, 'missing-box', {...fields, manual_id:'manual-1'});
  assert.equal(state.frames[0].decisions.length, 2);
  assert.equal(state.frames[0].decisions[1].manual_id, 'manual-1');
  assert.equal(JSON.stringify(bundle), before);
});

test('explicit class coverage is independent of accepting boxes', () => {
  const api=model(), bundle=fixture(), state=api.create(bundle);
  api.edit(bundle,state,'f1','p1','accept',fields);
  assert.equal(state.frames[0].coverage.length,0);
  api.coverage(state,'f1','visual.unit.witch',true,true);
  assert.equal(state.frames[0].coverage[0].unresolved,true);
  assert.equal(state.frames[0].coverage[0].exhaustive,true);
  api.coverage(state,'f1','visual.unit.balloon',false,true);
  assert.equal(state.frames[0].coverage.length,2);
});

test('review export requires actual human attribution and rejects invalid bounds', () => {
  const api=model(), bundle=fixture(), state=api.create(bundle);
  assert.throws(() => api.finish(state,'',false));
  assert.throws(() => api.finish(state,'Named human',false));
  assert.throws(() => api.edit(bundle,state,'f1','p1','accept',{...fields,bbox_xyxy:[-1,0,10,10]}));
  assert.throws(() => api.edit(bundle,state,'f1','p1','accept',{...fields,visual_class:'witch'}));
  const out=api.finish(state,'Named human',true);
  assert.equal(out.provenance.kind,'human');
  assert.equal(out.provenance.synthetic,false);
  assert.equal(out.provenance.human_review_attested,true);
  assert.equal(state.provenance.human_review_attested,false);
});

test('synthetic reviewer always exports synthetic provenance even when clicked by QA', () => {
  const api=model(), bundle={...fixture(),synthetic:true}, state=api.create(bundle);
  const out=api.finish(state,'QA demonstration',true);
  assert.equal(out.provenance.kind,'synthetic');
  assert.equal(out.provenance.synthetic,true);
  assert.equal(out.provenance.human_review_attested,false);
});

test('frame audit metadata names the source file and exact PTS without exposing parent path', () => {
  const api=model(), bundle={...fixture(),source_recording:'E:\\private\\source.mp4'};
  const frame={...bundle.frames[0],raw_pts:1080000,time_base:'1/90000'};
  assert.equal(typeof api.frameMetadata,'function','frame audit metadata is not implemented');
  const value=api.frameMetadata(bundle,frame);
  assert.ok(value.includes('source.mp4'));
  assert.ok(value.includes('1080000'));
  assert.ok(value.includes('1/90000'));
  assert.ok(!value.includes('private'));
});
