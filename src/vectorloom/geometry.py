"""2-D affine geometry for Vector Loom.

A transform is a plain 6-tuple (a, b, c, d, e, f) representing the 2x3 matrix:

    x' = a*x + c*y + e
    y' = b*x + d*y + f

Tuples are used instead of a Matrix class because they are tiny, immutable,
JSON-irrelevant runtime values, and the operations read cleanly as functions.
Everything in the runtime flattens geometry to world-space points through these
helpers, so translate, scale, and rotate all compose uniformly.
"""

import math


IDENTITY = (1.0, 0.0, 0.0, 1.0, 0.0, 0.0)


def translate(tx, ty):
    """Return a transform that shifts points by (tx, ty)."""
    return (1.0, 0.0, 0.0, 1.0, float(tx), float(ty))


def scale(sx, sy):
    """Return a transform that scales points by (sx, sy) about the origin."""
    return (float(sx), 0.0, 0.0, float(sy), 0.0, 0.0)


def rotate(degrees):
    """Return a transform that rotates points clockwise about the origin.

    Clockwise is chosen because Canvas y grows downward, so a positive angle
    rotates the way a user expects on screen.
    """
    r = math.radians(degrees)
    cos = math.cos(r)
    sin = math.sin(r)
    return (cos, sin, -sin, cos, 0.0, 0.0)


def compose(outer, inner):
    """Return the transform that applies `inner` first, then `outer`.

    This is ordinary matrix multiplication outer @ inner. Walking down a tree,
    a child's world transform is compose(parent_world, child_local).
    """
    a1, b1, c1, d1, e1, f1 = outer
    a2, b2, c2, d2, e2, f2 = inner
    return (
        a1 * a2 + c1 * b2,
        b1 * a2 + d1 * b2,
        a1 * c2 + c1 * d2,
        b1 * c2 + d1 * d2,
        a1 * e2 + c1 * f2 + e1,
        b1 * e2 + d1 * f2 + f1,
    )


def apply_point(m, x, y):
    """Transform a single point, returning a (x, y) float tuple."""
    a, b, c, d, e, f = m
    return (a * x + c * y + e, b * x + d * y + f)


def apply_points(m, points):
    """Transform a sequence of (x, y) points, returning a list of tuples."""
    a, b, c, d, e, f = m
    return [(a * x + c * y + e, b * x + d * y + f) for (x, y) in points]


def apply_vector(m, vx, vy):
    """Transform a direction/delta, ignoring translation. Use for moving deltas."""
    a, b, c, d, _e, _f = m
    return (a * vx + c * vy, b * vx + d * vy)


def invert(m):
    """Return the inverse transform. Raises ZeroDivisionError on a singular matrix."""
    a, b, c, d, e, f = m
    det = a * d - b * c
    return (
        d / det,
        -b / det,
        -c / det,
        a / det,
        (c * f - d * e) / det,
        (b * e - a * f) / det,
    )


def from_trs(tx, ty, sx, sy, rotate_degrees):
    """Build a transform from translate, scale, then rotate components.

    Application order on a point is rotate, then scale, then translate, which
    matches how a placed structure reads: spin it, size it, then move it.
    """
    m = translate(tx, ty)
    m = compose(m, scale(sx, sy))
    if rotate_degrees:
        m = compose(m, rotate(rotate_degrees))
    return m


def decompose(m):
    """Decompose a transform into {tx, ty, sx, sy, rotate} matching from_trs.

    Inverts from_trs (translate ∘ scale ∘ rotate). Exact when the matrix is a
    translate/scale/rotate with no shear; a manipulation committed at the root
    under a uniform camera is exact. Shear (possible only when conjugating
    through a rotated, non-uniformly-scaled ancestor) is dropped.
    """
    a, b, c, d, e, f = m
    sx = math.hypot(a, c)
    rotate_degrees = math.degrees(math.atan2(-c, a))
    det = a * d - b * c
    sy = det / sx if sx else math.hypot(b, d)
    return {"tx": e, "ty": f, "sx": sx, "sy": sy, "rotate": rotate_degrees}
