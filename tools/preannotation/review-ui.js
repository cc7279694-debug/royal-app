/* Local, offline UI. User strings enter textContent/value, never innerHTML. */
(() => {
  const bundle=globalThis.PREANNOTATION_BUNDLE, api=globalThis.PreannotationReview;
  const state=api.create(bundle), $=id=>document.getElementById(id);
  let frameIndex=0, selected=null, manualId=null, image=null, dragStart=null, imageReady=false, imageVersion=0;
  const current=()=>bundle.frames[frameIndex];
  const review=()=>state.frames[frameIndex];
  const message=text=>{$('status').textContent=text;};
  function setImageReady(ready){
    imageReady=ready;
    $('edit-form').querySelectorAll('button,input,select').forEach(control=>{control.disabled=!ready;});
    $('save-coverage').disabled=!ready;
  }
  function requireImage(){
    if(imageReady&&image)return true;
    message('请等待当前帧原图成功加载后再审核。');return false;
  }
  bundle.frames.forEach((frame,index)=>{const option=document.createElement('option');option.value=index;
    option.textContent=`${index+1} · ${frame.source_relative_seconds.toFixed(2)}s`; $('frame-select').append(option);});
  $('summary').textContent=`${bundle.recording_id} · ${bundle.frames.length} 帧 · ${bundle.frames.reduce((n,f)=>n+f.proposals.length,0)} 待审建议`;
  if(bundle.synthetic){document.querySelector('h1').textContent='合成演示 · 不会产生真实人审 GT';
    document.querySelector('.notice').textContent='合成图与模拟预测，仅供操作验证。所有下载文件都会标记 synthetic，不会导入为真实 GT。';}
  function draw(){
    if(!image||!imageReady)return;
    const canvas=$('image'),ctx=canvas.getContext('2d'); canvas.width=current().width;canvas.height=current().height;
    ctx.drawImage(image,0,0);ctx.lineWidth=2;ctx.font='12px sans-serif';
    current().proposals.forEach((proposal,index)=>{
      const decision=review().decisions.find(d=>d.proposal_id===proposal.proposal_id),b=decision?.bbox_xyxy||proposal.bbox_xyxy;
      ctx.strokeStyle=proposal.proposal_id===selected?'#ffdf76':decision?.decision==='accepted'?'#82e3a1':decision?.decision==='rejected'?'#ef9292':'#94bbff';
      ctx.strokeRect(b[0],b[1],b[2]-b[0],b[3]-b[1]);ctx.fillStyle=ctx.strokeStyle;ctx.fillText(`${index+1}`,b[0]+3,Math.max(12,b[1]-3));
    });
    review().decisions.filter(d=>d.action==='missing-box').forEach(d=>{const b=d.bbox_xyxy;ctx.strokeStyle='#deaeff';ctx.strokeRect(b[0],b[1],b[2]-b[0],b[3]-b[1]);});
  }
  function renderList(){
    $('proposal-list').replaceChildren();
    current().proposals.forEach((proposal,index)=>{
      const decision=review().decisions.find(d=>d.proposal_id===proposal.proposal_id),button=document.createElement('button');
      button.className=`proposal ${decision?.decision||'pending'} ${selected===proposal.proposal_id?'selected':''}`;
      button.disabled=!imageReady;
      button.textContent=`${index+1}. ${proposal.raw_teacher.class} · ${proposal.raw_teacher.confidence.toFixed(3)} · ${decision?.decision||'pending'}`;
      button.onclick=()=>selectProposal(proposal);$('proposal-list').append(button);
    });
    $('coverage-list').replaceChildren();review().coverage.forEach(row=>{const div=document.createElement('div');div.className='coverage-row';
      div.textContent=`${row.visual_class} · ${row.exhaustive?'整帧已查':'未完整检查'} · ${row.unresolved?'仍有未知':'此类别无未知声明'}`;$('coverage-list').append(div);});
  }
  function setFields(fields){
    $('visual-class').value=fields.visual_class||''; $('canonical').value=fields.canonical_mapping||'';
    ['x1','y1','x2','y2'].forEach((id,index)=>{$(id).value=fields.bbox_xyxy?.[index]??'';});
    for(const name of ['owner','form','origin']) $(name).value=fields[name]||'unknown';
    $('visibility').value=fields.visibility||'visible';$('uncertainty').value=fields.uncertainty||'unknown';
    $('appearance').value=fields.appearance_id||'';$('note').value=fields.note||'';
  }
  function selectProposal(proposal){
    if(!requireImage())return;
    selected=proposal.proposal_id;manualId=null;$('save-missing').hidden=true;
    $('edit-title').textContent=`建议 ${current().proposals.indexOf(proposal)+1}`;
    $('raw-teacher').textContent=`原始模型：${proposal.raw_teacher.class}；归属假设 ${proposal.raw_teacher.owner_prediction||'unknown'}；置信度 ${proposal.raw_teacher.confidence.toFixed(3)}。人审字段不继承模型归属。`;
    setFields(review().decisions.find(d=>d.proposal_id===selected)||{bbox_xyxy:proposal.bbox_xyxy});renderList();draw();
  }
  function frameChange(index){
    const version=++imageVersion;
    image=null;dragStart=null;setImageReady(false);
    $('image').width=0;$('image').height=0;$('image').hidden=true;
    frameIndex=Math.max(0,Math.min(bundle.frames.length-1,index));selected=null;manualId=null;$('save-missing').hidden=true;
    $('frame-select').value=frameIndex;$('previous').disabled=frameIndex===0;$('next').disabled=frameIndex===bundle.frames.length-1;
    $('frame-meta').textContent=api.frameMetadata(bundle,current());
    $('edit-title').textContent='选择一个建议框';$('raw-teacher').textContent='';setFields({});renderList();
    $('image-status').textContent='原图加载中，暂不能提交标注。';
    const loaded=new Image();
    loaded.onload=()=>{
      if(version!==imageVersion)return;
      image=loaded;setImageReady(true);$('image').hidden=false;draw();renderList();
      $('image-status').textContent='原图已加载，可以审核。';
    };
    loaded.onerror=()=>{
      if(version!==imageVersion)return;
      image=null;dragStart=null;setImageReady(false);$('image').width=0;$('image').height=0;$('image').hidden=true;renderList();
      $('image-status').textContent='原图加载失败，暂不能审核。请切换帧重试。';
    };
    loaded.src=current().image;
  }
  $('frame-select').onchange=()=>frameChange(Number($('frame-select').value));
  $('previous').onclick=()=>frameChange(frameIndex-1);$('next').onclick=()=>frameChange(frameIndex+1);
  $('missing').onclick=()=>{if(!requireImage())return;selected=null;manualId=`missing-${Date.now()}-${review().decisions.length+1}`;
    $('save-missing').hidden=false;$('edit-title').textContent='补漏框 · 在图上拖动';$('raw-teacher').textContent='手动补框，不包含模型来源。';setFields({});renderList();draw();};
  const coordinates=event=>{const r=$('image').getBoundingClientRect();return [Math.max(0,Math.min(current().width,(event.clientX-r.left)*current().width/r.width)),
    Math.max(0,Math.min(current().height,(event.clientY-r.top)*current().height/r.height))];};
  $('image').onpointerdown=event=>{if(imageReady&&manualId){dragStart=coordinates(event);$('image').setPointerCapture(event.pointerId);}};
  $('image').onpointerup=event=>{if(!imageReady){dragStart=null;return;}if(dragStart){const end=coordinates(event),b=[Math.min(dragStart[0],end[0]),Math.min(dragStart[1],end[1]),Math.max(dragStart[0],end[0]),Math.max(dragStart[1],end[1])];
    ['x1','y1','x2','y2'].forEach((id,i)=>{$(id).value=Math.round(b[i]*100)/100;});dragStart=null;}};
  $('edit-form').onsubmit=event=>{
    event.preventDefault();if(!requireImage())return;try{
      const action=event.submitter.dataset.action,fields={visual_class:$('visual-class').value.trim()||null,canonical_mapping:$('canonical').value.trim()||null,
        bbox_xyxy:['x1','y1','x2','y2'].map(id=>Number($(id).value)),owner:$('owner').value,form:$('form').value,origin:$('origin').value,
        appearance_id:$('appearance').value.trim()||null,visibility:$('visibility').value,uncertainty:$('uncertainty').value,note:$('note').value};
      if(action==='missing-box')fields.manual_id=manualId;
      api.edit(bundle,state,current().frame_id,selected,action,fields);renderList();draw();message(`已暂存 ${action}。尚未审核的区域仍为未知。`);
    }catch(error){message(error.message);}
  };
  $('save-coverage').onclick=()=>{if(!requireImage())return;try{api.coverage(state,current().frame_id,$('coverage-class').value.trim(),$('exhaustive').checked,$('unresolved').checked);
    renderList();message('已单独记录此类别的整帧检查声明。拒绝、未知和未审框仍然保留。');}catch(error){message(error.message);}};
  $('download').onclick=()=>{try{const returned=api.finish(state,$('reviewer').value,$('attested').checked),blob=new Blob([JSON.stringify(returned,null,2)+'\n'],{type:'application/json'}),url=URL.createObjectURL(blob),link=document.createElement('a');
    link.href=url;link.download=`${bundle.recording_id}-human-return-${Date.now()}.json`;link.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
    message('已下载独立回传文件。请用 CLI 验证并导入到一个新的版本目录。');}catch(error){message(error.message);}};
  frameChange(0);
})();
