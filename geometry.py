from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple, List

EPS = 1e-9


@dataclass(frozen=True)
class LineABC:
    A: float
    B: float
    C: float


def validate_in_range(values: List[float], lo: float, hi: float) -> None:
    for v in values:
        if v < lo - EPS or v > hi + EPS:
            raise ValueError(f"Value {v} is out of range [{lo}; {hi}].")


def line_from_general(A: float, B: float, C: float) -> LineABC:
    if abs(A) <= EPS and abs(B) <= EPS:
        raise ValueError("Invalid general-form line: A and B cannot both be 0 (A^2 + B^2 != 0).")
    return LineABC(A, B, C)


def line_from_point_normal(x0: float, y0: float, l: float, m: float) -> LineABC:
    if abs(l) <= EPS and abs(m) <= EPS:
        raise ValueError("Invalid form-(6) line: normal (l,m) cannot be (0,0) (l^2 + m^2 != 0).")

    A = l
    B = m
    C = -(l * x0 + m * y0)
    return LineABC(A, B, C)


def _classify_pair_with_det(l1: LineABC, l2: LineABC) -> Tuple[str, float]:
    A1, B1, C1 = l1.A, l1.B, l1.C
    A2, B2, C2 = l2.A, l2.B, l2.C

    D = A1 * B2 - A2 * B1
    if abs(D) > EPS:
        return "intersect", D

    # CHANGED: removed local tol = 1e-7 and use global EPS consistently.
    if abs(A1 * C2 - A2 * C1) <= EPS and abs(B1 * C2 - B2 * C1) <= EPS:
        return "coincident", D

    return "parallel", D

# CHANGED: now classification is delegated to helper above.
def classify_pair(l1: LineABC, l2: LineABC) -> str:
    classification, _ = _classify_pair_with_det(l1, l2)
    return classification

# CHANGED: determinant is reused from helper instead of recalculating it again.
def intersection_point(l1: LineABC, l2: LineABC) -> Optional[Tuple[float, float]]:
    classification, D = _classify_pair_with_det(l1, l2)
    if classification != "intersect":
        return None

    A1, B1, C1 = l1.A, l1.B, l1.C
    A2, B2, C2 = l2.A, l2.B, l2.C

    x = (B1 * C2 - B2 * C1) / D
    y = (C1 * A2 - C2 * A1) / D
    return (x, y)



def _same_point(p1: Tuple[float, float], p2: Tuple[float, float], eps: float = 1e-7) -> bool:
    return abs(p1[0] - p2[0]) <= eps and abs(p1[1] - p2[1]) <= eps


def unique_points(points: List[Tuple[float, float]]) -> List[Tuple[float, float]]:
    uniq: List[Tuple[float, float]] = []
    for p in points:
        if not any(_same_point(p, q) for q in uniq):
            uniq.append(p)
    return uniq


def analyze_three(l0: LineABC, l1: LineABC, l2: LineABC) -> dict:
    lines = [l0, l1, l2]
    pairs = [(0, 1), (0, 2), (1, 2)]

    pair_status = {}
    pair_points = {}
    pts: List[Tuple[float, float]] = []

    for i, j in pairs:
        s = classify_pair(lines[i], lines[j])
        pair_status[(i, j)] = s
        pt = intersection_point(lines[i], lines[j])
        pair_points[(i, j)] = pt
        if pt is not None:
            pts.append(pt)

    uniq = unique_points(pts)

    coinc_pairs = [p for p in pairs if pair_status[p] == "coincident"]
    special = None

    if len(coinc_pairs) == 3:
        special = "all_three_coincident"
        uniq = []
        return {
            "pair_status": pair_status,
            "pair_points": pair_points,
            "unique_points": uniq,
            "special": special,
        }

    if len(coinc_pairs) >= 1:
        i, j = coinc_pairs[0]
        k = 3 - i - j
        rel = classify_pair(lines[i], lines[k])

        if rel == "coincident":
            special = "all_three_coincident"
            uniq = []
        elif rel == "parallel":
            special = "two_coincident_third_parallel"
            uniq = []
        else:
            special = "two_coincident_third_intersects"
            pt = intersection_point(lines[i], lines[k])
            uniq = [] if pt is None else [pt]

    return {
        "pair_status": pair_status,
        "pair_points": pair_points,
        "unique_points": uniq,
        "special": special,
    }