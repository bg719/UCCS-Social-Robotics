__version__ = "0.0.0"
__author__ = 'ancient-sentinel'

import qi


class ServiceScope:
    """The scope for a service registered within the context of an existing Application"""

    def __init__(self, qiapp, service_class, service_name=None):
        """
        Initializes a new service scope object.

        :param qiapp: (qi.Application) The hosting qi application.
        :param service_class: (class) The service class.
        :param service_name: (str) A name for the service. If None, the
            class name will be used by default.
        """
        self.service_class = service_class
        if not service_name:
            service_name = service_class.__name__
        self.name = service_name
        self.instance = None
        self._id = None
        self._qiapp = qiapp
        self._session = qiapp.session
        self.err_msg = None

    def create_scope(self):
        """Creates an instance of the service and registers it with the application session."""
        if self.is_started:
            return

        self.instance = self.service_class(self._qiapp)
        self._id = self._session.registerService(self.name, self.instance)

        if hasattr(self.instance, "on_start"):
            def handle_on_start_done(on_start_future):
                try:
                    if on_start_future.hasError():
                        self.err_msg = "Error in on_start(), stopping service: %s" \
                                       % on_start_future.error()
                        if hasattr(self.instance, "logger"):
                            self.instance.logger.error(self.err_msg)
                        else:
                            print self.err_msg
                except Exception as e:
                    print(e)
                    self.close_scope()

            qi.async(self.instance.on_start).addCallback(handle_on_start_done)

    def close_scope(self):
        """Unregisters the service instance from the application session and disposes the instance."""
        if self._id:
            # Call the services on_stop function if available
            if hasattr(self.instance, "on_stop"):
                # We need a qi.async call so that if the class is single threaded,
                # it will wait for callbacks to be finished.
                qi.async(self.instance.on_stop).wait()

            self._session.unregisterService(self._id)
            self._id = None
            self.instance = None

    @property
    def is_started(self):
        """Returns a value indicating whether a scope has been created and the service started."""
        return self._id is not None

