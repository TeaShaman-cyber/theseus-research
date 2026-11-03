# ChatGPT Project Contract governance

Coordination: [issue #107](https://github.com/TeaShaman-cyber/theseus-research/issues/107).

This directory is the candidate neutral Git home for the ChatGPT Project
Contract. The current accepted runtime contract is still v10 in
`TeaShaman-cyber/marcopolo-cookbook/project/project-contract.wl`; the files here
do **not** become project-wide authority merely by existing or merging.

Stage A imported the accepted v10 semantics without changing routing or authority. Stage B defines v11 routing while keeping runtime installation/probe separate:

- `legacy/project-contract-v10.wl` is the exact accepted v10 migration fixture;
- `chatgpt-project-contract.yaml` is a compact structured, LLM-reviewable canonical-source candidate;
- `project-settings.txt` is the deterministic compact projection generated from it;
- `tools/project_contract.py` proves semantic equality with the accepted v10
  fixture, rejects duplicate or malformed source structure, round-trips the
  generated projection, and enforces the current 8000-character Project Settings
  ceiling.

The `.wl` extension is historical, not an invariant. Early Project Contract work
used Wolfram as a formal verifier over a symbolic routing model. Future v11 work
should preserve that **formal verification role** for routing, gate and fallback
graph properties while also requiring adversarial LLM/Codex semantic review.
Formal model validity is not runtime acceptance.

Promotion to v11, canonical-source handoff, Session Search/Sprites routing changes,
and actual ChatGPT Project Settings installation are separate protected steps.


## v11 formal and semantic gates

- `formal/project-contract-v11-model.json` is an explicit control-flow model, separate from the runtime projection.
- `tools/project_contract_formal.py` performs deterministic graph/invariant checks in ordinary repo QA.
- `formal/verify.wl` independently evaluates the same invariant family in Wolfram Language.
- Wolfram proves properties of the formal model, not semantic completeness or runtime behavior.
- Adversarial LLM/Codex review remains a separate required gate.
- Git merge does not install Project Settings; runtime acceptance still requires `PC_OK_V11`.
