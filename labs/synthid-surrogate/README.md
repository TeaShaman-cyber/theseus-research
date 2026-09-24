# SynthID surrogate lab

Small reproducibility lab for [research issue #78](https://github.com/TeaShaman-cyber/theseus-research/issues/78).

It answers one narrow question: can the public SynthID watermark mechanics and a simple reference-style weighted-mean score be exercised deterministically with a **known lab key** on a hosted CPU runner?

It deliberately does **not**:

- read the private DeepSeek corpus;
- claim to detect Anthropic's production Claude watermark;
- contain Anthropic keys or detector credentials;
- optimize watermark removal;
- promote a surrogate score into provider attribution.

`run_smoke.py` generates synthetic token streams from uniform pseudo-logits, with and without the public lab watermark configuration. It scores both populations using G-values from Hugging Face's SynthID implementation and a small Torch translation of DeepMind's published weighted-mean formula. A fixed 10% token-substitution pass is recorded only as a robustness smoke-test; it is not a gate and is not tuned for removal.

The GitHub Actions workflow pins the exact Transformers source revision used for the experiment and uses CPU-only PyTorch. The receipt is uploaded as a CI artifact. A passing receipt means only `SURROGATE_ONLY` mechanics worked on that runner.
