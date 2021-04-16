__version__ = "0.0.0"
__author__ = 'ancient-sentinel'

import abc
import constants as const

from models import KeyFrame, to_point


class MotionSequence:
    """The base class for motion sequences."""
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def add_keyframe(self, keyframe):
        """
        Appends the keyframe to the sequence.

        :param keyframe: (models.KeyFrame) The keyframe.
        :return: True if the keyframe was added successfully;
            otherwise, False.
        """
        return False

    @abc.abstractmethod
    def get_keyframes(self):
        """
        Gets the list of keyframes which define the motion sequence.

        :return: (List[models.KeyFrame]) The list of keyframes.
        """
        return []

    @abc.abstractmethod
    def validate(self, exhaustive=False):
        """
        Determines whether the motion sequence is valid.

        :param exhaustive: (bool) A flag indicating whether to perform
            exhaustive validation. The goal of exhaustive validation is
            to catch any errors detectable prior to execution. A non-
            exhaustive validation is intended to be quick, cheap, and
            check only for the most likely sources of errors.
        :return: True if the motion sequence is valid; otherwise False
        """
        return False


class PlanarSequence(MotionSequence):

    def __init__(self, effectors):
        self.effectors = effectors
        self.keyframes = []

    def new_keyframe(self, start, end, duration, effectors=None):
        """
        Adds a new keyframe between the provided starting and ending
        positions with the specified duration.

        :param start: (Iterable[float]) The starting position.
        :param end: (Iterable[float]) The ending position.
        :param duration: (float) The duration of the frame.
        :param effectors: (Union[List[str], str])
            The effector(s) targeted by the keyframe. Overrides
            the default effectors defined for this planar sequence.
        :return: True if the new keyframe was added successfully;
            otherwise False.
        """
        start = to_point(start)
        end = to_point(end)

        if not effectors:
            effectors = self.effectors
        keyframe = KeyFrame(start, end, duration, effectors, const.KFTYPE_PLANAR)
        self.keyframes.append(keyframe)

    def add_keyframe(self, keyframe):
        if self.check_keyframe(keyframe):
            self.keyframes.append(keyframe)
            return True
        return False

    def get_keyframes(self):
        return self.keyframes

    def check_keyframe(self, keyframe):
        return keyframe.complete() and keyframe.kftype == const.KFTYPE_PLANAR

    def validate(self, exhaustive=False):
        pass
