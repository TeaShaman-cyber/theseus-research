#!/usr/bin/env python3
"""Read-only historical validator probes. Requires full local Git history.

Executes version-pinned project-owned historical validator source in memory;
no network access, credentials, repository mutation, or GitHub publication.
It does NOT prove that any private identity was actually disclosed.
"""
import copy,importlib.util,json,subprocess,sys,types
from pathlib import Path
repo=str(Path(__file__).resolve().parents[4])
head='40b572554b8711dc6fb06de6cdc7e02e99f6dfdb'
def load(sha,path):
 return subprocess.check_output(['git','-C',repo,'show',sha+':'+path],text=True)
def probe(sha,kind):
 module=types.ModuleType('historic_registry_'+sha[:8])
 exec(compile(load(sha,'tools/registry_contract.py'),sha+':tools/registry_contract.py','exec'),module.__dict__)
 doc=json.loads(load(sha,'registry/research-lines.json'))
 if kind=='status_typo':
  x=next(x for x in doc['lines'] if x['id']=='theseus-needle-lab');x['status']='activ'
 if kind=='empty_component':
  x=next(x for x in doc['lines'] if x['id']=='theseus-needle-lab');x['repository']='TeaShaman-cyber/'
 if kind=='private_identity':
  x=next(x for x in doc['lines'] if x['id']=='sonar');x['repository']='TeaShaman-cyber/private-sonar'
 if kind=='visibility_mismatch':
  x=next(x for x in doc['lines'] if x['id']=='theseus-needle-lab');x['status']='private-incubation'
 return module.validate_registry(doc)
cases={
 'status_typo':('c3282c1a6eeb79985fd60ad8060ccca104e911d5',3939739198),
 'empty_component':('afa3a4888d09cb9aaba50c166b9e8c1ef6da4f01',3939807477),
 'private_identity':('755c68f625582a450b69826fc51b7c7ed5c44eaa',3939993038),
 'visibility_mismatch':('755c68f625582a450b69826fc51b7c7ed5c44eaa',3939993043)
}
results=[]
for name,(old,cid) in cases.items():
 a=probe(old,name);b=probe(head,name)
 assert not a,(name,'before unexpectedly rejected',a)
 assert b,(name,'after failed to reject',b)
 results.append({'case':name,'review_comment_id':cid,'before_sha':old,'after_sha':head,
  'before_validation_errors':a,'after_validation_errors':b,
  'result':'RED_BEFORE_GREEN_AFTER_VALIDATION',
  'scope':'pure registry validator, synthetic in-memory invalid entry; not an end-to-end GitHub write'})
 # JSON stdout is intentionally machine-readable
print(json.dumps(results,indent=2))
