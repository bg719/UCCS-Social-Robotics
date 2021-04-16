__version__ = "0.0.0"
__author__ = 'ancient-sentinel'

import codes
import numpy as np
import constants as const


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


class ExecutionResult:
    """The result of executing a motion sequence."""

    def __init__(self, success, status, message):
        self.success = success
        self.status = status
        self.message = message

    @staticmethod
    def success_result(message=None, status=codes.SUCCESS):
        return ExecutionResult(True, status, message)

    @staticmethod
    def error_result(message, status=codes.GEN_ERROR):
        return ExecutionResult(False, status, message)

    @staticmethod
    def invalid_arg(arg_name):
        return ExecutionResult(False, codes.BAD_ARG, "Invalid argument: {0}".format(arg_name))

    @staticmethod
    def invalid_kftype(kftype):
        return ExecutionResult(False, codes.BAD_ARG, "Encountered invalid keyframe type: {0}".format(kftype))

    @staticmethod
    def no_such_context(context_name):
        return ExecutionResult(False, codes.NO_CTX, "No registered context named: {0}".format(context_name))


class KeyFrame:

    def __init__(self, start, end, duration,
                 effectors, frame, axis_mask, kftype):
        self.start = start
        self.end = end
        self.duration = duration
        self.effectors = effectors
        self.frame = frame
        self.axis_mask = axis_mask
        self.kftype = kftype

    def complete(self):
        return self.end and self.duration \
               and self.effectors and self.kftype


class Plane:
    """
    A get_plane in 3-space, defined by a `point` in the get_plane and a `vector`
    which is normal to the get_plane.
    """

    def __init__(self, point, normal):
        """
        Initializes a new get_plane instance.

        :param point: (Iterable[float]) A 3D point which resides in the get_plane.
        :param normal: (Iterable[float]) A 3-space vector normal to the get_plane.
        """
        self.point = point
        self.normal = normal

    @staticmethod
    def from_points(points):
        """
        Determines the get_plane which passes through the set of three
        points provided.

        :param points: (Iterable[Iterable[float]]) The 3 points to be used to
            define the get_plane. All 3 points must be non-collinear in order to
            identify a get_plane in 3-space.
        :return: The get_plane containing the 3 specified points, or None
            if two or more of the points were collinear.
        """
        if len(points) == 3:
            return Plane.create_from_points(*points)
        return None

    @staticmethod
    def create_from_points(p1, p2, p3):
        """
        Determines the get_plane which passes through the three points.

        :param p1: The first point.
        :param p2: The second point.
        :param p3: The third point.
        :return: The get_plane containing the 3 specified points, or None
            if two or more of the points were collinear.
        """
        p1 = to_point(p1)
        p2 = to_point(p2)
        p3 = to_point(p3)

        u = p3 - p2
        v = p2 - p1

        u_x_v = np.cross(u, v)

        if u_x_v == 0:
            return None

        return Plane(p1, u_x_v)