__version__ = "0.0.0"
__author__ = 'ancient-sentinel'

import stk.runner
import stk.events
import stk.services
import stk.logging

# SIMYAN service modules
from motion import SIMMotion
from speech import SIMSpeech
from vision import SIMVision

from drawing import SIMDrawingDemo

# SIMYAN utilities
from simutils.service import ServiceScope
from simutils.speech import SpeechEvent
from simutils.motion.absolute import *


# noinspection SpellCheckingInspection
class SIMServiceManager(object):
    """The manager for SIMYAN services."""
    APP_ID = "org.uccs.simyan.SIMServiceManager"

    def __init__(self, qiapp):
        self.qiapp = qiapp
        self.events = stk.events.EventHelper(qiapp.session)
        self.s = stk.services.ServiceCache(qiapp.session)
        self.logger = stk.logging.get_logger(qiapp.session, self.APP_ID)

        self.scoped_services = [
            ServiceScope(qiapp, SIMMotion),
            ServiceScope(qiapp, SIMSpeech),
            ServiceScope(qiapp, SIMVision)
        ]

    def startServices(self):
        self.logger.info('Starting SIMYAN service.')
        self._start_services()

    def stopServices(self):
        self.logger.info('Stopping SIMYAN services.')

    def on_start(self):
        self.logger.info('Starting SIMServiceManager.')
        self._start_services()

    # def _active_services(self, log=False):
    #     names = []
    #     self.logger.info("Querying active Simyan services...")
    #     for service in self.scoped_services:
    #         if service.is_started:
    #             names.append(service.name)
    #             info = service.name + " is registered."
    #             self.logger.info(info)
    #             if self.say_info:
    #                 self.say_info(info)
    #     return names

    def stop(self, *args):
        """Standard way of stopping the application."""
        self.logger.info("Stopping SIMServiceManager.")
        self.qiapp.stop()

    def on_stop(self):
        """Cleanup the activity"""
        self._stop_services()
        self.logger.info("Application finished: SIMServiceManager .")
        self.events.clear()

    def _start_services(self):
        """Register SIMYAN services."""
        for service in self.scoped_services:
            self.logger.info("Registering service: {0}".format(service.name))
            service.create_scope()
            if not service.is_started:
                self.logger.info("Registration failed for service: {0}".format(service.name))

    def _stop_services(self):
        """Unregister SIMYAN services."""
        for service in self.scoped_services:
            self.logger.info("Stopping service: {0}".format(service.name))
            if service.is_started:
                service.close_scope()


if __name__ == "__main__":
    stk.runner.run_service(SIMServiceManager)
