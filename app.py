from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np


from typing import Tuple
from geometry import (
    line_from_general,
    line_from_point_normal,
    validate_in_range,
    analyze_three,
)


RANGE_LO = -146.0
RANGE_HI = 146.0


def _read_floats(prompt: str, count: int) -> Tuple[float, ...]:
    s = input(prompt).strip()
    parts = s.split()
    if len(parts) != count:
        raise ValueError(f"Expected {count} numbers, got {len(parts)}.")
    try:
        return tuple(float(p) for p in parts)
    except ValueError:
        raise ValueError("All inputs must be numeric (int or float).")


def _fmt_point(p: Tuple[float, float]) -> str:
    return f"({p[0]:.6f}, {p[1]:.6f})"

def plot_lines(lines, intersection_points):
    x_min, x_max = RANGE_LO, RANGE_HI
    y_min, y_max = RANGE_LO, RANGE_HI

    x_vals = np.linspace(x_min, x_max, 1200)

    for i, line in enumerate(lines):
        A, B, C = line.A, line.B, line.C

        if abs(B) > 1e-9:
            y_vals = (-A * x_vals - C) / B
            plt.plot(x_vals, y_vals, label=f"L{i}")
        else:
            if abs(A) > 1e-9:
                x_const = -C / A
                plt.axvline(x=x_const, label=f"L{i}")

    for idx, p in enumerate(intersection_points):
        plt.scatter(p[0], p[1], s=80)
        plt.annotate(f"P{idx+1}", (p[0], p[1]), textcoords="offset points", xytext=(6, 6))

    plt.xlim(x_min, x_max)
    plt.ylim(y_min, y_max)

    plt.axhline(0)
    plt.axvline(0)
    plt.grid(True)
    plt.legend()
    plt.title("Visualization of 3 Lines ")

    plt.gca().set_aspect("equal", adjustable="box")

    plt.show()

def main() -> None:
    print("Lab: 3 lines, variant (1,6,6), input range [-146; 146]")
    print("Form (1):  A*x + B*y + C = 0   with A^2 + B^2 != 0")
    print("Form (6):  point M(x0,y0) + normal N(l,m)")
    print("           l*(x - x0) + m*(y - y0) = 0   with l^2 + m^2 != 0")
    print()

    try:
        A, B, C = _read_floats("Enter L0 in general form (A B C): ", 3)
        x01, y01, l1, m1 = _read_floats("Enter L1 in form (6) (x0 y0 l m): ", 4)
        x02, y02, l2, m2 = _read_floats("Enter L2 in form (6) (x0 y0 l m): ", 4)

        validate_in_range([A, B, C, x01, y01, l1, m1, x02, y02, l2, m2], RANGE_LO, RANGE_HI)

        L0 = line_from_general(A, B, C)
        L1 = line_from_point_normal(x01, y01, l1, m1)
        L2 = line_from_point_normal(x02, y02, l2, m2)

        res = analyze_three(L0, L1, L2)

    except ValueError as e:
        print(f"Input/validation error: {e}")
        return

    special = res["special"]
    uniq = res["unique_points"]

    if special == "all_three_coincident":
        print("Lines coincide")
        return

    if special == "two_coincident_third_parallel":
        print("Lines do not intersect")
        return

    if special == "two_coincident_third_intersects":
        print(f"Single intersection point: {_fmt_point(uniq[0])}")
        return

    if len(uniq) == 0:
        print("Lines do not intersect")
    elif len(uniq) == 1:
        print(f"Single intersection point: {_fmt_point(uniq[0])}")
    elif len(uniq) == 2:
        print(f"Two intersection points: {_fmt_point(uniq[0])} and {_fmt_point(uniq[1])}")
    else:
        print(
            f"Three intersection points: "
            f"{_fmt_point(uniq[0])}, {_fmt_point(uniq[1])}, {_fmt_point(uniq[2])}"
        )

    plot_lines([L0, L1, L2], uniq)
if __name__ == "__main__":
    main()