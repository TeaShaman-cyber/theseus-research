from itertools import combinations
from collections import deque
def build(n, edges):
    adj=[[] for _ in range(n)];deg=[0]*n;parent=list(range(n))
    def root(x):
        while parent[x]!=x:
            parent[x]=parent[parent[x]];x=parent[x]
        return x
    for a,b in edges:
        adj[a].append(b);deg[b]+=1;parent[root(a)]=root(b)
    q=deque(i for i in range(n) if deg[i]==0);rank=[-1]*n;k=0
    while q:
        a=q.popleft();rank[a]=k;k+=1
        for b in adj[a]:
            deg[b]-=1
            if not deg[b]:q.append(b)
    return adj,rank,[root(i) for i in range(n)],k==n
def path(adj,a,b,rank=None):
    pending=[a];seen=set();visits=0
    while pending:
        x=pending.pop()
        if x in seen:continue
        seen.add(x);visits+=1
        if x==b:return True,visits
        pending.extend(y for y in adj[x] if rank is None or rank[y]<=rank[b])
    return False,visits
def filtered(adj,rank,component,a,b):
    if a==b:return True,0
    if rank[a]>=rank[b] or component[a]!=component[b]:return False,0
    return path(adj,a,b,rank)
n=4;pairs=[(i,j) for i in range(n) for j in range(n) if i!=j];dags=queries=filtered_zero=redundant=0
for mask in range(1<<len(pairs)):
    edges=[e for k,e in enumerate(pairs) if mask>>k&1]
    adj,rank,c,ok=build(n,edges)
    if not ok:continue
    dags+=1
    for a,b in pairs:
        want,_=path(adj,a,b);got,visits=filtered(adj,rank,c,a,b)
        assert got==want
        queries+=1;filtered_zero+=visits==0
        if (a,b) not in edges and want:
            after,_,_,_=build(n,edges+[(a,b)])
            assert all(path(adj,x,y)[0]==path(after,x,y)[0] for x,y in pairs)
            redundant+=1
print('EXHAUSTIVE_PASS',dict(dags=dags,queries=queries,zero_visit_filters=filtered_zero,redundant_insertions=redundant))
# Large synthetic graph: two disconnected directed chains. Query first to second.
n=10000;edges=[(i,i+1) for i in range(n-1) if i!=n//2-1]
adj,rank,c,_=build(n,edges)
for name,a,b in [('disjoint',0,n-1),('reverse',n//2-1,0),('reachable',0,n//2-1)]:
    old=path(adj,a,b);new=filtered(adj,rank,c,a,b);assert old[0]==new[0];print(name,dict(old=old,new=new))
# Same weak component; destination is unreachable but a large branch follows it in topological order.
# Fixed valid rank order (not necessarily the one Kahn chooses).
edges=[(0,1),(0,2)]+[(i,i+1) for i in range(2,n-1) if i!=3]+[(3,1)]
adj,_,c,ok=build(n,edges);assert ok
rank=[0,n-1]+list(range(1,n-1))
assert all(rank[a]<rank[b] for a,b in edges)
# compare on synthetic branching DAG using a valid deterministic ordering
edges=[(0,1),(0,2)]+[(i,i+1) for i in range(3,n-1)]+[(0,3)]
adj,_,c,ok=build(n,edges);rank=list(range(n));assert ok and all(rank[a]<rank[b] for a,b in edges)
old=path(adj,0,2);new=filtered(adj,rank,c,0,2);assert old[0]==new[0];print('rank_prune_branch',dict(old=old,new=new))
