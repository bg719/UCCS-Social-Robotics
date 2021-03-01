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

# SIMYAN utilities
from sim_utils.service import ServiceScope


# noinspection SpellCheckingInspection
class ActivityManager(object):
    """The activity responsible for management of SIMYAN services and activities."""
    APP_ID = "org.uccs.simyan"

    def __init__(self, qiapp):
        self.qiapp = qiapp
        self.events = stk.events.EventHelper(qiapp.session)
        self.s = stk.services.ServiceCache(qiapp.session)
        self.logger = stk.logging.get_logger(qiapp.session, self.APP_ID)
        self.scoped_services = [
            ServiceScope(qiapp, SIMMotorControl),
            ServiceScope(qiapp, SIMSpeech),
            ServiceScope(qiapp, SIMVision)
        ]
        self.say_info = self.s.ALTextToSpeech.say  # Set this to None to stop speaking SIMYAN info

    def _start_services(self):
        """Register SIMYAN services."""
        for service in self.scoped_services:
            if self.say_info:
                self.say_info("Registering" + str(service.name))
            service.create_scope()
            if not service.is_started and self.say_info:
                self.say_info("Registration failed.")

    def _stop_services(self):
        """Unregister SIMYAN services."""
        for service in self.scoped_services:
            if self.say_info:
                self.say_info("Stopping" + str(service.name))
            if service.is_started:
                service.close_scope()

    def on_start(self):
        self.say_info("Starting SIMYAN. Registering services.")
        self._start_services()

        if self.s.SIMMotorControl and self.say_info:
            self.say_info("Motor control is registered.")
        if self.s.SIMSpeech and self.say_info:
            self.say_info("Speech is registered.")
        if self.s.SIMVision and self.say_info:
            self.say_info("Vision is registered.")

        self.stop()

    def stop(self):
        """Standard way of stopping the application."""
        self.logger.info("Stopping Simyan Activity.")
        self.qiapp.stop()

    def on_stop(self):
        """Cleanup the activity"""
        self._stop_services()
        self.logger.info("Application finished: Simyan.")
        self.events.clear()


if __name__ == "__main__":
    stk.runner.run_activity(ActivityManager)
