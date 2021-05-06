__version__ = "0.0.0"
__author__ = 'ancient-sentinel'

import constants as const
from models import KeyFrame
from utils import to_point
from _context import *
from _handler import *
from _sequence import *


class AbsoluteSequence(MotionSequence):

    def __init__(self, effector, frame, axis_mask):
        """
        Initializes a new absolute motion sequence instance.

        :param effector: (str) The default effector targeted
            by this sequence.
        :param frame: (int) The default spatial frame.
        :param axis_mask: (int) The default axis mask for
            this sequence.
        """
        self.effector = effector
        self.frame = frame
        self.axis_mask = axis_mask
        self._keyframes = []

    def new_position_keyframe(self, start, end, duration, effector=None,
                              frame=None, axis_mask=None, with_previous=False):
        """
        Adds a new keyframe between the provided starting and ending
        absolute positions with the specified duration.

        :param start: (Iterable[float]) The starting position.
        :param end: (Iterable[float]) The ending position.
        :param duration: (float) The duration of the keyframe.
        :param effector: (str) The effector targeted by the
            keyframe. Overrides the default effector defined
            for this motion sequence.
        :param frame: (int) The spatial frame. Overrides the
            default frame for this sequence.
        :param axis_mask: (int) The axis mask to use for this
            keyframe. Overrides the default axis mask defined for
            this sequence.
        :param with_previous: (bool) If True, the motion defined
            by the keyframe will be executed 1) simultaneously with
            the previous motion if the previous motion was for a
            different effector, or 2) after the previous motion if
            if was for the same effector.
        :return: True if the new keyframe was added successfully;
            otherwise False.
        """
        start = to_point(start, 6)
        end = to_point(end, 6)

        if not effector:
            effector = self.effector

        if not frame:
            frame = self.frame

        if not axis_mask:
            axis_mask = self.axis_mask

        keyframe = KeyFrame(start, end, duration, effector, frame, axis_mask,
                            const.KFTYPE_ABSOLUTE_POSITION, with_previous)

        if not keyframe.is_complete():
            return False

        self._keyframes.append(keyframe)
        return True

    def next_position_keyframe(self, end, duration, effector=None,
                               frame=None, axis_mask=None, with_previous=True):
        """
        Adds a new keyframe to the sequence which uses the ending position
        of the previous keyframe as the starting position and moves to the
        specified end position.

        :param end: (Iterable[float]) The ending position.
        :param duration: (float) The duration of the keyframe.
        :param effector: (Union[List[str], str])
            The effector(s) targeted by the keyframe. Overrides
            the default effectors for this sequence.
        :param frame: (int) The spatial frame. Overrides the
            default frame for this sequence.
        :param axis_mask: (int) The axis mask to use for this
            keyframe. Overrides the default axis mask defined for
            this sequence.
        :param with_previous: (bool) If True, the motion defined
            by the keyframe will be executed 1) simultaneously with
            the previous motion if the previous motion was for a
            different effector, or 2) after the previous motion if
            if was for the same effector.
        :return: True if the new keyframe was added successfully;
            otherwise False.
        """
        return self.new_position_keyframe(None, end, duration, effector,
                                          frame, axis_mask, with_previous)

    def new_transform_keyframe(self, start, end, duration, effector=None,
                               frame=None, axis_mask=None, with_previous=False):
        """
        Adds a new keyframe between the provided starting and ending
        absolute transforms with the specified duration.

        :param start: (Iterable[float]) The starting transform.
        :param end: (Iterable[float]) The ending transform.
        :param duration: (float) The duration of the keyframe.
        :param effector: (Union[List[str], str])
            The effector targeted by the keyframe. Overrides
            the default effectors for this sequence.
        :param frame: (int) The spatial frame. Overrides the
            default frame for this sequence.
        :param axis_mask: (int) The axis mask to use for this
            keyframe. Overrides the default axis mask defined for
            this sequence.
        :param with_previous: (bool) If True, the motion defined
            by the keyframe will be executed 1) simultaneously with
            the previous motion if the previous motion was for a
            different effector, or 2) after the previous motion if
            if was for the same effector.
        :return: True if the new keyframe was added successfully;
            otherwise False.
        """
        # not really points, but format for transform is the same,
        # except with 12 elements
        start = to_point(start, 12)
        end = to_point(end, 12)

        if not effector:
            effector = self.effector

        if not frame:
            frame = self.frame

        if not axis_mask:
            axis_mask = self.axis_mask

        keyframe = KeyFrame(start, end, duration, effector, frame,
                            axis_mask, const.KFTYPE_ABSOLUTE_TRANSFORM, with_previous)

        if not keyframe.is_complete():
            return False

        self._keyframes.append(keyframe)
        return True

    def next_transform_keyframe(self, end, duration, effector=None,
                                frame=None, axis_mask=None, with_previous=True):
        """
        Adds a new keyframe to the sequence which uses the ending position
        of the previous keyframe as the starting position and moves to the
        specified end transform.

        :param end: (Iterable[float]) The ending transform.
        :param duration: (float) The duration of the keyframe.
        :param effector: (Union[List[str], str])
            The effector targeted by the keyframe. Overrides
            the default effector for this sequence.
        :param frame: (int) The spatial frame. Overrides the
            default frame for this sequence.
        :param axis_mask: (int) The axis mask to use for this
            keyframe. Overrides the default axis mask defined for
            this sequence.
        :param with_previous: (bool) If True, the motion defined
            by the keyframe will be executed 1) simultaneously with
            the previous motion if the previous motion was for a
            different effector, or 2) after the previous motion if
            if was for the same effector.
        :return: True if the new keyframe was added successfully;
            otherwise False.
        """
        return self.new_transform_keyframe(
            None, end, duration, effector, frame, axis_mask, with_previous)

    def add_keyframe(self, keyframe):
        """
        Appends the keyframe to the sequence.

        :param keyframe: (models.KeyFrame) The keyframe.
        :return: True if the keyframe was added successfully;
            otherwise, False.
        """
        if self.check_keyframe(keyframe):
            self._keyframes.append(keyframe)
            return True
        return False

    def get_keyframes(self):
        """
        Gets the list of keyframes which define the motion sequence.

        :return: (List[models.KeyFrame]) The list of keyframes.
        """
        return list(self._keyframes)

    @staticmethod
    def check_keyframe(keyframe):
        """
        Checks whether the keyframe is valid for an absolute sequence.

        :param keyframe: (models.KeyFrame) The keyframe.
        :return: True if the keyframe is valid; otherwise, False.
        """
        if not keyframe.is_complete():
            return False
        elif keyframe.kftype == const.KFTYPE_ABSOLUTE_POSITION:
            ok_start = True
            if keyframe.start is not None:
                ok_start = len(keyframe.start) == 6
            return ok_start and len(keyframe.end) == 6
        elif keyframe.kftype == const.KFTYPE_ABSOLUTE_TRANSFORM:
            ok_start = True
            if keyframe.start is not None:
                ok_start = len(keyframe.start) == 12
            return ok_start and len(keyframe.end) == 12
        else:
            return False


class AbsoluteSequenceContext(MotionSequenceContext):

    def __init__(self, name, initial_pose=const.POSE_STAND_INIT,
                 thresholds=0.001, extensive_validation=True):
        """
        Initializes a new absolute sequence context instance.

        Threshold formats:
            * float: A single value for comparisons at all indices
                for both position and transform vectors.
            * [float, float]: The first value will be used for all
                comparison of all indices on position vectors, and
                the second for comparison of all indices on transformation
                vectors.
            * [Union[float, Iterable[float]], Union[float, Iterable[float]]]:
                The first value of list of values will be used
                position vector comparisons, and the second will be
                used for transformation vector comparisons.
            Examples:
                - 0.001
                - (0.001, 0.00001)
                - [[0.1, 0.2, 0.3, 0.01, 0.02, 0.03],
                    [0.1, 0.1, 0.2, 0.2, 0.1, 0.1, 0.1, 0.2, 0.1]]
                - [[0.1, 0.2, 0.3, 0.01, 0.02, 0.03], 0.001]
            Note:
                - Position vectors have 6 elements
                - Transform vectors have 12 elements

        :param name: (str) The name of the context.
        :param initial_pose: (Union[str, Callable]) Either
            the string identifier for a predefined pose or
            a function to set the initial position.
        :param thresholds: (Union[float, Iterable[float, Iterable[float]]])
            The threshold(s) for testing positional/transformational
            equality. Either a single value to be used for all
            comparisons or a 2 element list of thresholds to be
            applied to corresponding indices for positional and
            transformational vectors, respectively.
        :param extensive_validation: (bool) A flag
            indicating whether this context should perform
            extensive validation before sending sequences
            to the motion service.
        """
        # validate name
        if not isinstance(name, str):
            raise TypeError('Invalid type for name.')

        # validate initial pose
        if isinstance(initial_pose, str) and \
                initial_pose in const.PREDEFINED_POSES:
            self._initial_pose = initial_pose
        elif callable(initial_pose):
            self._initial_pose = initial_pose
        else:
            raise TypeError('Invalid initial pose.')

        # validate threshold
        if isinstance(thresholds, float):
            self._thresholds = [[thresholds] * 6, [thresholds] * 12]
        elif isinstance(thresholds, (list, tuple)):
            # check position threshold
            position = thresholds[0]
            if isinstance(position, float):
                position = [position] * 6
            elif len(position) != 6:
                raise ValueError('Wrong length vector of positional threshold values.')

            # check transform threshold
            transform = thresholds[1]
            if isinstance(transform, float):
                transform = [transform] * 12
            elif len(transform) != 12:
                raise ValueError('Wrong length vector of transform threshold values.')

            self._thresholds = [position, transform]
        else:
            raise TypeError('Invalid thresholds specifier.')

        self._name = name
        self._extensive_validation = extensive_validation

    def check_sequence(self, sequence, extensive=False):
        """
        Checks that the sequence is valid.

        :param sequence: (AbsoluteSequence)
            The motion sequence.
        :param extensive: (bool) A flag indicating
            whether to recheck each key frame in the
            sequence for validity.
        :return: True if the sequence is valid;
            otherwise, False.
        """
        if not isinstance(sequence, AbsoluteSequence):
            return False
        if extensive:
            return all(AbsoluteSequence.check_keyframe(kf)
                       for kf in sequence.get_keyframes())
        return True

    def extensive_validation(self):
        """Indicates whether extensive validation will be performed
         before sequences are sent to the motion service."""
        return self._extensive_validation

    def get_bounds(self):
        """"
        Gets the bounds on the region where the motion sequence
        is to take place.

        :return: The bounds or None if the context's region
            is unbounded.
        """
        return None

    def get_ctype(self):
        """Gets the context type."""
        return const.CTYPE_ABSOLUTE

    def get_name(self):
        """Gets the name of the context."""
        return self._name

    def get_or_set_initial_pose(self):
        """
        Either returns the string identifier for a named pose,
        or attempts to set the initial position.

        :return: (Union[str, bool]) The pose identifier; or, True
            if the initial position was set successfully, False if
            setting the initial position failed.
        """
        if callable(self._initial_pose):
            try:
                self._initial_pose()
                return True
            except:
                return False
        else:
            return self._initial_pose

    def get_thresholds(self):
        """Returns the comparison threshold(s) for this context."""
        return self._thresholds


class AbsoluteSequenceHandler(MotionSequenceHandler):
    """A handler for absolute motion sequences."""

    def __init__(self):
        """Initializes a new absolute motion sequence handler instance."""
        self.allowed_types = [
            const.KFTYPE_ABSOLUTE_POSITION,
            const.KFTYPE_ABSOLUTE_TRANSFORM
        ]

    def handle_sequence(self, sequence, context, motion_proxy, posture_proxy):
        """
        Handles the execution of the specified motion `sequence` within the
        scope of the provided motion sequence `context`.

        :param sequence: (AbsoluteSequence)
            The absolute motion sequence.
        :param context: (AbsoluteSequenceContext)
            The absolute motion sequence context.
        :param motion_proxy: (ALMotion)
            The motion service or proxy.
        :param posture_proxy: (ALRobotPosture)
            The posture service or proxy.
        :return: (models.ExecutionResult)
            The result of executing the sequence.
        """
        keyframes = sequence.get_keyframes()

        if not keyframes or len(keyframes) == 0:
            return ExecutionResult.error_result('No keyframes in sequence.')

        # construct ALMotion invocations
        try:
            invoke_list = [self._new_invocation(keyframes[0], motion_proxy)]
            idx = 0
            last = keyframes[0]
            # thresholds = context.get_thresholds() or 0.001

            for current in keyframes:
                if current.with_previous and (current.start is None or idx == 0):
                    self._append(invoke_list[idx], current, last)
                else:
                    idx += 1
                    invoke_list.append(self._new_invocation(current, motion_proxy))
                    self._append(invoke_list[idx], current, last)
                last = current
        except KeyframeException as e:
            return ExecutionResult.keyframe_exception(e)
        except KeyframeTypeError as e:
            return ExecutionResult.invalid_kftype(e.kftype)
        except Exception as e:
            return ExecutionResult.error_result(
                'Exception while attempting to generate sequence invocations. ' +
                'Message: {0}'.format(e.message))

        # set initial pose
        try:
            set_pose = context.get_or_set_initial_pose()

            if isinstance(set_pose, str):
                success = posture_proxy.goToPosture(set_pose, 0.5)
                if not success:
                    return ExecutionResult.error_result(
                        'ALRobotPosture reported failure to go to posture: {0}'.format(set_pose))
            elif not set_pose:
                return ExecutionResult.error_result(
                    'Context reported failure to set initial position. ' +
                    'Aborting execution of motion sequence.')
        except Exception as e:
            return ExecutionResult.error_result(
                'Exception while attempting to set initial position.' +
                'Aborting execution of motion sequence.')

        # execute motion sequence
        for invocation in invoke_list:
            if invocation[TYPE] == const.KFTYPE_ABSOLUTE_POSITION:
                motion_proxy.positionInterpolations(*invocation[ARGS])
            else:
                motion_proxy.transformInterpolations(*invocation[ARGS])

        return ExecutionResult.success_result()

    def handles_type(self, ctype):
        """
        Determines whether this handler can handle the specified
        motion sequence context type.

        :param ctype: (str) The motion sequence context type.
        :return: True if this handler can handle the context type;
            otherwise, False.
        """
        return ctype == const.CTYPE_ABSOLUTE

    def _get_position_time(self, position, motion_proxy):
        """
        Gets the time needed to move to the specified position.

        :param position: (List[float]) The position.
        :param motion_proxy: (ALMotion) The motion proxy or service.
        :return: The time needed to move to the specified position.
        """
        # for now, just return a constant; but, in general
        # this could be more dynamic based on the current position
        # of the robot (obtained from the motion_proxy) and the
        # distance to the desired position
        return 3

    def _get_transform_time(self, transform, motion_proxy):
        """
        Gets the time needed to move to the specified transform.

        :param transform: (List[float]) The transform.
        :param motion_proxy: (ALMotion) The motion proxy or service.
        :return: The time needed to move to the specified transform.
        """
        # for now, just return a constant; but, in general
        # this could be more dynamic based on the current transforms
        # for the robot (obtained from the motion_proxy) and the
        # distance to the desired transforms
        return 3

    def _new_invocation(self, keyframe, motion_proxy):
        """
        Generates a new set of invocation arguments for the
        ALMotion.positionInterpolations(...) methods based on the
        provided initial keyframe.

        :param keyframe: (models.KeyFrame) The initial keyframe for
            the invocation.
        :param motion_proxy: (ALMotion) The motion proxy or service.
        :return: The set of invocation arguments.
        """
        args = new_invocation_args()
        args[EFFECTORS].append(keyframe.effector)
        args[FRAMES].append(keyframe.frame)
        args[MASKS].append(const.AXIS_MASK_VEL)

        # if the keyframe has a defined start, we need to make it the
        # initial argument in the path list and determine a time to
        # move to it
        if keyframe.start:
            args[PATHS].append([keyframe.start])
            if keyframe.kftype == const.KFTYPE_ABSOLUTE_POSITION:
                move_time = self._get_position_time(keyframe.start, motion_proxy)
                args[TIMES].append([move_time])
            elif keyframe.kftype == const.KFTYPE_ABSOLUTE_TRANSFORM:
                move_time = self._get_transform_time(keyframe.start, motion_proxy)
                args[TIMES].append([move_time])
            else:
                raise KeyframeTypeError(keyframe.kftype)
        else:
            args[PATHS].append([])
            args[TIMES].append([])
        return keyframe.kftype, args

    @staticmethod
    def _append(invocation, current, previous):
        """
        Appends the current keyframe to the invocation arguments.

        :param invocation: The invocation arguments.
        :param current: (models.KeyFrame) The current keyframe to be appended.
        :param previous: (models.KeyFrame) The previous keyframe.
        """
        # we can't mix position and transform keyframes
        if current.kftype != previous.kftype:
            raise KeyframeException.type_mismatch(current, previous)

        # if the same effector is specified, simply add to
        # it's path and time lists (frame and axis mask discrepancies are
        # currently ignored)
        if current.effector == previous.effector:
            # add the current position to the path list for the effector
            invocation[ARGS][PATHS][-1].append(current.end)
            # add the relative time to move to the position
            times = invocation[ARGS][TIMES][-1]
            if len(times) > 0:
                times.append(current.duration + times[-1])
            else:
                times.append(current.duration)

        # if we already have the effector declared, find the index
        # of it's lists and add the current position and time
        elif current.effector in invocation[ARGS][EFFECTORS]:
            idx = invocation[ARGS][EFFECTORS].index(current.effector)
            invocation[ARGS][PATHS][idx].append(current.end)
            times = invocation[ARGS][TIMES][idx]
            times.append(current.duration + times[-1])

        # otherwise, we add the new effector to the invocation
        else:
            invocation[ARGS][EFFECTORS].append(current.effector)
            invocation[ARGS][PATHS].append([current.end])
            invocation[ARGS][FRAMES].append(current.frame)
            invocation[ARGS][MASKS].append(current.axis_mask)
            invocation[ARGS][TIMES].append([current.duration])


if __name__ == '__main__':
    seq = AbsoluteSequence(const.EF_LEFT_ARM, const.FRAME_ROBOT, const.AXIS_MASK_VEL)
    points = [
        [0.15457427501678467, 0.131572425365448, 0.5019456148147583,
            -1.5897225141525269, -0.935154914855957, 0.20292489230632782],
        [0.15036171674728394, 0.10574427992105484, 0.5386977791786194,
            -1.668771505355835, -1.0586074590682983, 0.09279955923557281],
        [0.16299599409103394, 0.0846848413348198, 0.5012325048446655,
            -1.6748456954956055, -0.8622304797172546, -0.027583902701735497],
        [0.15538376569747925, 0.13587330281734467, 0.5069384574890137,
            -1.7119406461715698, -0.9142926931381226, 0.27707982063293457]
    ]

    for p in points:
        seq.next_position_keyframe(p, 3)

    seq.next_position_keyframe(points[0], 3, with_previous=False)
    seq.next_position_keyframe(points[1], 5, const.EF_RIGHT_ARM,
                               const.FRAME_WORLD, const.AXIS_MASK_ALL)

    handler = AbsoluteSequenceHandler()

    handler.handle_sequence(seq, None, None, None)
