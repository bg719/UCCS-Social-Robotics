__version__ = "0.0.0"
__author__ = 'ancient-sentinel'

import abc


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
