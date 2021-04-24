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
    Returns a new, emtpy invocation argument list.
    
    :return: a 5-tuple of lists, corresponding with
        ([effectors_vector], [paths_vector], [frames_vector],
         [masks_vector], [times_vector])
    """
    return [], [], [], [], []


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

