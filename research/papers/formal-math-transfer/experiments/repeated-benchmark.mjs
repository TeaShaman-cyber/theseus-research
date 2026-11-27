import assert from 'node:assert/strict';
import { performance } from 'node:perf_hooks';
import { pathToFileURL } from 'node:url';
import { resolve } from 'node:path';
const [baseline,candidate]=process.argv.slice(2);
if(!baseline||!candidate)throw Error('Usage: node repeated-benchmark.mjs BASELINE_CHECKOUT CANDIDATE_CHECKOUT');
const implementations=await Promise.all([baseline,candidate].map(p=>import(pathToFileURL(resolve(p,'src/dreaming/proposal-ledger.ts')))));
const [old,now]=implementations;
const record=i=>now.createProposalRecord({proposal:{type:'UNKNOWN',claim:'Synthetic '+i,source_refs:[{source_ref:'fixture:1',evidence_hash:'sha256:e1'}],why_unknown:'Missing synthetic evidence.',required_evidence:['Synthetic evidence.']},origin:{packetId:'synthetic',evidenceFingerprint:'sha256:e',requestFingerprint:'sha256:r',perspectiveId:'p'+i,route:{id:'a',provider:'a',model:'a',modelFamily:'a'}}});
const shapes={
 proposals:n=>[],
 reverse_chain:n=>Array.from({length:n-1},(_,i)=>[n-i-2,n-i-1]),
 forward_chain:n=>Array.from({length:n-1},(_,i)=>[i,i+1]),
 fanout:n=>Array.from({length:n-1},(_,i)=>[0,i+1]),
 disconnected:n=>Array.from({length:n-1},(_,i)=>[i,i+1]).filter(([i])=>(i+1)%32!==0).reverse(),
 diamonds:n=>Array.from({length:Math.floor((n-1)/3)},(_,i)=>{const k=i*3;return [[k,k+1],[k,k+2],[k+1,k+3],[k+2,k+3]];}).flat().reverse()
};
function makeHistory(n,shape){
 const records=Array.from({length:n},(_,i)=>record(i));
 return [...records,...shapes[shape](n).map(([i,j])=>now.createSupersessionEvent({supersededRecordId:records[i].recordId,replacementRecordId:records[j].recordId,reason:shape}))];
}
function measured(impl,history){
 const t=performance.now();
 const view=impl.materializeLedger(history);
 const ms=performance.now()-t;
 assert.deepEqual(view.events,history);
 return ms;
}
function count(impl,history){
 const get=Map.prototype.get;let reads=0;
 try{Map.prototype.get=function(key){if(typeof key==='string'&&key.startsWith('sha256:'))reads++;return get.call(this,key);};assert.deepEqual(impl.materializeLedger(history).events,history);}
 finally{Map.prototype.get=get;}
 return reads;
}
const repeats=7;
for(const n of [160,1000,2500]){
 for(const shape of Object.keys(shapes)){
  const history=makeHistory(n,shape);
  const oracle=old.materializeLedger(history);
  assert.deepEqual(now.materializeLedger(history),oracle);
  for(let i=0;i<2;i++)for(const impl of implementations)measured(impl,history);
  const samples=[[],[]];
  // Counterbalanced order; no instrumented map access in elapsed samples.
  for(let i=0;i<repeats;i++)for(const j of i%2?[1,0]:[0,1])samples[j].push(measured(implementations[j],history));
  for(let j=0;j<2;j++)console.log(JSON.stringify({n,shape,events:history.length,version:j?'candidate':'baseline',repeats,ms:samples[j],shaMapGets:count(implementations[j],history)}));
 }
}
