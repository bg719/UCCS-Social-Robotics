__version__ = "0.0.0"
__author__ = 'ancient-sentinel'

import codes
import constants as const
import numpy as np
from utils import to_point


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
        return ExecutionResult(False, codes.BAD_ARG,
                               "Invalid argument: {0}".format(arg_name))

    @staticmethod
    def invalid_kftype(kftype):
        return ExecutionResult(False, codes.BAD_ARG,
                               "Encountered invalid keyframe type: {0}".format(kftype))

    @staticmethod
    def keyframe_exception(exception):
        return ExecutionResult(False, codes.BAD_ARG, exception.message)

    @staticmethod
    def no_such_context(context_name):
        return ExecutionResult(False, codes.NO_CTX,
                               "No registered context named: {0}".format(context_name))


class KeyFrame:

    def __init__(self, start, end, duration, effector, frame, axis_mask,
                 kftype, with_previous=False):
        self.start = start
        self.end = end
        self.duration = duration
        self.effector = effector
        self.frame = frame
        self.axis_mask = axis_mask
        self.kftype = kftype
        self.with_previous = with_previous

    def is_complete(self):
        if self.end is None:
            return False
        elif not self.duration or self.duration < 0:
            return False
        elif self.effector is None:
            return False
        elif not self.kftype:
            return False
        return True


class Plane:
    """
    A plane in 3-space, defined by a `point` in the plane and a `vector`
    which is normal to the plane.
    """

    def __init__(self, point, normal):
        """
        Initializes a new plane instance.

        :param point: (Iterable[float]) A 3D point which resides in the plane.
        :param normal: (Iterable[float]) A 3-space vector normal to the plane.
        """
        self.point = point
        self.normal = normal

    @staticmethod
    def from_points(points):
        """
        Determines the plane which passes through the set of three
        points provided.

        :param points: (Iterable[Iterable[float]]) The 3 points to be used to
            define the plane. All 3 points must be non-collinear in order to
            identify a plane in 3-space.
        :return: The plane containing the 3 specified points, or None
            if two or more of the points were collinear.
        """
        if len(points) == 3:
            return Plane.create_from_points(*points)
        return None

    @staticmethod
    def create_from_points(p1, p2, p3):
        """
        Determines the plane which passes through the three points.

        :param p1: The first point.
        :param p2: The second point.
        :param p3: The third point.
        :return: The plane containing the 3 specified points, or None
            if two or more of the points were collinear.
        """
        p1 = np.array(to_point(p1))
        p2 = np.array(to_point(p2))
        p3 = np.array(to_point(p3))

        u = p3 - p2
        v = p2 - p1

        u_x_v = np.cross(u, v)

        if u_x_v == 0:
            return None

        return Plane(p1, u_x_v)
