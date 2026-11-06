# ChatGPT Project Contract governance

Coordination: [issue #107](https://github.com/TeaShaman-cyber/theseus-research/issues/107).

This directory is the **canonical Git source** for the ChatGPT Project Contract.
The currently installed project-runtime projection is v11 (`PC_OK_V11`); an
accepted Git v12 update does **not** by itself install new Project Settings.

- `legacy/project-contract-v10.wl` is the pinned accepted historical migration fixture.
- `chatgpt-project-contract.yaml` is the current canonical source.
- `project-settings.txt` is its deterministic generated ChatGPT Settings projection.
- `tools/project_contract.py` validates unique fields, structure, source/projection
  round-trip and the 8,000-character ceiling. The v10 migration equivalence
  check applies to the historical v10 source, not arbitrarily to later revisions.

The v12 change prefers the directly verified exe.dev shell and
`exe-dev-core-router` from `theseus-cloud-shell`, with Fly Sprites and MarcoPolo
only as observed-need alternatives. Authority and user permission do not migrate
to the runtime. See [#114](https://github.com/TeaShaman-cyber/theseus-research/issues/114).
The project-installed state must still be independently probed with `PC_OK_V12`.

The Wolfram `.wl` model verifier remains an independent formal check, not proof
that the ChatGPT Project Settings projection is installed or active.

## Formal and semantic gates (v11 historical, v12 active)

- `formal/project-contract-v12-model.json` is the active explicit control-flow model, separate from the runtime projection; v11 remains as historical evidence.
- Fallback termination is modeled with the well-founded rank `remaining_untried_routes`: the only cycle edge strictly decreases a finite nonnegative measure and the zero case exits to a terminal state.
- `tools/project_contract_formal.py` performs deterministic graph/invariant checks in ordinary repo QA.
- `formal/verify.wl` independently evaluates the same invariant family in Wolfram Language.
- Wolfram proves properties of the formal model, not semantic completeness or runtime behavior.
- Adversarial LLM/Codex review remains a separate required gate.
- Git merge does not install Project Settings; v12 runtime acceptance requires `PC_OK_V12`.
