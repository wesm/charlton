# This file is part of Charlton
# Copyright (C) 2011 Nathaniel Smith <njs@pobox.com>
# See file COPYING for license information.

# Some generic utilities.

__all__ = ["atleast_2d_column_default", "to_unique_tuple",
           "widest_float", "widest_complex", "wide_dtype_for", "widen",
           "odometer_iter",
           ]

import numpy as np

# Like np.atleast_2d, but this converts lower-dimensional arrays into columns,
# instead of rows.
def atleast_2d_column_default(a):
    a = np.atleast_1d(a)
    if a.ndim <= 1:
        a = a.reshape((-1, 1))
    assert a.ndim >= 2
    return a

def test_atleast_2d_column_default():
    assert np.all(atleast_2d_column_default([1, 2, 3]) == [[1], [2], [3]])

    assert atleast_2d_column_default(1).shape == (1, 1)
    assert atleast_2d_column_default([1]).shape == (1, 1)
    assert atleast_2d_column_default([[1]]).shape == (1, 1)
    assert atleast_2d_column_default([[[1]]]).shape == (1, 1, 1)

    assert atleast_2d_column_default([1, 2, 3]).shape == (3, 1)
    assert atleast_2d_column_default([[1], [2], [3]]).shape == (3, 1)


def to_unique_tuple(seq):
    seq_new = []
    for obj in seq:
        if obj not in seq_new:
            seq_new.append(obj)
    return tuple(seq_new)

def test_to_unique_tuple():
    assert to_unique_tuple([1, 2, 3]) == (1, 2, 3)
    assert to_unique_tuple([1, 3, 3, 2, 3, 1]) == (1, 3, 2)
    assert to_unique_tuple([3, 2, 1, 4, 1, 2, 3]) == (3, 2, 1, 4)


for float_type in ("float128", "float96", "float64"):
    if hasattr(np, float_type):
        widest_float = getattr(np, float_type)
        break
else:
    assert False
for complex_type in ("complex256", "complex196", "complex128"):
    if hasattr(np, complex_type):
        widest_complex = getattr(np, complex_type)
        break
else:
    assert False

def wide_dtype_for(arr):
    arr = np.asarray(arr)
    if (np.issubdtype(arr.dtype, np.integer)
        or np.issubdtype(arr.dtype, np.floating)):
        return widest_float
    elif np.issubdtype(arr.dtype, np.complexfloating):
        return widest_complex
    raise ValueError, "cannot widen a non-numeric type %r" % (arr.dtype,)

def widen(arr):
    return np.asarray(arr, dtype=wide_dtype_for(arr))

def test_wide_dtype_for_and_widen():
    assert np.allclose(widen([1, 2, 3]), [1, 2, 3])
    assert widen([1, 2, 3]).dtype == widest_float
    assert np.allclose(widen([1.0, 2.0, 3.0]), [1, 2, 3])
    assert widen([1.0, 2.0, 3.0]).dtype == widest_float
    assert np.allclose(widen([1+0j, 2, 3]), [1, 2, 3])
    assert widen([1+0j, 2, 3]).dtype == widest_complex
    from nose.tools import assert_raises
    assert_raises(ValueError, widen, ["hi"])

def odometer_iter(maximums):
    cur = [0] * len(maximums)
    yield tuple(cur)
    if not maximums:
        return
    while True:
        cur[-1] += 1
        for i in xrange(len(cur) - 1, 0, -1):
            if cur[i] >= maximums[i]:
                cur[i] = 0
                cur[i - 1] += 1
        if cur[0] >= maximums[0]:
            break
        yield tuple(cur)

def test_odometer_iter():
    def t(a, b):
        result = list(odometer_iter(a))
        print result
        assert result == b
    t([], [()])
    t([3], [(0,), (1,), (2,)])
    t([2, 3, 1],
      [(0, 0, 0),
       (0, 1, 0),
       (0, 2, 0),
       (1, 0, 0),
       (1, 1, 0),
       (1, 2, 0)])
