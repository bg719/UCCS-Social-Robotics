__version__ = "0.0.0"
__author__ = 'ancient-sentinel'

import qi

from inspect import  isclass


class ServiceScope:
    """The scope for a service registered within the context of an existing Application"""

    def __init__(self, qiapp, service_class, service_name=None):
        if not isclass(service_class):
            raise ValueError('The service must be a class.')

        self.service_class = service_class
        if not service_name:
            service_name = service_class.__name__
        self.name = service_name

        self.qiapp = qiapp
        self.session = qiapp.session
        self.err_msg = None

        self._id = None
        self._instance = None
        self._is_started = False

    def create_scope(self, *args, **kwargs):
        """
        Creates an instance of the service and registers it with the application session.

        :param args: (Any) The positional arguments to pass to the instance.
        :param kwargs: (Any) The keyword arguments to pass to the instance.
        """
        if self._is_started:
            return

        self._instance = self.service_class(self.qiapp, *args, **kwargs)

        self._id = self.session.registerService(self.name, self.instance)

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

        self._is_started = self.id is not None

    def close_scope(self):
        """Unregisters the service instance from the application session and disposes the instance."""
        if self.id:
            # Call the services on_stop function if available
            if hasattr(self.instance, "on_stop"):
                # We need a qi.async call so that if the class is single threaded,
                # it will wait for callbacks to be finished.
                qi.async(self.instance.on_stop).wait()

            self.session.unregisterService(self.id)
            self._id = None
            self._instance = None
            self._is_started = False

    def id(self):
        """Gets the ID of the service."""
        return self._id

    def instance(self):
        """Gets the service instance."""
        return self._instance

    def is_started(self):
        """Gets a value indicating whether the service is started."""
        return self._is_started

