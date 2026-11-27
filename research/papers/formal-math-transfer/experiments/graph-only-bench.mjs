import {performance} from 'node:perf_hooks';
import assert from 'node:assert/strict';
function sequential(n,edges) {
 const adj=Array.from({length:n},()=>new Set());let visits=0;
 for(const [u,v] of edges){
  const pending=[v],seen=new Set();
  while(pending.length){const x=pending.pop();if(seen.has(x))continue;visits++;if(x===u)return {valid:false,visits};seen.add(x);for(const y of adj[x])pending.push(y);}
  adj[u].add(v);
 }
 return {valid:true,visits};
}
function batch(n,edges){
 const adj=Array.from({length:n},()=>new Set()),indegree=Array(n).fill(0);
 for(const [u,v] of edges){if(!adj[u].has(v)){adj[u].add(v);indegree[v]++;}}
 const queue=[];for(let i=0;i<n;i++)if(!indegree[i])queue.push(i);
 let visits=0,edgesVisited=0;
 for(let k=0;k<queue.length;k++){const x=queue[k];visits++;for(const y of adj[x]){edgesVisited++;if(--indegree[y]===0)queue.push(y);}}
 return {valid:visits===n,visits,edgesVisited};
}
const n=4,pairs=[];for(let i=0;i<n;i++)for(let j=0;j<n;j++)if(i!==j)pairs.push([i,j]);
let cases=0;for(let mask=0;mask<1<<pairs.length;mask++){const edges=pairs.filter((_,i)=>mask>>i&1);for(const e of [edges,[...edges].reverse(),[...edges,...edges]]){assert.equal(batch(n,e).valid,sequential(n,e).valid);cases++;}}
assert.equal(batch(1,[[0,0]]).valid,false);
console.log('DAG_BATCH_PARITY_PASS',cases,'ordered histories, plus self-loop');
for(const n of [1000,5000,10000]){
 const edges=Array.from({length:n-1},(_,i)=>[n-i-2,n-i-1]);
 let t=performance.now();const a=sequential(n,edges),oldMs=performance.now()-t;
 t=performance.now();const b=batch(n,edges),newMs=performance.now()-t;
 assert.equal(a.valid,true);assert.equal(b.valid,true);assert.equal(a.visits,n*(n-1)/2);
 console.log(JSON.stringify({n,edges:edges.length,oldVisits:a.visits,newVisits:b.visits,newEdgesVisited:b.edgesVisited,oldMs:Math.round(oldMs),newMs:Math.round(newMs)}));
}
