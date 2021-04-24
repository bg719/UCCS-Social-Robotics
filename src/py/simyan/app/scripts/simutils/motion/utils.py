__version__ = "0.0.0"
__author__ = 'ancient-sentinel'


def to_point(p, n=3):
    """
    Attempts to convert the parameter `p` into a point in `n`-space.
    Parameters which result in a valid point definition include:

    * Numeric iterables with `n` elements,
    * The value 0 (corresponding with the origin).

    :param p: (Union[Iterable[float], float]) The parameter to be
        converted into a point.
    :param n: (int) The dimension of the space.
    :return: The point as an n-element list or numpy array, or
        None if the parameter could not be successfully
        converted to a point.
    """
    if p is None or n < 1:
        return None
    elif p == 0:
        return [0] * n
    elif len(p) == n and all(isinstance(x, (float, int)) for x in p):
        return p
    return None
