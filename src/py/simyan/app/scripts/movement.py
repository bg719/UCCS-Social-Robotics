__version__ = "0.0.0"

import qi

import stk.runner
import stk.events
import stk.services
import stk.logging


from sim_utils.motion import MotionSequenceContext


class SIMMotorControl(object):
    """A SIMYAN NAOqi service providing supplemental motor control services."""
    APP_ID = "org.uccs.simyan.SIMMotorControl"

    def __init__(self, qiapp):
        # generic activity boilerplate
        self.qiapp = qiapp
        self.events = stk.events.EventHelper(qiapp.session)
        self.s = stk.services.ServiceCache(qiapp.session)
        self.logger = stk.logging.get_logger(qiapp.session, self.APP_ID)

        # service state
        self.contexts = {}

    @qi.bind(returnType=qi.Bool, paramsType=[qi.Object], methodName="registerContext")
    def register_context(self, context):
        if not self._can_register(context):
            return False
        self.contexts[context.name] = context
        return True

    @qi.bind(returnType=qi.Bool, paramsType=[qi.String], methodName="hasContext")
    def has_context(self, name):
        return name in self.contexts

    @qi.bind(returnType=qi.Bool, paramsType=[qi.String], methodName="removeContext")
    def remove_context(self, name):
        context = self.contexts.pop(name, None)
        return context is not None

    @qi.bind(returnType=qi.Bool, paramsType=[qi.String], methodName="supportsType")
    def supports_type(self, type):
        """
        Determines whether the context type is supported.
        :return: True if supported, otherwise False
        """
        # todo
        pass

    @qi.bind(returnType=qi.Void, paramsType=[])
    def stop(self):
        """Stop the service."""
        self.logger.info("SIMMotorControl stopped by request.")
        self.qiapp.stop()

    @qi.nobind
    def on_stop(self):
        """Cleanup (add yours if needed)"""
        self.logger.info("SIMMotorControl finished.")

    @qi.nobind
    def _can_register(self, context):
        """
        Determines whether the context can be registered.
        :return: True if the context can be created, otherwise False
        """
        return (not self.has_context(context.name)) and self.supports_type(context.type)


####################
# Setup and Run
####################


if __name__ == "__main__":
    stk.runner.run_service(SIMMotorControl)
