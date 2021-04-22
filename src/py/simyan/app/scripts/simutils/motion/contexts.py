__version__ = "0.0.0"
__author__ = 'ancient-sentinel'

import abc
import constants as const

from models import Plane, to_point
from sequences import AbsoluteSequence, PlanarSequence


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

    def execute_seq(self, sequence):
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
        return const.CTYPE_NONE

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

        :param sequence: (sequence.AbsoluteSequence)
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
            self._service = self.session.service("SIMMotorControl")
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
            self._service = self.session.service("SIMMotorControl")
        return self._service

    @property
    def session(self):
        """Gets the qi session for this context."""
        return self._session

    def check_sequence(self, sequence, extensive=False):
        """
        Checks that the sequence is valid.

        :param sequence: (sequence.AbsoluteSequence)
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
