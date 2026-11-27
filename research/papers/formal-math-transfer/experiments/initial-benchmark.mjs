import {performance} from 'node:perf_hooks';
import assert from 'node:assert/strict';
import {pathToFileURL} from 'node:url';
import {resolve} from 'node:path';
const [baseline,candidate]=process.argv.slice(2);
if(!baseline||!candidate)throw Error('Usage: node <script> BASELINE_CHECKOUT CANDIDATE_CHECKOUT');
const old=await import(pathToFileURL(resolve(baseline,'src/dreaming/proposal-ledger.ts')));
const now=await import(pathToFileURL(resolve(candidate,'src/dreaming/proposal-ledger.ts')));
const record=i=>now.createProposalRecord({proposal:{type:'UNKNOWN',claim:'Synthetic '+i,source_refs:[{source_ref:'fixture:1',evidence_hash:'sha256:e1'}],why_unknown:'Missing synthetic evidence.',required_evidence:['Synthetic evidence.']},origin:{packetId:'synthetic',evidenceFingerprint:'sha256:e',requestFingerprint:'sha256:r',perspectiveId:'p'+i,route:{id:'a',provider:'a',model:'a',modelFamily:'a'}}});
for(const n of [160,1000,5000]){
 const records=Array.from({length:n},(_,i)=>record(i));
 const history=[...records,...Array.from({length:n-1},(_,i)=>now.createSupersessionEvent({supersededRecordId:records[n-i-2].recordId,replacementRecordId:records[n-i-1].recordId,reason:'chain'}))];
 for(const [label,impl] of [['old',old],['new',now]]){
  let reads=0;const get=Map.prototype.get;
  Map.prototype.get=function(k){if(typeof k==='string'&&k.startsWith('sha256:'))reads++;return get.call(this,k);};
  const start=performance.now();let result;
  try{result=impl.materializeLedger(history);}finally{Map.prototype.get=get;}
  const ms=Math.round(performance.now()-start);
  assert.deepEqual(result.events,history);
  console.log(JSON.stringify({n,events:history.length,version:label,ms,reads}));
 }
}
