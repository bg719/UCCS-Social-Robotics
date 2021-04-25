__version__ = "0.0.0"
__author__ = 'ancient-sentinel'

import qi


class ServiceScope:
    """The scope for a service registered within the context of an existing Application"""

    def __init__(self, qiapp, service_class, service_name=None):
        self.service_class = service_class
        if not service_name:
            service_name = service_class.__name__
        self.name = service_name
        self.instance = service_class(qiapp)
        self.id = None
        self.session = qiapp.session
        self.is_started = False
        self.err_msg = None

    def create_scope(self):
        """Creates an instance of the service and registers it with the application session."""
        if self.is_started:
            return

        self.id = self.session.registerService(self.name, self.instance)

        if hasattr(self.instance, "on_start"):
            def handle_on_start_done(on_start_future):
                try:
                    self.err_msg = "Error in on_start(), stopping service: %s" \
                                   % on_start_future.error()
                    if hasattr(self.instance, "logger"):
                        self.instance.logger.error(self.err_msg)
                    else:
                        print self.err_msg
                except:
                    self.close_scope()

            qi.async(self.instance.on_start).addCallback(handle_on_start_done)

        self.is_started = self.id is not None

    def close_scope(self):
        """Unregisters the service instance from the application session and disposes the instance."""
        if self.id:
            # Call the services on_stop function if available
            if hasattr(self.instance, "on_stop"):
                # We need a qi.async call so that if the class is single threaded,
                # it will wait for callbacks to be finished.
                qi.async(self.instance.on_stop).wait()

            self.session.unregisterService(self.id)
            self.id = None
            self.is_started = False
            self.instance = None

