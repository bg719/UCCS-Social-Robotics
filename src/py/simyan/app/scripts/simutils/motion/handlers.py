__version__ = "0.0.0"
__author__ = 'ancient-sentinel'

import abc
import constants as const

from models import ExecutionResult


class KeyframeTypeError(ValueError):
    """Invalid keyframe type provided."""

    def __init__(self, kftype):
        """
        Initializes a new keyframe type error.

        :param kftype: (str) The invalid keyframe type.
        """
        self.kftype = kftype


class MotionSequenceHandler:
    """The base class for motion sequence handlers."""
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def handle_seq(self, context, sequence, motion_proxy, posture_proxy):
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
        self.allowed_types = [
            const.KFTYPE_ABSOLUTE_POSITION,
            const.KFTYPE_ABSOLUTE_TRANSFORM
        ]

    def handle_seq(self, context, sequence, motion_proxy, posture_proxy):
        keyframes = sequence.get_keyframes()

        if not keyframes or len(keyframes) == 0:
            return ExecutionResult.error_result('No keyframes in sequence.')

        try:
            invoke_list = [self._new_invocation(keyframes[0], motion_proxy)]
            idx = 0
            last = keyframes[0]
            effectors = set(last.effectors)
            thresholds = context.get_thresholds() or 0.001

            for current in keyframes:
                curr_effectors = set(current.effectors)
                if current.kftype == last.kftype and curr_effectors == effectors:
                    if not current.start or idx == 0:
                        self._append(invoke_list[idx], current)
                    elif self._are_same(current.start, last.end, thresholds):
                        self._append(invoke_list[idx], current)
                    last = current
                    continue
                idx += 1
                invoke_list[idx] = self._new_invocation(current, motion_proxy)
                self._append(invoke_list[idx], current)
                effectors = curr_effectors
        except KeyframeTypeError as e:
            return ExecutionResult.invalid_kftype(e.kftype)
        except Exception as e:
            return ExecutionResult.error_result(
                'Exception while attempting to generate sequence invocations. ' +
                'Message: {0}'.format(e.message))

        set_pose = context.get_or_set_initial_pose()

        if isinstance(set_pose, str):
            posture_proxy.goToPosture(set_pose, 0.5)
        elif not set_pose:
            return ExecutionResult.error_result(
                'Context reported failure to set initial position. ' +
                'Aborting execution of motion sequence.')

        for invocation in invoke_list:
            if invocation[TYPE] == const.KFTYPE_ABSOLUTE_POSITION:
                motion_proxy.positionInterpolations(*invocation[ARGS])
            else:
                motion_proxy.transformInterpolations(*invocation[ARGS])

        return ExecutionResult.success_result()

    def handles_type(self, ctype):
        return ctype == const.CTYPE_ABSOLUTE

    def _get_position_time(self, position, motion_proxy):
        return 3

    def _get_transform_time(self, transform, motion_proxy):
        return 3

    def _new_invocation(self, firstkf, motion_proxy):
        paths, masks, frames, times = [], [], [], []
        if firstkf.start:
            paths.append(firstkf.start)
            frames.append(firstkf.frame)
            masks.append(const.AXIS_MASK_VEL)
            if firstkf.kftype == const.KFTYPE_ABSOLUTE_POSITION:
                move_time = self._get_position_time(firstkf.start, motion_proxy)
                times.append(move_time)
            elif firstkf.kftype == const.KFTYPE_ABSOLUTE_TRANSFORM:
                move_time = self._get_transform_time(firstkf.start, motion_proxy)
                times.append(move_time)
            else:
                raise KeyframeTypeError(firstkf.kftype)
        return firstkf.kftype, (firstkf.effectors, paths, frames, masks, times)

    @staticmethod
    def _append(invocation, keyframe):
        invocation[ARGS][PATHS].append(keyframe.end)
        invocation[ARGS][FRAMES].append(keyframe.frame)
        invocation[ARGS][MASKS].append(keyframe.axis_mask)
        invocation[ARGS][TIMES].append(keyframe.duration)

    @staticmethod
    def _are_same(p1, p2, thresholds=0.001):
        p1_len = len(p1)
        if p1_len != len(p2):
            return False
        if isinstance(thresholds, float):
            thresholds = [thresholds] * len(p1)
        elif isinstance(thresholds, (list, tuple)) and len(thresholds) == 2:
            if p1_len == 6:
                thresholds = thresholds[0]
            elif p1_len == 12:
                thresholds = thresholds[1]
        else:
            thresholds = [0] * p1_len

        for i in range(p1_len):
            try:
                threshold = thresholds[i]
            except IndexError:
                threshold = 0

            if p1[i] - p2[i] > threshold:
                return False
        return True


class PlanarSequenceHandler(MotionSequenceHandler):
    """A handler for planar motion sequences."""

    def __init__(self):
        """Initializes a new planar motion sequence handler instance."""
        pass

    def handle_seq(self, context, sequence, motion_proxy, posture_proxy):
        """
        Handles the execution of the specified planar motion sequence within
        the scope of the provided motion sequence context.

        :param context: (contexts.PlanarMotionSequenceContext)
            The planar motion sequence context.
        :param sequence: (sequences.PlanarSequence)
            The motion sequence.
        :return: (models.ExecutionResult) The result of executing the sequence.
        """
        keyframes = sequence.get_keyframes()

        if not keyframes or len(keyframes) == 0:
            return ExecutionResult.error_result('No keyframes in sequence.')

        frame = context.get_frame()

        if not frame:
            return ExecutionResult.error_result('Planar context must define the frame.')

        bounds = context.get_bounds()

        try:
            invoke_list = []
        except KeyframeTypeError as kerr:
            return ExecutionResult.invalid_kftype(kerr.kftype)

    def handles_type(self, ctype):
        """
        Determines whether this handler can handle the specified
        motion sequence context type.

        :param ctype: (str) The motion sequence context type.
        :return: True if this handler can handle the context type;
            otherwise, False.
        """
        return ctype == const.CTYPE_PLANAR
