__version__ = "0.0.0"
__author__ = 'ancient-sentinel'

import numpy as np


def to_point(p, n=3):
    """
    Attempts to convert the parameter `p` into a point in `n`-space.
    Parameters which result in a valid point definition include:

    * Numeric iterables with `n` elements,
    * The value 0 (corresponding with the origin).

    :param p: (Union[Iterable[float], float]) The parameter to be
        converted into a point.
    :param n: (int) The dimension of the space.
    :return: The point as an n-element numpy array, or None if the
        parameter could not be successfully converted to a point.
    """
    if n < 1:
        return None
    elif p == 0:
        return np.zeros(n)
    elif isinstance(p, np.ndarray) and len(p) == n:
        return p
    elif len(p) == n and all(isinstance(x, float) for x in p):
        return np.ndarray(p)
    return None
