__version__ = "0.0.0"
__author__ = 'ancient-sentinel'

import constants as const
from models import KeyFrame
from utils import to_point
from _context import *
from _handler import *
from _sequence import *


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
            return (keyframe.start or len(keyframe.start) == 6) \
                and len(keyframe.end) == 6
        elif keyframe.kftype == const.KFTYPE_ABSOLUTE_TRANSFORM:
            return (keyframe.start or len(keyframe.start) == 12) \
                and len(keyframe.end) == 12
        else:
            return False


class AbsoluteSequenceContext(MotionSequenceContext):

    def __init__(self, session, name, initial_pose=const.POSE_STAND_INIT,
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

        :param session: (qi.Session) The qi session.
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
        if not session:
            raise TypeError('The session cannot be None.')

        if not isinstance(name, str):
            raise TypeError('Invalid type for name.')

        if isinstance(initial_pose, str) and \
                initial_pose in const.PREDEFINED_POSES:
            self._initial_pose = initial_pose
        elif callable(initial_pose):
            self._initial_pose = initial_pose
        else:
            raise TypeError('Invalid initial pose.')

        if isinstance(thresholds, float):
            self._thresholds = [[thresholds] * 6, [thresholds] * 12]
        elif isinstance(thresholds, (list, tuple)):
            position = thresholds[0]
            if isinstance(position, float):
                position = [position] * 6
            elif len(position) != 6:
                raise ValueError('Wrong length vector of positional threshold values.')

            transform = thresholds[1]
            if isinstance(transform, float):
                transform = [transform] * 12
            elif len(transform) != 12:
                raise ValueError('Wrong length vector of transform threshold values.')

            self._thresholds = [position, transform]
        else:
            raise TypeError('Invalid thresholds specifier.')

        self._session = session
        self._name = name
        self._service = None
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

    @property
    def motion_service(self):
        """Gets the motion service."""
        if self._service is None:
            self._service = self.session.service("SIMMotion")
        return self._service

    @property
    def session(self):
        """Gets the qi session for this context."""
        return self._session

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

    def handle_seq(self, context, sequence, motion_proxy, posture_proxy):
        keyframes = sequence.get_keyframes()

        if not keyframes or len(keyframes) == 0:
            return ExecutionResult.error_result('No keyframes in sequence.')

        try:
            invoke_list = [self._new_invocation(keyframes[0], motion_proxy)]
            idx = 0
            last = keyframes[0]
            effectors = set(last.effector)
            thresholds = context.get_thresholds() or 0.001

            for current in keyframes:
                curr_effectors = set(current.effector)
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
        args = new_invocation_args()
        args[EFFECTORS].extend(firstkf.effector)
        if firstkf.start:
            args[PATHS].append(firstkf.start)
            args[FRAMES].append(firstkf.frame)
            args[MASKS].append(const.AXIS_MASK_VEL)
            if firstkf.kftype == const.KFTYPE_ABSOLUTE_POSITION:
                move_time = self._get_position_time(firstkf.start, motion_proxy)
                args[TIMES].append(move_time)
            elif firstkf.kftype == const.KFTYPE_ABSOLUTE_TRANSFORM:
                move_time = self._get_transform_time(firstkf.start, motion_proxy)
                args[TIMES].append(move_time)
            else:
                raise KeyframeTypeError(firstkf.kftype)
        return firstkf.kftype, args

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