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

    # @abc.abstractmethod
    # def validate(self, exhaustive=False):
    #     """
    #     Determines whether the motion sequence is valid.
    #
    #     :param exhaustive: (bool) A flag indicating whether to perform
    #         exhaustive validation. The goal of exhaustive validation is
    #         to catch any errors detectable prior to execution. A non-
    #         exhaustive validation is intended to be quick, cheap, and
    #         check only for the most likely sources of errors.
    #     :return: True if the motion sequence is valid; otherwise False.
    #     """
    #     return False


class AbsoluteSequence(MotionSequence):

    def __init__(self, effectors, frame, axis_mask):
        """
        Initializes a new absolute motion sequence instance.

        :param effectors: (Union[str, Iterable[str]])
            The default effector(s) targeted by this sequence.
            Either the string identifier for a single effector
            or a list of effector identifiers.
        :param frame: (int) The spatial frame.
        :param axis_mask: (int) The default axis mask for
            this sequence.
        """
        self.effectors = effectors
        self.frame = frame
        self.axis_mask = axis_mask
        self._keyframes = []

    def new_position_keyframe(self, start, end, duration,
                              effectors=None, frame=None, axis_mask=None):
        """
        Adds a new keyframe between the provided starting and ending
        absolute positions with the specified duration.

        :param start: (Iterable[float]) The starting position.
        :param end: (Iterable[float]) The ending position.
        :param duration: (float) The duration of the keyframe.
        :param effectors: (Union[List[str], str])
            The effector(s) targeted by the keyframe. Overrides
            the default effectors for this sequence.
        :param frame: (int) The spatial frame. Overrides the
            default frame for this sequence.
        :param axis_mask: (int) The axis mask to use for this
            keyframe. Overrides the default axis mask defined for
            this sequence.
        :return: True if the new keyframe was added successfully;
            otherwise False.
        """
        start = to_point(start, 6)
        end = to_point(end, 6)

        if not effectors:
            effectors = self.effectors

        if not frame:
            frame = self.frame

        if not axis_mask:
            axis_mask = self.axis_mask

        keyframe = KeyFrame(start, end, duration, effectors, frame,
                            axis_mask, const.KFTYPE_ABSOLUTE_POSITION)

        if not keyframe.is_complete():
            return False

        self._keyframes.append(keyframe)
        return True

    def next_position_keyframe(self, end, duration, effectors=None,
                               frame=None, axis_mask=None):
        """
        Adds a new keyframe to the sequence which uses the ending position
        of the previous keyframe as the starting position and moves to the
        specified end position.

        :param end: (Iterable[float]) The ending position.
        :param duration: (float) The duration of the keyframe.
        :param effectors: (Union[List[str], str])
            The effector(s) targeted by the keyframe. Overrides
            the default effectors for this sequence.
        :param frame: (int) The spatial frame. Overrides the
            default frame for this sequence.
        :param axis_mask: (int) The axis mask to use for this
            keyframe. Overrides the default axis mask defined for
            this sequence.
        :return: True if the new keyframe was added successfully;
            otherwise False.
        """
        return self.new_position_keyframe(
            None, end, duration, effectors, frame, axis_mask)

    def new_transform_keyframe(self, start, end, duration,
                               effectors=None, frame=None, axis_mask=None):
        """
        Adds a new keyframe between the provided starting and ending
        absolute transforms with the specified duration.

        :param start: (Iterable[float]) The starting transform.
        :param end: (Iterable[float]) The ending transform.
        :param duration: (float) The duration of the keyframe.
        :param effectors: (Union[List[str], str])
            The effector(s) targeted by the keyframe. Overrides
            the default effectors for this sequence.
        :param frame: (int) The spatial frame. Overrides the
            default frame for this sequence.
        :param axis_mask: (int) The axis mask to use for this
            keyframe. Overrides the default axis mask defined for
            this sequence.
        :return: True if the new keyframe was added successfully;
            otherwise False.
        """
        # not really points, but format for transform is the same,
        # except with 12 elements
        start = to_point(start, 12)
        end = to_point(end, 12)

        if not effectors:
            effectors = self.effectors

        if not frame:
            frame = self.frame

        if not axis_mask:
            axis_mask = self.axis_mask

        keyframe = KeyFrame(start, end, duration, effectors, frame,
                            axis_mask, const.KFTYPE_ABSOLUTE_TRANSFORM)

        if not keyframe.is_complete():
            return False

        self._keyframes.append(keyframe)
        return True

    def next_transform_keyframe(self, end, duration, effectors=None,
                                frame=None, axis_mask=None):
        """
        Adds a new keyframe to the sequence which uses the ending position
        of the previous keyframe as the starting position and moves to the
        specified end transform.

        :param end: (Iterable[float]) The ending transform.
        :param duration: (float) The duration of the keyframe.
        :param effectors: (Union[List[str], str])
            The effector(s) targeted by the keyframe. Overrides
            the default effectors for this sequence.
        :param frame: (int) The spatial frame. Overrides the
            default frame for this sequence.
        :param axis_mask: (int) The axis mask to use for this
            keyframe. Overrides the default axis mask defined for
            this sequence.
        :return: True if the new keyframe was added successfully;
            otherwise False.
        """
        return self.new_transform_keyframe(
            None, end, duration, effectors, frame, axis_mask)

    def add_keyframe(self, keyframe):
        if self.check_keyframe(keyframe):
            self._keyframes.append(keyframe)
            return True
        return False

    def get_keyframes(self):
        return list(self._keyframes)

    @staticmethod
    def check_keyframe(keyframe):
        if not keyframe.is_complete():
            return False
        elif keyframe.kftype == const.KFTYPE_ABSOLUTE_POSITION:
            return (keyframe.start or len(keyframe.start) == 6) \
                and len(keyframe.end) == 6
        elif keyframe.kftype == const.KFTYPE_ABSOLUTE_TRANSFORM:
            return (keyframe.start or len(keyframe.start) == 12) \
                and len(keyframe.end) == 12
        else:
            return False


class PlanarSequence(MotionSequence):

    def __init__(self, effectors, axis_mask=const.AXIS_MASK_VEL):
        """
        Initializes a new planar sequence instance.

        :param effectors: (Union[str, Iterable[str])
            The default effector(s) targeted by this sequence.
            Either the string identifier for a single effector
            or a list of effector identifiers.
        :param axis_mask: (int) The default axis mask for
            this sequence.
        """
        self.effectors = effectors
        self.axis_mask = axis_mask
        self._keyframes = []

    def new_keyframe(self, start, end, duration, effectors=None, axis_mask=None):
        """
        Adds a new keyframe between the provided starting and ending
        positions with the specified duration.

        :param start: (Iterable[float]) The starting position.
        :param end: (Iterable[float]) The ending position.
        :param duration: (float) The duration of the frame.
        :param effectors: (Union[List[str], str])
            The effector(s) targeted by the keyframe. Overrides
            the default effectors defined for this planar sequence.
        :param axis_mask: (int) The axis mask to use for this
            keyframe. Overrides the default axis mask defined for
            this planar sequence.
        :return: True if the new keyframe was added successfully;
            otherwise False.
        """
        start = to_point(start, 2)
        end = to_point(end, 2)

        if not effectors:
            effectors = self.effectors

        if not axis_mask:
            axis_mask = self.axis_mask

        keyframe = KeyFrame(start, end, duration, effectors, None,
                            axis_mask, const.KFTYPE_PLANAR)

        if not keyframe.is_complete():
            return False

        self._keyframes.append(keyframe)
        return True

    def next_keyframe(self, end, duration, effectors=None, axis_mask=None):

        return self.new_keyframe(None, end, duration, effectors, axis_mask)

    def add_keyframe(self, keyframe):
        if self.check_keyframe(keyframe):
            self._keyframes.append(keyframe)
            return True
        return False

    def get_keyframes(self):
        return list(self._keyframes)

    @staticmethod
    def check_keyframe(keyframe):
        if not keyframe.is_complete():
            return False
        elif keyframe.kftype == const.KFTYPE_PLANAR:
            return False
        elif keyframe.start and len(keyframe.start) != 2:
            return False
        elif len(keyframe.end) != 2:
            return False
        else:
            return True
