__version__ = "0.0.0"
__author__ = 'ancient-sentinel'


class DrawingSpec:
    """A drawing specification."""
    def __init__(self, name, description):
        """
        Initializes a new drawing specification.

        :param name: (str) The name of the specification.
        :param description: (str) A description of the drawing
            represented by the specification.
        """
        self.name = name
        self.description = description
        self.keywords = []
        self.sequences = []


class InvalidDrawingSpecException(Exception):
    """An exception occurring due to an invalid drawing specification."""
    def __init__(self, message):
        """
        Initializes a new invalid drawing specification exception instance.

        :param message: (str) The message describing the error.
        """
        self.message = message
