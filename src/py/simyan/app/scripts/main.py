__version__ = "0.0.0"
__author__ = 'ancient-sentinel'

import qi
import stk.runner
import stk.events
import stk.services
import stk.logging

# SIMYAN service modules
from movement import SIMMotorControl
from speech import SIMSpeech
from vision import SIMVision

# noinspection SpellCheckingInspection
class SimyanActivitiesManager(object):
    """A sample standalone app, that demonstrates simple Python usage"""
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
        self.say = self.s.ALTextToSpeech.say

    def start_services(self):
        """Register SIMYAN services."""
        for service in self.scoped_services:
            self.say("Registering" + str(service.name))
            service.create_scope()

    def stop_services(self):
        """Unregister SIMYAN services"""
        for service in self.scoped_services:
            self.say("Stopping" + str(service.name))
            if service.is_started:
                service.close_scope()

    def on_start(self):
        self.start_services()

        if self.s.SIMMotorControl:
            self.s.ALTextToSpeech.say("Motor control is registered.")
        if self.s.SIMSpeech:
            self.s.ALTextToSpeech.say("Speech is registered.")
        if self.s.SIMVision:
            self.s.ALTextToSpeech.say("Vision is registered.")

        self.s.ALTextToSpeech.say("Stopping")
        self.stop()

    def stop(self):
        """Standard way of stopping the application."""
        self.logger.info("Stopping Simyan Activities Manager.")
        self.qiapp.stop()

    def on_stop(self):
        """Cleanup the activity"""
        self.stop_services()
        self.logger.info("Application finished: Simyan Activities Manager.")
        self.events.clear()


class ServiceScope:
    """The scope for a service registered as part of an Application"""

    def __init__(self, qiapp, service_class, service_name=None):
        self.service_class = service_class
        if not service_name:
            service_name = service_class.__name__
        self.name = service_name
        self.instance = service_class(qiapp)
        self.id = None
        self.session = qiapp.session
        self.is_started = False

    def create_scope(self):
        self.id = self.session.registerService(self.name, self.instance)

        if hasattr(self.instance, "on_start"):
            def handle_on_start_done(on_start_future):
                try:
                    msg = "Error in on_start(), stopping service: %s" \
                          % on_start_future.error()
                    if hasattr(self.instance, "logger"):
                        self.instance.logger.error(msg)
                    else:
                        print msg
                except:
                    self.close_scope()
            qi.async(self.instance.on_start).addCallback(self._handle_on_start_done)

        self.is_started = self.id is not None

    def close_scope(self):
        # Cleanup
        if hasattr(self.instance, "on_stop"):
            # We need a qi.async call so that if the class is single threaded,
            # it will wait for callbacks to be finished.
            qi.async(self.instance.on_stop).wait()
        if self.id:
            self.session.unregisterService(self.id)
            self.id = None
            self.is_started = False




if __name__ == "__main__":
    stk.runner.run_activity(SimyanActivitiesManager)
