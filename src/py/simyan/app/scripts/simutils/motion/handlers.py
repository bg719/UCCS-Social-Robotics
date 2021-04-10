__version__ = "0.0.0"
__author__ = 'ancient-sentinel'

import abc

from models import ExecutionResult


class MotionSequenceHandler:
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def handle_seq(self, context, sequence):
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
