__version__ = "0.0.0"
__author__ = 'ancient-sentinel'

import abc
import qi
import constants as const

from constants import FRAME_TORSO, FRAME_ROBOT, FRAME_WORLD
from models import Plane, to_point


class MotionSequenceContext(qi.Object):
    """The context for a motion sequence."""

    __metaclass__ = abc.ABCMeta

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
        return self.motion_service.executeSequence(self.get_name(), sequence)

    @abc.abstractmethod
    def get_frame(self):
        """
        Gets the context frame.

        * FRAME_TORSO = 0
        * FRAME_WORLD = 1
        * FRAME_ROBOT = 2
        """
        return None

    @abc.abstractproperty
    def motion_service(self):
        """Gets the motion service."""
        return None

    @abc.abstractmethod
    def get_name(self):
        """Gets the context name."""
        return None

    @abc.abstractproperty
    def session(self):
        """Gets the qi session for this context."""
        return None

    @abc.abstractmethod
    def get_ctype(self):
        """Gets the context type."""
        return const.CTYPE_NONE

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


class PlanarSequenceContext(MotionSequenceContext):
    """The context for a motion sequence in a get_plane in 3-space."""

    def __init__(self, session, name, plane):
        """
        Initializes a new planar sequence context instance.

        :param session: (qi.Session) The qi session.
        :param name: (str) The get_name of the context.
        :param plane: (models.Plane) The get_plane.
        """
        self._session = session
        self._name = name
        self._service = None
        self._frame = FRAME_TORSO

        if not isinstance(plane, Plane):
            raise ValueError('Expected a Plane, but got a {0}.'.format(type(plane)))

        if not PlanarSequenceContext.valid_point_3d(plane.point):
            raise ValueError('Invalid 3D point.')

        if not PlanarSequenceContext.valid_normal_3d(plane.normal):
            raise ValueError('Invalid 3D normal.')

        self._plane = plane

    def get_frame(self):
        """
        Gets the context frame.

        * FRAME_TORSO = 0
        * FRAME_WORLD = 1
        * FRAME_ROBOT = 2
        """
        return self._frame

    @property
    def motion_service(self):
        """Gets the motion service."""
        if self._service is None:
            self._service = self.session.service("SIMMotorControl")
        return self._service

    def get_name(self):
        """Gets the get_name of the context."""
        return self._name

    def get_plane(self):
        """Gets the plane where the motion sequence is supposed take place."""
        return self._plane

    @property
    def session(self):
        """Gets the qi session for this context."""
        return self._session

    def set_frame(self, frame):
        """
        Sets the get_frame for this context.

        * FRAME_TORSO = 0
        * FRAME_WORLD = 1
        * FRAME_ROBOT = 2
        :param frame: The get_frame.
        """
        if frame not in [FRAME_TORSO, FRAME_ROBOT, FRAME_WORLD]:
            raise ValueError("Invalid get_frame identifier.")
        self._frame = frame

    def get_ctype(self):
        """Gets the context type."""
        return const.CTYPE_PLANAR

    @staticmethod
    def create_XYPlanarContext(name, session, z_pos=0):
        """
        Creates a planar sequence context for a get_plane running parallel
        to the xy-get_plane at the specified position, `z_pos`, along the z-axis.
        The get_plane's normal vector points in the direction of the positive
        z-axis.

        :param name: (str) The get_name of the sequence context.
        :param session: (qi.Session) The qi session.
        :param z_pos: (float) The position of the get_plane along the z-axis.
        :return: The sequence context for the specified get_plane.
        """
        plane = Plane([0, 0, z_pos], [0, 0, 1])
        context = PlanarSequenceContext(session, name, plane)
        return context

    @staticmethod
    def create_YZPlanarContext(name, session, x_pos=0):
        """
        Creates a planar sequence context for a get_plane running parallel
        to the yz-get_plane at the specified position, `x_pos`, along the x-axis.
        The get_plane's normal vector points in the direction of the positive
        x-axis.

        :param name: (str) The get_name of the sequence context.
        :param session: (qi.Session) The qi session.
        :param x_pos: (float) The position of the get_plane along the x-axis.
        :return: The sequence context for the specified get_plane.
        """
        plane = Plane([x_pos, 0, 0], [1, 0, 0])
        context = PlanarSequenceContext(session, name, plane)
        return context

    @staticmethod
    def create_XZPlanarContext(name, session, y_pos=0):
        """
        Creates a planar sequence context for a get_plane running parallel
        to the xz-get_plane at the specified position, `y_pos`, along the y-axis.
        The get_plane's normal vector points in the direction of the positive
        y-axis.

        :param name: (str) The get_name of the sequence context.
        :param session: (qi.Session) The qi session.
        :param y_pos: (float) The position of the get_plane along the y-axis.
        :return: The sequence context for the specified get_plane.
        """
        plane = Plane([0, y_pos, 0], [0, 1, 0])
        context = PlanarSequenceContext(session, name, plane)
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
