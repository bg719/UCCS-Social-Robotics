__version__ = "0.0.0"
__author__ = 'ancient-sentinel'

import abc
from constants import CTYPE_NONE


class MotionSequenceContext(object):
    """The context for a motion sequence."""

    __metaclass__ = abc.ABCMeta

    @abc.abstractproperty
    def extensive_validation(self):
        """Indicates whether extensive validation will be performed
         before sequences are sent to the motion service."""
        return False

    @abc.abstractproperty
    def motion_service(self):
        """Gets the motion service."""
        return None

    @abc.abstractproperty
    def session(self):
        """Gets the qi session for this context."""
        return None

    @abc.abstractmethod
    def check_sequence(self, sequence, extensive=False):
        """
        Checks that the sequence is valid.

        :param sequence: (sequence.MotionSequence)
            The motion sequence.
        :param extensive: (bool) A flag indicating
            whether to recheck each key frame in the
            sequence for validity.
        :return: True if the sequence is valid;
            otherwise, False.
        """
        return False

    def execute_sequence(self, sequence):
        """
        Sends the motion sequence to the motion service to be
        executed and returns the result.

        :param sequence: The motion sequence.
        :return: The execution result or None if the motion
            service is not available.
        """
        if not self.motion_service:
            return None
        elif not self.check_sequence(sequence, self.extensive_validation):
            raise ValueError('Motion sequence failed validation.')
        return self.motion_service.executeSequence(self.get_name(), sequence)

    @abc.abstractmethod
    def get_bounds(self):
        """
        Gets the bounds on the region where the motion sequence
        is to take place.

        :return: The bounds or None if the context's region
            is unbounded.
        """
        return None

    @abc.abstractmethod
    def get_ctype(self):
        """Gets the context type."""
        return CTYPE_NONE

    @abc.abstractmethod
    def get_name(self):
        """Gets the context name."""
        return None

    @abc.abstractmethod
    def get_or_set_initial_pose(self):
        """
        Either returns the string identifier for a named pose,
        or attempts to set the initial position.

        :return: (Union[str, bool]) The pose identifier; or, True
            if the initial position was set successfully, False if
            setting the initial position failed.
        """
        return False

    def register(self):
        """
        Registers this context with the motion service.

        :return: True if the registration was successful;
            otherwise, False.
        """
        if self.motion_service is None:
            return False
        return self.motion_service.registerContext(self)

    def unregister(self):
        """
        Unregisters this context from the motion service.

        :return: True if this context was formerly registered and
            successfully unregistered; otherwise, False.
        """
        if self.motion_service is None:
            return False
        return self.motion_service.removeContext(self.get_name)
