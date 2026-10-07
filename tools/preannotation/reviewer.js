/* Pure review operations. Teacher predictions are never mutated. */
(() => {
  const clone = value => JSON.parse(JSON.stringify(value));
  const check = (condition, message) => { if (!condition) throw new Error(message); };
  const classPattern = /^visual\.(unit|structure|effect|ui|other)\.[a-z0-9]+(?:[._-][a-z0-9]+)*$/;
  const getFrame = (state, id) => {
    const result = state.frames.find(frame => frame.frame_id === id);
    check(result, 'Unknown frame identity'); return result;
  };
  globalThis.PreannotationReview = {
    frameMetadata(bundle, frame) {
      const filename=(bundle.source_recording||'source unknown').split(/[\\/]/).pop();
      return `${filename} · ${frame.frame_id} · PTS ${frame.raw_pts} × ${frame.time_base} · 原图 ${frame.width}×${frame.height} · 整帧默认未审`;
    },
    create(bundle) {
      return {schema:'preannotation_human_return_v1', bundle_sha256:bundle.bundle_sha256,
        provenance:{kind:bundle.synthetic?'synthetic':'human', reviewer:'', human_review_attested:false, synthetic:!!bundle.synthetic},
        frames:bundle.frames.map(frame => ({frame_id:frame.frame_id, coverage:[], decisions:[]}))};
    },
    edit(bundle, state, frameId, proposalId, action, fields) {
      const frame = bundle.frames.find(item => item.frame_id === frameId);
      check(frame, 'Unknown source frame');
      check(['accept','reject','relabel','bbox-correct','missing-box'].includes(action), 'Unknown action');
      check((action==='reject' && !fields.visual_class) || classPattern.test(fields.visual_class), 'Use a visual.unit/structure/effect/ui/other class');
      const b=fields.bbox_xyxy;
      check(Array.isArray(b) && b.length===4 && b.every(Number.isFinite) &&
        0<=b[0] && b[0]<b[2] && b[2]<=frame.width && 0<=b[1] && b[1]<b[3] && b[3]<=frame.height,
        'Box must stay inside the original source image');
      check((action==='reject' && !fields.appearance_id) || /^[A-Za-z0-9][A-Za-z0-9._:-]{0,99}$/.test(fields.appearance_id), 'Enter an appearance identity');
      if (action==='missing-box') check(proposalId===null && fields.manual_id, 'Missing box needs a manual ID');
      else check(frame.proposals.some(p=>p.proposal_id===proposalId), 'Unknown teacher proposal');
      const decision={...clone(fields), proposal_id:proposalId, action,
        decision:action==='reject'?'rejected':'accepted'};
      const target=getFrame(state,frameId);
      const index=target.decisions.findIndex(item => action==='missing-box'
        ? item.manual_id===fields.manual_id : item.proposal_id===proposalId);
      if (index<0) target.decisions.push(decision); else target.decisions[index]=decision;
      return decision;
    },
    coverage(state, frameId, visualClass, exhaustive, unresolved) {
      check(classPattern.test(visualClass), 'Use a prefixed visual class');
      const frame=getFrame(state,frameId), item={visual_class:visualClass, scope:'full_frame',
        exhaustive:!!exhaustive, unresolved:!!unresolved};
      const index=frame.coverage.findIndex(row=>row.visual_class===visualClass);
      if(index<0) frame.coverage.push(item); else frame.coverage[index]=item;
    },
    finish(state, reviewer, attested) {
      check(reviewer.trim() && attested===true, 'Enter the actual human reviewer and explicitly attest review');
      const result=clone(state);
      const synthetic=state.provenance.synthetic;
      result.provenance={kind:synthetic?'synthetic':'human',reviewer:reviewer.trim(),human_review_attested:!synthetic,synthetic,
        reviewed_at:new Date().toISOString()};
      return result;
    },
  };
})();
