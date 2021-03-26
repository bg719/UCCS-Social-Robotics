__version__ = "0.0.0"

import qi

import stk.runner
import stk.events
import stk.services
import stk.logging


class SIMMotorControl(object):
    """A SIMYAN NAOqi service providing supplemental motor control services."""
    APP_ID = "org.uccs.simyan.SIMMotorControl"

    def __init__(self, qiapp):
        # generic activity boilerplate
        self.qiapp = qiapp
        self.events = stk.events.EventHelper(qiapp.session)
        self.s = stk.services.ServiceCache(qiapp.session)
        self.logger = stk.logging.get_logger(qiapp.session, self.APP_ID)
        # Internal variables
        self.level = 0

    @qi.bind(returnType=qi.Void, paramsType=[qi.Int8])
    def set(self, level):
        "Set level"
        self.level = level

    @qi.bind(returnType=qi.Int8, paramsType=[])
    def get(self):
        "Get level"
        return self.level

    @qi.bind(returnType=qi.Void, paramsType=[])
    def reset(self):
        "Reset level to default value"
        return self.set(0)

    @qi.bind(returnType=qi.Void, paramsType=[])
    def stop(self):
        """Stop the service."""
        self.logger.info("SIMMotorControl stopped by request.")
        self.qiapp.stop()

    @qi.nobind
    def on_stop(self):
        """Cleanup (add yours if needed)"""
        self.logger.info("SIMMotorControl finished.")


####################
# Setup and Run
####################


if __name__ == "__main__":
    stk.runner.run_service(SIMMotorControl)
