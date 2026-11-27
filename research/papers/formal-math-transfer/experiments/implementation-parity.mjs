import assert from 'node:assert/strict';
import {pathToFileURL} from 'node:url';
import {resolve} from 'node:path';
const [baseline,candidate]=process.argv.slice(2);
if(!baseline||!candidate)throw Error('Usage: node <script> BASELINE_CHECKOUT CANDIDATE_CHECKOUT');
const old=await import(pathToFileURL(resolve(baseline,'src/dreaming/proposal-ledger.ts')));
const now=await import(pathToFileURL(resolve(candidate,'src/dreaming/proposal-ledger.ts')));
const records=Array.from({length:4},(_,i)=>now.createProposalRecord({proposal:{type:'UNKNOWN',claim:'Synthetic '+i,source_refs:[{source_ref:'fixture:1',evidence_hash:'sha256:e1'}],why_unknown:'Missing synthetic evidence.',required_evidence:['Synthetic evidence.']},origin:{packetId:'synthetic',evidenceFingerprint:'sha256:e',requestFingerprint:'sha256:r',perspectiveId:'p'+i,route:{id:'a',provider:'a',model:'a',modelFamily:'a'}}}));
const edges=records.flatMap((a,i)=>records.filter((_,j)=>i!==j).map(b=>now.createSupersessionEvent({supersededRecordId:a.recordId,replacementRecordId:b.recordId,reason:'parity'})));
function result(f){try{return {ok:true,value:f()}}catch(e){return {ok:false,name:e.name,message:e.message}}}
let cases=0,appends=0,valid=0;
for(let mask=0;mask<1<<edges.length;mask++){
 const selected=edges.filter((_,i)=>mask&(1<<i));
 for(const seq of [selected,[...selected].reverse()]){
  const history=[...records,...seq];
  const expected=result(()=>old.materializeLedger(history));
  const actual=result(()=>now.materializeLedger(history));
  assert.deepEqual(actual,expected);cases++;
  if(expected.ok){
   valid++;
   for(const candidate of edges){
    const before=old.createLedgerReplay();for(const e of history)before.append(e);
    const after=now.createLedgerReplay(history);
    assert.deepEqual(result(()=>{before.append(candidate);return before.snapshot()}),result(()=>{after.append(candidate);return after.snapshot()}));appends++;
   }
  }
 }
}
console.log(JSON.stringify({status:'PASS',cases,valid,appends}));
