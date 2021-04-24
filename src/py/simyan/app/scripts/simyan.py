__version__ = "0.0.0"
__author__ = 'ancient-sentinel'

import stk.runner
import stk.events
import stk.services
import stk.logging

# SIMYAN service modules
from movement import SIMMotorControl
from speech import SIMSpeech
from vision import SIMVision

from drawing import SIMDrawingDemo

# SIMYAN utilities
from simutils.service import ServiceScope
from simutils.motion.absolute import *


# noinspection SpellCheckingInspection
class SIMActivityManager(object):
    """The activity responsible for management of SIMYAN services and activities."""
    APP_ID = "org.uccs.simyan.SIMActivityManager"

    def __init__(self, qiapp):
        self.qiapp = qiapp
        self.events = stk.events.EventHelper(qiapp.session)
        self.s = stk.services.ServiceCache(qiapp.session)
        self.logger = stk.logging.get_logger(qiapp.session, self.APP_ID)
        self.scoped_services = [
            ServiceScope(qiapp, SIMMotorControl),
            # ServiceScope(qiapp, SIMSpeech),
            # ServiceScope(qiapp, SIMVision)
        ]
        self.activity = None
        # Set this to None to stop speaking SIMYAN info
        self.say_info = self.s.ALTextToSpeech.say

    def _start_services(self):
        """Register SIMYAN services."""
        for service in self.scoped_services:
            if self.say_info:
                self.say_info("Registering " + str(service.name))
            service.create_scope()
            if not service.is_started and self.say_info:
                self.say_info("Registration failed.")

    def _stop_services(self):
        """Unregister SIMYAN services."""
        for service in self.scoped_services:
            if self.say_info:
                self.say_info("Stopping " + str(service.name))
            if service.is_started:
                service.close_scope()

    def _active_services(self, log=False):
        names = []
        self.logger.info("Querying active Simyan services...")
        for service in self.scoped_services:
            if service.is_started:
                names.append(service.name)
                info = service.name + " is registered."
                self.logger.info(info)
                if self.say_info:
                    self.say_info(info)
        return names

    def on_start(self):
        # self.say_info("Starting Simyan. Registering services.")
        self._start_services()
        # self._active_services(log=True)

	if not self.s.SIMMotorControl.repeat("Called motor control"):
	    # class MyObj:
		# name = "My object"
	    
	    # obj = MyObj()
	    context = AbsoluteSequenceContext(
		self.qiapp.session, self.APP_ID, 
		motion_proxy=self.s.SIMMotorControl, extensive_validation=False)
	    self.s.SIMMotorControl.registerContext(context)
	else:
	    draw = ServiceScope(self.qiapp, SIMDrawingDemo)
	    try:
	        draw.create_scope()
	    except Exception as e:
	        self.logger.info(e.message)
	        draw.close_scope()

        self.events.connect("FrontTactilTouched", self.stop)
        # self.stop()

    def stop(self, *args):
        """Standard way of stopping the application."""
        self.logger.info("Stopping Simyan activity.")
        self.qiapp.stop()

    def on_stop(self):
        """Cleanup the activity"""
        self._stop_services()
        self.logger.info("Application finished: Simyan.")
        self.events.clear()


class SIMActivityContext:
    """The context for an executing SIMYAN activity."""
    APP_ID = "org.uccs.simyan.SIMActivityContext"

    def __init__(self, qiapp):
        self.qiapp = qiapp
        self.events = stk.events.EventHelper(qiapp.session)
        self.s = stk.services.ServiceCache(qiapp.session)
        self.logger = stk.logging.get_logger(qiapp.session, self.APP_ID)
        self.scoped_services = []


if __name__ == "__main__":
    stk.runner.run_service(SIMActivityManager)
