__version__ = "0.0.0"
__author__ = 'anguyen7-99, ancient-sentinel'

from enum import Enum
from inspect import getargspec, ismethod


class QiState(Enum):
    """ class QiState for qiChatBuilder """
    Blank = 0
    Topic = 1
    Language = 2
    Concept = 3
    User = 4
    Dialog = 5


class QiChatBuilder:
    def __init__(self):
        self.script = ''
        self.concepts = {}
        self.state = QiState.Blank

    def set_topic(self, topic):
        """sets topic for qiChat"""
        # if state of qiChat script has a blank topic, then raise error to set topic  for the qiChat script
        if not self.state == QiState.Blank:
            raise ValueError("Can only set topic for a blank chat script.")
        if not topic.startswith('~'):
            topic = '~' + topic
        if not topic.endswith('()\n'):
            topic = topic + '()\n'
        self.script += 'topic: ' + topic
        self.state = QiState.Topic
        return self

    def set_language(self, language):
        """sets language for qiChat"""
        # if state of qiChat does not have a language not set up,
        # then raise error to set up language for the the qiChat script
        if not self.state == QiState.Topic:
            raise ValueError("Can only set language for a blank chat script.")

        if not language.endswith('\n'):
            language = language+'\n'
        self.script += 'language: ' + language
        self.state = QiState.Language
        return self

    def add_concept(self, concept, definitions=[]):
        """sets up qiChat concept """
        # add a concept dictionary
        concept_def = {
            'name': concept
        }

        # If the state of qiChat does not have a topic, language, and concept set up,
        # then raise error to set up a topic, language, and concept for qiChat script
        if self.state not in (QiState.Topic, QiState.Language, QiState.Concept):
            raise ValueError("qiChat must set up a concept for both user and robot ")
        if not concept.startswith('('):
            concept = '(' + concept
        if not concept.endswith(')'):
            concept = concept + ')'

        my_def = ' ^repeat['
        for definition in definitions:
            my_def += ' {0} '.format(definition)
        my_def = my_def + ']'
        concept_def['definition'] = my_def + ']'
        concept = concept + my_def + '\n'
        self.concepts[concept] = my_def
        self.script += 'concept:' + concept
        self.state = QiState.Concept
        return self

    def user_says(self, say):
        """sets user says for qiChat """
        # if the state of qiChat for user says is greater than a blank script,
        # then  set up topic to add the user says for qiChat script
        if not self.state > QiState.Blank:
            raise ValueError("qiChat must define a topic for user.")
        if not say.startswith('('):
            say = '(' + say
        if not say.endswith(')\n'):
            say = say + ')\n'
        self.script += 'u: ' + say
        self.state = QiState.User
        return self

    def robot_dialog(self, dialog):
        """ sets robot dialog for qiChat """
        # if the state of qiChat for robot dialog  is greater than a blank script,
        # then  set up topic to add robot dialog  for qiChat script
        if not self.state > QiState.Blank:
            raise ValueError("qiChat must define a topic for robot .")
        if not dialog.endswith('\n'):
            dialog = dialog + '\n'
        self.script += '' + dialog
        self.state = QiState.Dialog
        return self

    def build(self):
        """builds the qiChat scripts"""
        return self.script


class SpeechEvent:
    """A speech event which invokes a callback when a particular phrase is recognized."""

    def __init__(self, phrases, callback, minimum_confidence=0.55, repeat=False):
        """
        Initializes a new speech event.

        :param phrases: ([Iterable[str]]) The list of phrases to be recognized.
        :param callback: (Callable) A callback function which takes one or
            two arguments. The first argument will always be the phrase that
            was recognized. If the function accepts a second argument, the
            confidence value will be passed as the second parameter.
        :param minimum_confidence: (float) The minimum confidence that a
            recognized phrase matches one defined for this event. Must be
            a value between 0 and 1, inclusive.
        :param repeat: (bool) If True, this speech event will re-register
            and the callback be re-invoked after each time it is raised;
            otherwise, it will be unsubscribed after the first occurrence.
        """
        if not callable(callback):
            raise ValueError('Callback must be a callable function.')

        if not (0 < minimum_confidence <= 1):
            raise ValueError('Minimum confidence must be a value between 0 and 1.')

        if isinstance(phrases, str):
            phrases = [phrases]

        self.callback = callback
        self.phrases = list(phrases)
        self.minimum_confidence = minimum_confidence
        self.repeat = repeat

        self._arg_count = len(getargspec(callback).args)
        self._is_method = ismethod(callback)

        if not self._is_method:
            allowed_count = (1, 2)
        else:
            allowed_count = (2, 3)

        if self._arg_count not in allowed_count:
            raise ValueError('Callback must take only one or two arguments.')

        self._subscription = None
        self._id = None
        self._is_subscribed = False
        self._future = None
        self._speech_service = None

    def is_subscribed(self):
        """Gets a value indicating whether this speech event is subscribed."""
        return self._is_subscribed

    def register(self, speech_service):
        """
        Registers this speech event to the provided speech service.

        :param speech_service: (SIMSpeech) The speech service.
        :return: True if the registration was successful; otherwise, False.
        """
        if speech_service:
            self._speech_service = speech_service
            return self._register()
        else:
            return False

    def unregister(self):
        """
        Unregisters this speech event from the speech service.

        :return: True if the event was unregistered successfully;
            otherwise, False.
        """
        if self._is_subscribed:
            self._is_subscribed = False
            self._future.cancel()
            return True
        else:
            return False

    def wait(self, timeout=None):
        """
        Waits for the speech event to occur. If a timeout is specified
        the event subscription will be canceled after that period if it has
        not already occurred.

        :param timeout: (float) The timeout in seconds.
        :return: (qi.FutureState) The final state of the event future.
        """
        if self._is_subscribed:
            if not timeout:
                return self._future.wait()
            else:
                return self._future.wait(timeout*1000000)

    def _call(self, future):
        """
        Calls the registered callback with the value set for the
        future and attempts to re-register this event if it is
        repeatable.

        :param future: (qi.Future) The speech event future.
        """
        if future.hasValue():
            if self._arg_count == 1 or (self._is_method and self._arg_count == 2):
                self.callback(future.value()[0])
            else:
                self.callback(*future.value())
        elif future.hasError():
            self._is_subscribed = False

        if self.repeat and not self._register():
            raise SpeechEventException('Failed to re-register speech event.')

    def _register(self):
        self._future = self._speech_service.subscribe(
            self.phrases, self.minimum_confidence).future

        self._is_subscribed = True
        self._future.addCallback(self._call)
        return self._is_subscribed


class SpeechEventException(Exception):
    """An exception raised due to a speech event error."""

    def __init__(self, message):
        """
        Initializes a new speech event exception with the provided
        message.

        :param message: (str) The error message.
        """
        self.message = message

