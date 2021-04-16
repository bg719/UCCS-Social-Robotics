__version__ = "0.0.0"
__author__ = 'ancient-sentinel'

import abc
import constants as const

from models import ExecutionResult


class MotionSequenceHandler:
    """The base class for motion sequence handlers."""
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def handle_seq(self, context, sequence, motion_proxy):
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
        :return: (models.ExecutionResult) The result of executing the sequence.
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


TYPE = 0
ARGS = 1
FRAMES = 1
PATHS = 2
MASKS = 3
TIMES = 4


class AbsoluteSequenceHandler(MotionSequenceHandler):
    """A handler for absolute motion sequences."""

    def __init__(self):
        """Initializes a new absolute motion sequence handler instance."""
        pass

    def handle_seq(self, context, sequence, motion_proxy):
        keyframes = sequence.get_keyframes()

        if not keyframes or \
                keyframes[0].kftype not in \
                {const.KFTYPE_ABSOLUTE_POSITION,
                 const.KFTYPE_ABSOLUTE_TRANSFORM}:
            return ExecutionResult.invalid_kftype(keyframes[0].kftype)

        last_type = keyframes[0].kftype
        invoke_list = [self._new_invocation(last_type, keyframes[0], motion_proxy)]
        idx = 0
        effectors = keyframes[0].effectors

        for i in range(len(keyframes)):
            current = keyframes[i]
            if current.kftype == last_type and current.effectors == effectors:
                if not current.start or idx == 0:
                    self._append(invoke_list[idx], current)
                    continue
            idx += 1
            invoke_list[idx] = self._new_invocation(current.kftype,
                                                    current, motion_proxy)
            self._append(invoke_list[idx], current)

        for invocation in invoke_list:
            if invocation[TYPE] == const.KFTYPE_ABSOLUTE_POSITION:
                motion_proxy.positionInterpolations(*invocation[ARGS])
            else:
                motion_proxy.transformInterpolations(*invocation[ARGS])

    def _get_position_time(self, position, motion_proxy):
        return 3

    def _get_transform_time(self, transform, motion_proxy):
        return 3

    def _new_invocation(self, kftype, firstkf, motion_proxy):
        paths = []
        frames = []
        masks = []
        times = []
        if firstkf.start:
            paths.append(firstkf.start)
            frames.append(firstkf.frame)
            masks.append(const.AXIS_MASK_VEL) # todo: confirm that this is correct
            if kftype == const.KFTYPE_ABSOLUTE_POSITION:
                move_time = self._get_position_time(firstkf.start, motion_proxy)
                times.append(move_time)
            else:
                move_time = self._get_transform_time(firstkf.start, motion_proxy)
                times.append(move_time)
        return kftype, (firstkf.effectors, paths, frames, masks, times)

    @staticmethod
    def _append(invocation, keyframe):
        invocation[ARGS][PATHS].append(keyframe.end)
        invocation[ARGS][FRAMES].append(keyframe.frame)
        invocation[ARGS][MASKS].append(keyframe.axis_mask)
        invocation[ARGS][TIMES].append(keyframe.duration)


class PlanarSequenceHandler(MotionSequenceHandler):
    """A handler for planar motion sequences."""

    def __init__(self):
        """Initializes a new planar motion sequence handler instance."""
        pass

    def handle_seq(self, context, sequence, motion_proxy):
        """
        Handles the execution of the specified planar motion sequence within
        the scope of the provided motion sequence context.

        :param context: (contexts.PlanarMotionSequenceContext)
            The planar motion sequence context.
        :param sequence: (sequences.PlanarSequence)
            The motion sequence.
        :return: (models.ExecutionResult) The result of executing the sequence.
        """
        pass

    def handles_type(self, ctype):
        """
        Determines whether this handler can handle the specified
        motion sequence context type.

        :param ctype: (str) The motion sequence context type.
        :return: True if this handler can handle the context type;
            otherwise, False.
        """
        return ctype == const.CTYPE_PLANAR
