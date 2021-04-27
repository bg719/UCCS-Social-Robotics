__version__ = "0.0.0"
__author__ = 'ancient-sentinel'

import abc
from models import ExecutionResult

# Constants
TYPE = 0
"""The index of the invocation type."""
ARGS = 1
"""The index of the invocation arguments list."""
EFFECTORS = 0
"""The index of the effectors vector in an invocation argument list."""
FRAMES = 1
"""The index of the frames vector in an invocation argument list."""
PATHS = 2
"""The index of the paths vector in an invocation argument list."""
MASKS = 3
"""The index of the masks vector in an invocation argument list."""
TIMES = 4
"""The index of the times vector in an invocation argument list."""


def new_invocation_args():
    """
    Returns a new, emtpy invocation argument set.
    
    :return: a 5-tuple of lists, corresponding with
        ([effectors_vector], [paths_vector], [frames_vector],
         [masks_vector], [times_vector])
    """
    return [], [], [], [], []


def are_equal(p1, p2, thresholds=0.001):
    """
    Determines whether `p1` and `p2` are the equal within the
    specified threshold(s).

    :param p1: (List[float]) The first position/transform.
    :param p2: (List[float]) The second position/transform.
    :param thresholds: (Union[float, Iterable[float, Iterable[float]]])
        The threshold(s) for testing positional/transformational
        equality. Either a single value to be used for all
        comparisons or a 2 element list of thresholds to be
        applied to corresponding indices for positional and
        transformational vectors, respectively.
    :return:
    """
    len_p1 = len(p1)
    if len_p1 != len(p2):
        return False

    # check/set thresholds value
    if isinstance(thresholds, float):
        thresholds = [thresholds] * len(p1)
    elif isinstance(thresholds, (list, tuple)) and len(thresholds) == 2:
        if len_p1 == 6:
            thresholds = thresholds[0]
        elif len_p1 == 12:
            thresholds = thresholds[1]
    else:
        thresholds = [0] * len_p1

    # check equality of p1 and p2
    for i in range(len_p1):
        try:
            threshold = thresholds[i]
        except IndexError:
            threshold = 0

        if p1[i] - p2[i] > threshold:
            return False
    return True


class KeyframeException(Exception):
    """An exception raised due to keyframe errors."""

    def __init__(self, message):
        self.message = message

    @staticmethod
    def type_mismatch(current, previous):
        return KeyframeException(
            "Keyframe type mismatch. Cannot execute keyframe " +
            "of type {0} with keyframe of type {1}.".format(
                current.kftype, previous.kftype))


class KeyframeTypeError(ValueError):
    """Invalid keyframe type provided."""

    def __init__(self, kftype, message=None):
        """
        Initializes a new keyframe type error.

        :param kftype: (str) The invalid keyframe type.
        :param message: (str) A message describing the error.
        """
        self.kftype = kftype
        self.message = message


class MotionSequenceHandler:
    """The base class for motion sequence handlers."""
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def handle_sequence(self, context, sequence, motion_proxy, posture_proxy):
        """
        Handles the execution of the specified motion `sequence` within the
        scope of the provided motion sequence `context`.

        NOTE: Since the context and motion sequence objects are passed
        through the qi framework to the motion service where the handler
        is managed, their type information will not be available to use to
        check that they are the correct type. All validation must be based
        on whether the attributes and methods they expose on this side are
        sufficient for the handler to execute.

        :param context: (contexts.MotionSequenceContext)
            The motion sequence context.
        :param sequence: (models.MotionSequence)
            The motion sequence.
        :param motion_proxy: (ALMotion)
            The motion service or proxy.
        :param posture_proxy: (ALRobotPosture)
            The posture service or proxy.
        :return: (models.ExecutionResult)
            The result of executing the sequence.
        """
        return ExecutionResult.error_result("Handling not implemented.")

    @abc.abstractmethod
    def handles_type(self, ctype):
        """
        Determines whether this handler can handle the specified
        motion sequence context type.

        :param ctype: (str) The motion sequence context type.
        :return: True if this handler can handle the context type;
            otherwise, False.
        """
        return False

