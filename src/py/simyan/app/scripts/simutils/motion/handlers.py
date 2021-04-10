__version__ = "0.0.0"
__author__ = 'ancient-sentinel'

import abc

from models import ExecutionResult


class MotionSequenceHandler:
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def handle_seq(self, context, sequence):
        """
        Handles the execution of the specified motion `sequence` withing the
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
        :return: (models.ExecutionResult) The result of executing the sequence.
        """
        return ExecutionResult.error_result("Handling not implemented.")

    @abc.abstractmethod
    def handles_type(self, type):
        """
        Determines whether this handler can handle the specified
        motion sequence context type.

        :param type: (str) The motion sequence context type.
        :return: True if this handler can handle the context type;
            otherwise, False.
        """
        return False


class PlanarSequenceHandler:

    def __init__(self):
        pass