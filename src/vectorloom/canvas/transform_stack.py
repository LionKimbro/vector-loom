"""The drawing-time transform stack for Vector Loom Canvas rendering."""

from copy import deepcopy
import math


def _identity_matrix():
    return (1, 0, 0, 1, 0, 0)


def _matrix_multiply(left, right):
    """Return the affine matrix for applying right, then left."""
    la, lb, lc, ld, le, lf = left
    ra, rb, rc, rd, re, rf = right
    return (
        la * ra + lc * rb,
        lb * ra + ld * rb,
        la * rc + lc * rd,
        lb * rc + ld * rd,
        la * re + lc * rf + le,
        lb * re + ld * rf + lf,
    )


def _translate(x, y):
    return (1, 0, 0, 1, x, y)


def _rotate(angle):
    radians = math.radians(angle)
    cosine = math.cos(radians)
    sine = math.sin(radians)
    return (cosine, sine, -sine, cosine, 0, 0)


def _inverse(matrix):
    a, b, c, d, e, f = matrix
    determinant = a * d - b * c
    if determinant == 0:
        raise ValueError("Transform matrix is not invertible.")
    return (
        d / determinant,
        -b / determinant,
        -c / determinant,
        a / determinant,
        (c * f - d * e) / determinant,
        (b * e - a * f) / determinant,
    )


def apply_matrix(matrix, x, y):
    return (
        matrix[0] * x + matrix[2] * y + matrix[4],
        matrix[1] * x + matrix[3] * y + matrix[5],
    )


def _derive_frame_transform(frame, parent_matrix):
    local_matrix = _matrix_multiply(
        _translate(frame["x"], frame["y"]),
        _rotate(frame["angle"]),
    )
    frame["M"] = _matrix_multiply(parent_matrix, local_matrix)
    frame["Minverse"] = _inverse(frame["M"])


def identity_frame():
    frame = {"x": 0, "y": 0, "angle": 0}
    _derive_frame_transform(frame, _identity_matrix())
    return frame


S = [identity_frame()]


def push_transform(transform):
    frame = {
        "x": transform.get("x", 0),
        "y": transform.get("y", 0),
        "angle": transform.get("angle", 0),
    }
    _derive_frame_transform(frame, S[-1]["M"])
    S.append(frame)


def drop_transform():
    if len(S) == 1:
        raise RuntimeError("Cannot drop the Transform Stack identity root frame.")
    return S.pop()


def peek_transform():
    return deepcopy(S[-1])


def _rederive_top_frame():
    parent_matrix = _identity_matrix() if len(S) == 1 else S[-2]["M"]
    _derive_frame_transform(S[-1], parent_matrix)


def locate(x, y):
    S[-1]["x"] = x
    S[-1]["y"] = y
    _rederive_top_frame()


def slide(dx, dy):
    S[-1]["x"] += dx
    S[-1]["y"] += dy
    _rederive_top_frame()


def turn(delta):
    S[-1]["angle"] += delta
    _rederive_top_frame()


def local_to_world(local_x, local_y):
    return apply_matrix(S[-1]["M"], local_x, local_y)


def world_to_local(world_x, world_y):
    return apply_matrix(S[-1]["Minverse"], world_x, world_y)
