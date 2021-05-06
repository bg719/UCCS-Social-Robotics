__version__ = "0.0.0"
__author__ = 'ancient-sentinel'


class DrawingSpec:

    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.keywords = []
        self.sequences = []


class InvalidDrawingSpecException(Exception):

    def __init__(self, message):
        self.message = message