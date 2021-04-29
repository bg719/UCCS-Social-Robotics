__version__ = "0.0.0"
__author__ = 'ancient-sentinel'

import codes
import numpy as np
from utils import to_point


class ExecutionResult:
    """The result of executing a motion sequence."""

    def __init__(self, success, status, message):
        """
        Initializes a new execution result.

        :param success: (bool) True if execution was successful;
            otherwise, False.
        :param status: (int) The status code.
        :param message: (str) The result message.
        """
        self.success = success
        self.status = status
        self.message = message

    @staticmethod
    def success_result(message=None, status=codes.SUCCESS):
        """
        Creates a new success result.

        :param message: (str) The result message.
        :param status: (int) The status code.
        :return: The execution result.
        """
        return ExecutionResult(True, status, message)

    @staticmethod
    def error_result(message, status=codes.GEN_ERROR):
        """
        Creates a new error result with the provided message and
        error code.

        :param message: (str) The error message.
        :param status: (int) The error status code.
        :return: The execution result.
        """
        return ExecutionResult(False, status, message)

    @staticmethod
    def invalid_arg(arg_name):
        """
        Creates a new error result for an invalid argument.

        :param arg_name: (str) The name of the invalid argument.
        :return: The execution result.
        """
        return ExecutionResult(False, codes.BAD_ARG,
                               "Invalid argument: {0}".format(arg_name))

    @staticmethod
    def invalid_kftype(kftype):
        """
        Creates a new error result for an invalid keyframe type.

        :param kftype: (int) The invalid keyframe type.
        :return: The execution result.
        """
        return ExecutionResult(False, codes.BAD_ARG,
                               "Encountered invalid keyframe type: {0}".format(kftype))

    @staticmethod
    def keyframe_exception(exception):
        """
        Creates a new error result for a keyframe exception.

        :param exception: (_handler.KeyframeException) The exception.
        :return: The execution result.
        """
        return ExecutionResult(False, codes.BAD_ARG, exception.message)

    @staticmethod
    def no_such_context(context_name):
        """
        Creates a new error result for a non-existent context.

        :param context_name: (str) The context name.
        :return: The execution result.
        """
        return ExecutionResult(False, codes.NO_CTX,
                               "No registered context named: {0}".format(context_name))


class KeyFrame:

    def __init__(self, start, end, duration, effector, frame, axis_mask,
                 kftype, with_previous=False):
        """
        Creates a new keyframe.

        :param start: (List[float]) (Optional) The starting position of the keyframe.
            If None, the ending position of the previous keyframe will be used as the
            starting position for this one.
        :param end: (List[float]) The ending position of the keyframe.
        :param duration: (float) The duration of the keyframe.
        :param effector: (str) The effector targeted by the keyframe.
        :param frame: (int) The spatial reference frame. Must be in motion.constants.FRAMES.
        :param axis_mask: (int) The axis mask. Must be in motion.constants.AXIS_MASKS.
        :param kftype: (int) The keyframe type. See motion.constants.KFTYPES.
        :param with_previous: (bool) If True, this keyframe will execute concurrently
            with the previous keyframe.
        """
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
