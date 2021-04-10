__version__ = "0.0.0"

import qi

import stk.runner
import stk.events
import stk.services
import stk.logging


# noinspection PyPep8Naming
class SIMMotorControl(object):
    """A SIMYAN NAOqi service providing supplemental motor control services."""
    APP_ID = "org.uccs.simyan.SIMMotorControl"

    def __init__(self, qiapp):
        """
        Initializes a new instance of the SIMMotorControl service.

        :param qiapp: (qi.Application) The hosting qi application.
        """
        # generic activity boilerplate
        self.qiapp = qiapp
        self.events = stk.events.EventHelper(qiapp.session)
        self.s = stk.services.ServiceCache(qiapp.session)
        self.logger = stk.logging.get_logger(qiapp.session, self.APP_ID)

        # service state
        self.contexts = {}
        self.handlers = {}

    @qi.bind(returnType=qi.Bool, paramsType=[qi.Object])
    def registerContext(self, context):
        """
        Registers the motion sequence context.

        :param context: (simutils.motion.MotionSequenceContext)
            The motion sequence context.
        :return: True if the context was registered successfully;
            otherwise, False.
        """
        if not self._can_register(context):
            return False
        return self._register_context(context)

    @qi.bind(returnType=qi.Bool, paramsType=[qi.String])
    def hasContext(self, name):
        """
        Checks whether a context with the specified name is
        registered.

        :param name: (str) The context name.
        :return: True if the context is registered;
            otherwise, False.
        """
        return self._get_context(name) is not None

    @qi.bind(returnType=qi.Bool, paramsType=[qi.String])
    def removeContext(self, name):
        """
        Removes the context with the specified name if it is
        registered.

        :param name: (str) The context name.
        :return: True if the context was registered and has
            been removed; otherwise, False.
        """
        context = self.contexts.pop(name, None)
        return context is not None

    @qi.bind(returnType=qi.Bool, paramsType=[qi.String])
    def supportsContextType(self, type):
        """
        Determines whether the context type is supported.

        :param type: (str) The context type.
        :return: True if the type is supported, otherwise False
        """
        return type in self.handlers

    @qi.bind(returnType=qi.Object, paramsType=[qi.String, qi.Object])
    def executeSequence(self, context_name, sequence):
        """
        Executes the motion sequence within the specified motion context.

        :param context_name: (str) The context name.
        :param sequence: (simutils.motion.MotionSequence)
            The motion sequence.
        :return: (ExecutionResult) The result of the sequence execution.
        """
        if not sequence:
            return ExecutionResult.invalid_arg("sequence")

        context = self._get_context(context_name)
        if not context:
            return ExecutionResult.no_such_context(context_name)

        # todo: get the handler
        # todo: pass the sequence to the handler
        # todo: return the result

    @qi.bind(returnType=qi.Void, paramsType=[])
    def stop(self):
        """Stop the service."""
        self.logger.info("SIMMotorControl stopped by request.")
        self.qiapp.stop()

    @qi.nobind
    def on_stop(self):
        """Cleanup resources."""
        self.logger.info("SIMMotorControl finished.")

    @qi.nobind
    def _can_register(self, context):
        """
        Determines whether the context can be registered.

        :return: True if the context can be created; otherwise, False.
        """
        return (not self.hasContext(context.name())) and \
            self.supportsContextType(context.type())

    @qi.nobind
    def _get_context(self, name):
        """
        Attempts to get the context with the specified name.

        :param name: the context name
        :return: the context or None if no context was found
        """
        return self.contexts.get(name, None)

    @qi.nobind
    def _register_context(self, context):
        """
        Registers the motion sequence context.

        :param context: (simutils.motion.MotionSequenceContext)
            The motion sequence context.
        :return: True if the context was registered successfully;
            otherwise, False.
        """
        pass


class PlanarSequenceHandler:

    def __init__(self):
        pass


####################
# Setup and Run
####################


if __name__ == "__main__":
    stk.runner.run_service(SIMMotorControl)
