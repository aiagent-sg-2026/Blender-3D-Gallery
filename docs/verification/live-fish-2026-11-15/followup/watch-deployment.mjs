import {execFileSync} from 'node:child_process';
import fs from 'node:fs';
const repo='yapweijun1996/Blender-3D-Gallery',fish='65e56ac20802cd8969fac3d9de9131e87319b96a';
let target=process.argv[2]??'43619711865',last='',cancelledPolls=0;
const gh=args=>JSON.parse(execFileSync('gh',args,{encoding:'utf8',timeout:30000}));
const write=data=>fs.writeFileSync(new URL('deployment-latest.json',import.meta.url),JSON.stringify(data,null,2)+'\n');
for(;;){
 try{
  const state=gh(['run','view',target,'--repo',repo,'--json','status,conclusion,headSha,jobs,url']);
  const observation={checkedAt:new Date().toISOString(),runId:target,...state};
  if(state.status==='completed'&&state.conclusion==='cancelled'){
   const runs=gh(['run','list','--repo',repo,'--workflow','deploy.yml','--limit','8','--json','databaseId,headSha,status,conclusion,url']);
   const next=runs.find(r=>String(r.databaseId)!==target&&['pending','queued','in_progress','waiting'].includes(r.status));
   if(next){
    const relation=gh(['api',`repos/${repo}/compare/${fish}...${next.headSha}`]);
    if(!['ahead','identical'].includes(relation.status))throw new Error('Replacement run does not contain the fish revision');
    observation.superseded=true;observation.replacementRun=next.databaseId;write(observation);
    fs.writeFileSync(new URL(`deployment-cancelled-${target}.json`,import.meta.url),JSON.stringify(observation,null,2)+'\n');
    console.log('FOLLOW_NEWER_MAIN',target,'=>',next.databaseId,next.headSha);target=String(next.databaseId);last='';cancelledPolls=0;continue;
   }
   cancelledPolls++;observation.awaitingReplacement=cancelledPolls<3;write(observation);
   if(cancelledPolls<3){await new Promise(r=>setTimeout(r,30000));continue;}
  }else write(observation);
  const key=JSON.stringify([target,state.status,state.conclusion,state.jobs.map(j=>[j.name,j.status,j.conclusion,j.steps?.filter(s=>s.status==='in_progress').map(s=>s.name)])]);
  if(key!==last){console.log(new Date().toISOString(),key);last=key;}
  if(state.status==='completed'){console.log('DEPLOYMENT_FINISHED',state.conclusion);process.exit(state.conclusion==='success'?0:2);}
 }catch(e){console.log('MONITOR_RETRY',new Date().toISOString(),e.status??e.code??e.message);}
 await new Promise(r=>setTimeout(r,30000));
}
