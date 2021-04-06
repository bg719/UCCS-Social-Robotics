__version__ = "0.0.0"
__author__ = 'ancient-sentinel'

import abc
import numpy as np


class MotionSequenceContext(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractproperty
    def frame(self):
        return None

    @abc.abstractproperty
    def motion_service(self):
        return None

    @abc.abstractproperty
    def name(self):
        return None

    @abc.abstractproperty
    def session(self):
        return None

    @abc.abstractproperty
    def type(self):
        return None

    def register(self):
        if self.motion_service is None:
            return False
        reg = self._create_registration()
        return self.motion_service.registerContext(reg)

    def unregister(self):
        if self.motion_service is None:
            return False
        return self.motion_service.removeContext(self.name)

    @abc.abstractmethod
    def _create_registration(self):
        """
        Creates the registration for the context to be sent to
        the SIMMotorControl service.

        :return: the context registration
        """
        return None


class PlanarSequenceContext(MotionSequenceContext):

    def __init__(self, session, name):
        self._session = session
        self._name = name
        self._service = None
        self._frame = None
        self._plane = {'point': None, 'normal': None}

    @property
    def frame(self):
        return self._frame

    @property
    def motion_service(self):
        if self._service is None:
            self._service = self.session.service("SIMMotorControl")
        return self._service

    @property
    def name(self):
        return self._name

    @property
    def plane(self):
        return self._plane

    @property
    def session(self):
        return self._session

    @property
    def type(self):
        return "planar"

    def set_plane(self, point3d, normal3d):
        if not self._valid_point_3d(point3d):
            raise ValueError('Invalid 3D point.')

        if not self._valid_normal_3d(normal3d):
            raise ValueError('Invalid 3D normal vector.')
        
        self._plane['point'] = point3d
        self._plane['normal'] = normal3d

    def _create_registration(self):
        """
        Creates the registration info for a planar motion sequence
        context to be sent to the SIMMotorControl service.

        :return: the registration info
        """
        # todo
        return None

    def _get_plane(self, points):
        p0 = np.array(points[0])
        p1 = np.array(points[1])
        p2 = np.array(points[2])

        u = p2-p1
        v = p1-p0

        return np.cross(u, v) != 0

    def _valid_normal_3d(self, normal3D):
        # todo
        return True

    def _valid_point_3d(self, point3D):
        # todo
        return True


    @staticmethod
    def X_Plane(name, x, session):
        context = PlanarSequenceContext(session, name)
        return context

    @staticmethod
    def Y_Plane(name, y, session):
        context = PlanarSequenceContext(session, name)
        return context

    @staticmethod
    def Z_Plane(name, z, session):
        context = PlanarSequenceContext(session, name)
        context.set_plane([])
        return context
