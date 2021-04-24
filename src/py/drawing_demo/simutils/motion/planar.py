__version__ = "0.0.0"
__author__ = 'ancient-sentinel'

import constants as const
from models import KeyFrame, Plane
from utils import to_point
from _context import *
from _handler import *
from _sequence import *


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
        """
        Adds a new keyframe to the sequence which uses the ending position
        of the previous keyframe as the starting position and moves to the
        specified end position.

        :param end: (Iterable[float]) The ending transform.
        :param duration: (float) The duration of the keyframe.
        :param effectors: (Union[List[str], str])
            The effector(s) targeted by the keyframe. Overrides
            the default effectors for this sequence.
        :param axis_mask: (int) The axis mask to use for this
            keyframe. Overrides the default axis mask defined for
            this sequence.
        :return: True if the new keyframe was added successfully;
            otherwise False.
        """
        return self.new_keyframe(None, end, duration, effectors, axis_mask)

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
        Checks whether the keyframe is valid for a planar sequence.

        :param keyframe: (models.KeyFrame) The keyframe.
        :return: True if the keyframe is valid; otherwise, False.
        """
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


class PlanarSequenceContext(MotionSequenceContext):
    """The context for a motion sequence in a plane in 3-space."""

    def __init__(self, session, name, plane, frame=const.FRAME_ROBOT,
                 initial_pose=const.POSE_STAND_INIT, extensive_validation=False):
        """
        Initializes a new planar sequence context instance.

        :param session: (qi.Session) The qi session.
        :param name: (str) The name of the context.
        :param plane: (models.Plane) The plane.
        :param frame: (int) The spatial frame.
            Allowed values:
            FRAME_TORSO = 0,
            FRAME_WORLD = 1,
            FRAME_ROBOT = 2.
        :param initial_pose: (Union[str, Callable]) Either
            the string identifier for a predefined pose or
            a function to set the initial position.
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

        if not isinstance(plane, Plane):
            raise ValueError('Expected a Plane, but got a {0}.'.format(type(plane)))

        if not PlanarSequenceContext.valid_point_3d(plane.point):
            raise ValueError('Invalid 3D point.')

        if not PlanarSequenceContext.valid_normal_3d(plane.normal):
            raise ValueError('Invalid 3D normal.')

        if frame not in const.FRAMES:
            raise ValueError('Invalid frame identifier.')

        self._session = session
        self._name = name
        self._service = None
        self._frame = frame
        self._bounds = None
        self._plane = plane
        self._extensive_validation = extensive_validation

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

    def check_sequence(self, sequence, extensive=False):
        """
        Checks that the sequence is valid.

        :param sequence: (PlanarSequence)
            The motion sequence.
        :param extensive: (bool) A flag indicating
            whether to recheck each key frame in the
            sequence for validity.
        :return: True if the sequence is valid;
            otherwise, False.
        """
        if not isinstance(sequence, PlanarSequence):
            return False
        if extensive:
            return all(PlanarSequence.check_keyframe(kf)
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
        return self._bounds

    def get_frame(self):
        """
        Gets the context frame.

        * FRAME_TORSO = 0
        * FRAME_WORLD = 1
        * FRAME_ROBOT = 2
        """
        return self._frame

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

    def get_name(self):
        """Gets the name of the context."""
        return self._name

    def get_plane(self):
        """Gets the plane where the motion sequence is supposed take place."""
        return self._plane

    def set_bounds(self, bounds):
        """
        Sets the bounds for this context.

        Formats:
            Rectangular:
                [[x, y], [x', y']] - Where (x, y) is the bottom left
                corner of the rectangular region, and (x', y') is the
                top right corner.

                --or--

                [x_min, x_max, y_min, y_max]
        :param bounds: (Union[Iterable[float], Iterable[Iterable[float]]])
            The bounds of the planar region.
        :return: True if bounds were set successfully; otherwise, False.
        """
        if len(bounds) == 2:
            p1 = to_point(bounds[0], 2)
            p2 = to_point(bounds[1], 2)
            if p1 and p2:
                bounds = (p1[0], p1[1], p2[0], p2[1])
        elif len(bounds) != 4:
            return False

        if bounds[0] < bounds[1] and bounds[2] < bounds[3]:
            self._bounds = bounds
            return True
        return False

    def get_ctype(self):
        """Gets the context type."""
        return const.CTYPE_PLANAR

    @staticmethod
    def create_XYPlanarContext(name, session, z_pos=0, frame=const.FRAME_ROBOT,
                               initial_pose=const.POSE_STAND_INIT, extensive_validation=False):
        """
        Creates a planar sequence context for a plane running parallel
        to the xy-plane at the specified position, `z_pos`, along the z-axis.
        The plane's normal vector points in the direction of the positive
        z-axis.

        :param name: (str) The name of the sequence context.
        :param session: (qi.Session) The qi session.
        :param z_pos: (float) The position of the plane along the z-axis.
        :param frame: (int) The spatial frame.
            Allowed values:
            FRAME_TORSO = 0,
            FRAME_WORLD = 1,
            FRAME_ROBOT = 2.
        :param initial_pose: (Union[str, Callable]) Either
            the string identifier for a predefined pose or
            a function to set the initial position.
        :param extensive_validation: (bool) A flag
            indicating whether this context should perform
            extensive validation before sending sequences
            to the motion service.
        :return: The sequence context for the specified plane.
        """
        plane = Plane([0, 0, z_pos], [0, 0, 1])
        context = PlanarSequenceContext(session, name, plane, frame,
                                        initial_pose, extensive_validation)
        return context

    @staticmethod
    def create_YZPlanarContext(name, session, x_pos=0, frame=const.FRAME_ROBOT,
                               initial_pose=const.POSE_STAND_INIT, extensive_validation=False):
        """
        Creates a planar sequence context for a plane running parallel
        to the yz-plane at the specified position, `x_pos`, along the x-axis.
        The plane's normal vector points in the direction of the positive
        x-axis.

        :param name: (str) The name of the sequence context.
        :param session: (qi.Session) The qi session.
        :param x_pos: (float) The position of the plane along the x-axis.
        :param frame: (int) The spatial frame.
            Allowed values:
            FRAME_TORSO = 0,
            FRAME_WORLD = 1,
            FRAME_ROBOT = 2.
        :param initial_pose: (Union[str, Callable]) Either
            the string identifier for a predefined pose or
            a function to set the initial position.
        :param extensive_validation: (bool) A flag
            indicating whether this context should perform
            extensive validation before sending sequences
            to the motion service.
        :return: The sequence context for the specified plane.
        """
        plane = Plane([x_pos, 0, 0], [1, 0, 0])
        context = PlanarSequenceContext(session, name, plane, frame,
                                        initial_pose, extensive_validation)
        return context

    @staticmethod
    def create_XZPlanarContext(name, session, y_pos=0, frame=const.FRAME_ROBOT,
                               initial_pose=const.POSE_STAND_INIT, extensive_validation=False):
        """
        Creates a planar sequence context for a plane running parallel
        to the xz-plane at the specified position, `y_pos`, along the y-axis.
        The plane's normal vector points in the direction of the positive
        y-axis.

        :param name: (str) The name of the sequence context.
        :param session: (qi.Session) The qi session.
        :param y_pos: (float) The position of the plane along the y-axis.
        :param frame: (int) The spatial frame.
            Allowed values:
            FRAME_TORSO = 0,
            FRAME_WORLD = 1,
            FRAME_ROBOT = 2.
        :param initial_pose: (Union[str, Callable]) Either
            the string identifier for a predefined pose or
            a function to set the initial position.
        :param extensive_validation: (bool) A flag
            indicating whether this context should perform
            extensive validation before sending sequences
            to the motion service.
        :return: The sequence context for the specified plane.
        """
        plane = Plane([0, y_pos, 0], [0, 1, 0])
        context = PlanarSequenceContext(session, name, plane, frame,
                                        initial_pose, extensive_validation)
        return context

    @staticmethod
    def valid_normal_3d(normal):
        """
        Determines whether the provided argument is a valid normal
        vector.

        :param normal: (Iterable[float]) A 3-element iterable containing
            numeric values, not all of which may be equal to 0.
        :return: True if the argument is a valid 3D normal vector;
            otherwise, False.
        """
        return PlanarSequenceContext.valid_point_3d(normal) and \
            not all(x == 0 for x in normal)

    @staticmethod
    def valid_point_3d(point):
        """
        Determines whether the provided argument is a valid 3D point.

        :param point: (Union[Iterable[float], int]) A 3-element iterable containing
            numeric values; or, the value 0 to indicate the origin.
        :return: True if the argument is a valid 3D point;
            otherwise, False.
        """
        if point == 0:
            return True
        elif len(point) == 3 and all(isinstance(x, float) for x in point):
            return True
        else:
            return False


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
        :param motion_proxy: (ALMotion)
            The motion service or proxy.
        :param posture_proxy: (ALRobotPosture)
            The posture service or proxy.
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
