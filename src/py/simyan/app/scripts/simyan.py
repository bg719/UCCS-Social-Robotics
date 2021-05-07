__version__ = "0.0.0"
__author__ = 'ancient-sentinel'

import qi

import stk.runner
import stk.events
import stk.services
import stk.logging
import threading

# SIMYAN service modules
from motion import SIMMotion
from speech import SIMSpeech
from vision import SIMVision

# SIMYAN utilities
from simutils.service import ServiceScope


# noinspection SpellCheckingInspection
class SIMServiceManager(object):
    """The manager for SIMYAN services."""
    APP_ID = "org.uccs.simyan.SIMServiceManager"

    def __init__(self, qiapp, dev=False):
        """
        Initializes a new SIMYAN service manager instance.

        :param qiapp: (qi.Application) The hosting qi application.
        """
        self.qiapp = qiapp
        self.events = stk.events.EventHelper(qiapp.session)
        self.s = stk.services.ServiceCache(qiapp.session)
        self.logger = stk.logging.get_logger(qiapp.session, self.APP_ID)

        # Service state
        self.dev = dev
        self.scoped_services = [
            ServiceScope(qiapp, SIMMotion),
            ServiceScope(qiapp, SIMSpeech),
            ServiceScope(qiapp, SIMVision)
        ]
        self.lock = threading.Lock()
        self.semaphore = 0

    @qi.bind(returnType=qi.Void, paramsType=[])
    def startServices(self):
        """Starts and registers all SIMYAN services."""
        self.logger.info('Starting SIMYAN services.')
        self._start_services()

    @qi.bind(returnType=qi.Void, paramsType=[])
    def stopServices(self):
        """Stops and unregisters all SIMYAN services."""
        self.logger.info('Stopping SIMYAN services.')
        self._stop_services()

    @qi.nobind
    def on_start(self):
        """Performs startup operations."""
        self.logger.info('Starting SIMServiceManager.')
        if not self.dev:
            self.logger.info('Call SIMServiceManager.startServices to start all SIMYAN services.')
        else:
            self.startServices()

    @qi.nobind
    def stop(self):
        """Standard way of stopping the service."""
        self.logger.info("Stopping SIMServiceManager.")
        self.qiapp.stop()

    @qi.nobind
    def on_stop(self):
        """Cleanup after the the service."""
        self._stop_services()
        self.logger.info("Application finished: SIMServiceManager .")
        self.events.clear()

    @qi.nobind
    def _start_services(self):
        """Register SIMYAN services."""
        self.lock.acquire()
        self.semaphore += 1
        for service in self.scoped_services:
            self.logger.info("Registering service: {0}".format(service.name))
            if not service.is_started:
                service.create_scope()
            if not service.is_started:
                self.logger.info("Registration failed for service: {0}".format(service.name))
        self.lock.release()

    @qi.nobind
    def _stop_services(self):
        """Unregister SIMYAN services."""
        self.lock.acquire()
        if self.semaphore == 0:
            self.lock.release()
            return
        elif self.semaphore == 1:
            for service in self.scoped_services:
                self.logger.info("Stopping service: {0}".format(service.name))
                if service.is_started:
                    service.close_scope()
        self.semaphore -= 1
        self.lock.release()


if __name__ == "__main__":
    stk.runner.run_service(SIMServiceManager)
