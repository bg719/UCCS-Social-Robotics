__version__ = "0.0.0"

import qi

import stk.runner
import stk.events
import stk.services
import stk.logging

from simutils.motion.models import ExecutionResult
from simutils.motion.handlers import PlanarSequenceHandler


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
        self.handlers = [
            PlanarSequenceHandler()
        ]

    @qi.bind(returnType=qi.Bool, paramsType=[qi.Object])
    def registerContext(self, context):
        """
        Registers the motion sequence context.

        :param context: (simutils.motion.contexts.MotionSequenceContext)
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
        return self._get_context_reg(name) is not None

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
        return any(handler.handles_type(type) for handler in self.handlers)

    @qi.bind(returnType=qi.Object, paramsType=[qi.String, qi.Object])
    def executeSequence(self, context_name, sequence):
        """
        Executes the motion sequence within the specified motion context.

        :param context_name: (str) The context name.
        :param sequence: (simutils.motion.models.MotionSequence)
            The motion sequence.
        :return: (simutils.motion.models.ExecutionResult)
            The result of the sequence execution.
        """
        if not sequence:
            return ExecutionResult.invalid_arg("sequence")

        # get the context registration
        reg = self._get_context_reg(context_name)
        if not reg:
            return ExecutionResult.no_such_context(context_name)

        # the context registration contains the context and its
        # handler as a tuple, as so: (context, handler)
        context, handler = reg

        # execute the sequence using the handler and context
        result = None
        try:
            result = handler.execute_seq(context, sequence)
        except RuntimeError as e:
            result = ExecutionResult.error_result(
                "An unhandled error occurred while attempting to execute"
                + "a motion sequence for context: {0}".format(context_name)
                + "\nMessage: {0}".format(e.message))
        return result

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
    def _get_context_reg(self, name):
        """
        Attempts to get the registration for the context with the
        specified name.

        :param name: (str) The context name.
        :return: The context registration or None if no context
            was found.
        """
        return self.contexts.get(name, None)

    @qi.nobind
    def _register_context(self, context):
        """
        Registers the motion sequence context.

        :param context: (simutils.motion.contexts.MotionSequenceContext)
            The motion sequence context.
        :return: True if the context was registered successfully;
            otherwise, False.
        """
        for handler in self.handlers:
            if handler.handles_type(context.type()):
                self.contexts[context.name()] = (context, handler)
                return True
        return False


####################
# Setup and Run
####################


if __name__ == "__main__":
    stk.runner.run_service(SIMMotorControl)
