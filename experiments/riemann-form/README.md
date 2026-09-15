# Riemann form check

This is a small executable scratchpad for mathematical claims that are already precise enough to check outside conversational context.

It is intentionally not a proof engine and does not score hypotheses.

## Checks in v1

1. **Critical line -> unit circle**

   For the Mobius map

   ```text
   u = s / (1 - s),  s = x + i y
   ```

   the checker derives exactly

   ```text
   |u|^2 - 1 = (2*x - 1) / (x^2 - 2*x + y^2 + 1).
   ```

   On the domain of the map, `|u| = 1` iff `Re(s) = 1/2`.

2. **Functional-equation involution -> reciprocal map**

   The checker verifies algebraically that

   ```text
   s -> 1 - s
   ```

   becomes

   ```text
   u -> 1/u.
   ```

3. **Finite self-adjoint real-rooted canaries**

   Characteristic polynomials are computed from integer matrices by exact Leibniz expansion, not stored as constants. Two symmetric matrices are checked for real-rootedness using exact polynomial discriminants.

4. **Negative control**

   The real rotation matrix

   ```text
   [[0, -1],
    [1,  0]]
   ```

   has characteristic polynomial `t^2 + 1`; the checker must reject it as real-rooted.

## CI role

GitHub Actions reruns the exact checks, regenerates a deterministic JSON receipt, compares it with the versioned reference receipt, and uploads the run receipt as an artifact.

The purpose is external verification and memory:

```text
claim -> executable check -> CI -> receipt -> rerun on change
```

## Explicit boundary

A green run does **not** prove the Riemann Hypothesis. In particular v1 does not prove:

- that a proposed physical partition function represents all zeta zeros;
- applicability of a Lee-Yang theorem to a proposed model;
- membership of the Riemann Xi function in the Laguerre-Polya class;
- convergence of finite spectral models or determinants to Xi.

Those are candidate future checks only after each statement has been reduced to an executable, theorem-level claim.
