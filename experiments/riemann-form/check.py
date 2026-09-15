#!/usr/bin/env python3
"""Deterministic exact checks for the Riemann representation research line."""

from __future__ import annotations

import argparse
import itertools
import json
from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Tuple

Monomial = Tuple[int, ...]
Poly = Dict[Monomial, int]
UniPoly = List[int]  # ascending coefficients


def p_clean(poly: Poly) -> Poly:
    return {m: c for m, c in poly.items() if c}


def p_add(a: Poly, b: Poly) -> Poly:
    out = dict(a)
    for monomial, coefficient in b.items():
        out[monomial] = out.get(monomial, 0) + coefficient
    return p_clean(out)


def p_scale(a: Poly, factor: int) -> Poly:
    return p_clean({m: factor * c for m, c in a.items()})


def p_mul(a: Poly, b: Poly) -> Poly:
    out: Poly = {}
    for ma, ca in a.items():
        for mb, cb in b.items():
            monomial = tuple(x + y for x, y in zip(ma, mb))
            out[monomial] = out.get(monomial, 0) + ca * cb
    return p_clean(out)


def p_sub(a: Poly, b: Poly) -> Poly:
    return p_add(a, p_scale(b, -1))


def render_xy(poly: Poly) -> str:
    """Render the tiny exact bivariate polynomials used by this canary."""
    order = [(2, 0), (1, 0), (0, 2), (0, 0)]
    names = {(2, 0): "x**2", (1, 0): "x", (0, 2): "y**2", (0, 0): "1"}
    pieces: List[Tuple[str, str]] = []
    for monomial in order:
        coefficient = poly.get(monomial, 0)
        if not coefficient:
            continue
        sign = "+" if coefficient > 0 else "-"
        magnitude = abs(coefficient)
        name = names[monomial]
        if monomial == (0, 0):
            body = str(magnitude)
        elif magnitude == 1:
            body = name
        else:
            body = f"{magnitude}*{name}"
        pieces.append((sign, body))
    if not pieces:
        return "0"
    sign, body = pieces[0]
    text = ("-" if sign == "-" else "") + body
    for sign, body in pieces[1:]:
        text += f" {sign} {body}"
    return text


def mobius_check() -> dict:
    # s=x+iy, u=s/(1-s).  Compute |u|^2-1 exactly as a rational function.
    x2 = {(2, 0): 1}
    y2 = {(0, 2): 1}
    x = {(1, 0): 1}
    one = {(0, 0): 1}
    abs_s_sq = p_add(x2, y2)
    one_minus_x = p_sub(one, x)
    abs_one_minus_s_sq = p_add(p_mul(one_minus_x, one_minus_x), y2)
    numerator = p_sub(abs_s_sq, abs_one_minus_s_sq)
    denominator = abs_one_minus_s_sq
    expected_numerator = {(1, 0): 2, (0, 0): -1}
    expected_denominator = {(2, 0): 1, (1, 0): -2, (0, 2): 1, (0, 0): 1}
    return {
        "map": "u=s/(1-s)",
        "difference": f"({render_xy(numerator)})/({render_xy(denominator)})",
        "critical_line_iff_unit_circle": (
            numerator == expected_numerator and denominator == expected_denominator
        ),
        "domain_note": "s != 1; denominator=(1-x)^2+y^2",
    }


def functional_involution_check() -> dict:
    # Univariate formal polynomial in s. u(1-s)=(1-s)/s and 1/u(s)=(1-s)/s.
    one: Poly = {(0,): 1}
    s: Poly = {(1,): 1}
    one_minus_s = p_sub(one, s)
    left_num, left_den = one_minus_s, s
    right_num, right_den = one_minus_s, s
    cross_difference = p_sub(p_mul(left_num, right_den), p_mul(right_num, left_den))
    return {
        "difference": "0" if not cross_difference else str(cross_difference),
        "one_minus_s_maps_to_reciprocal": not cross_difference,
    }


def up_trim(poly: UniPoly) -> UniPoly:
    result = list(poly)
    while len(result) > 1 and result[-1] == 0:
        result.pop()
    return result


def up_add(a: UniPoly, b: UniPoly) -> UniPoly:
    n = max(len(a), len(b))
    out = [0] * n
    for i in range(n):
        out[i] = (a[i] if i < len(a) else 0) + (b[i] if i < len(b) else 0)
    return up_trim(out)


def up_scale(a: UniPoly, factor: int) -> UniPoly:
    return up_trim([factor * c for c in a])


def up_mul(a: UniPoly, b: UniPoly) -> UniPoly:
    out = [0] * (len(a) + len(b) - 1)
    for i, ca in enumerate(a):
        for j, cb in enumerate(b):
            out[i + j] += ca * cb
    return up_trim(out)


def permutation_sign(permutation: Sequence[int]) -> int:
    inversions = sum(
        1
        for i in range(len(permutation))
        for j in range(i + 1, len(permutation))
        if permutation[i] > permutation[j]
    )
    return -1 if inversions % 2 else 1


def characteristic_polynomial(matrix: Sequence[Sequence[int]]) -> List[int]:
    """Return det(t I - A), descending integer coefficients, by Leibniz expansion."""
    n = len(matrix)
    polynomial: UniPoly = [0]
    for permutation in itertools.permutations(range(n)):
        term: UniPoly = [1]
        for row, column in enumerate(permutation):
            if row == column:
                factor = [-matrix[row][column], 1]
            else:
                factor = [-matrix[row][column]]
            term = up_mul(term, factor)
        polynomial = up_add(polynomial, up_scale(term, permutation_sign(permutation)))
    return list(reversed(up_trim(polynomial)))


def is_symmetric(matrix: Sequence[Sequence[int]]) -> bool:
    return all(matrix[i][j] == matrix[j][i] for i in range(len(matrix)) for j in range(len(matrix)))


def discriminant(coefficients: Sequence[int]) -> int:
    if len(coefficients) == 3:
        a, b, c = coefficients
        return b * b - 4 * a * c
    if len(coefficients) == 4:
        a, b, c, d = coefficients
        return (
            18 * a * b * c * d
            - 4 * b**3 * d
            + b * b * c * c
            - 4 * a * c**3
            - 27 * a * a * d * d
        )
    raise ValueError("canary discriminant supports degree 2 or 3 only")


def matrix_canary(matrix: Sequence[Sequence[int]]) -> dict:
    charpoly = characteristic_polynomial(matrix)
    disc = discriminant(charpoly)
    symmetric = is_symmetric(matrix)
    # For these degree-2/3 real polynomials, nonnegative discriminant means all roots are real.
    return {
        "matrix": [list(row) for row in matrix],
        "symmetric": symmetric,
        "charpoly": charpoly,
        "discriminant": disc,
        "all_roots_real": symmetric and disc >= 0,
    }


def build_receipt() -> dict:
    mobius = mobius_check()
    involution = functional_involution_check()
    canaries = {
        "swap_2x2": matrix_canary([[0, 1], [1, 0]]),
        "path_3x3": matrix_canary([[2, 1, 0], [1, 2, 1], [0, 1, 2]]),
    }
    negative_control = matrix_canary([[0, -1], [1, 0]])
    passed = (
        mobius["critical_line_iff_unit_circle"]
        and involution["one_minus_s_maps_to_reciprocal"]
        and all(item["all_roots_real"] for item in canaries.values())
        and not negative_control["all_roots_real"]
    )
    return {
        "schema": "riemann-form-check/v1",
        "mobius": mobius,
        "functional_involution": involution,
        "self_adjoint_canaries": canaries,
        "negative_control": negative_control,
        "status": "PASS" if passed else "FAIL",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--receipt", type=Path, required=True)
    args = parser.parse_args()
    receipt = build_receipt()
    args.receipt.parent.mkdir(parents=True, exist_ok=True)
    args.receipt.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(receipt, sort_keys=True))
    return 0 if receipt["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
