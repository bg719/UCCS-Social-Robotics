__version__ = "0.0.0"
__author__ = 'anguyen7-99, ancient-sentinel'

from enum import Enum
from inspect import getargspec, ismethod


class QiState(Enum):
    Blank = 0
    Topic = 1
    Language = 2
    Concept = 3
    User = 4
    Dialog = 5
    Events = 6


class QiChatBuilder:
    def __init__(self):
        self.script = ''
        self.concepts = {}
        self.state = QiState.Blank

    def set_topic(self, topic= str):
        """
        set qiChat topic
        qiChat topic would set up conversational topic for the robot and user
        Example: builder.set_topic('Greetings')

        :param topic: (str) the topic
        :returns: builder
        """
        if not self.state == QiState.Blank:
            raise ValueError("Can only set topic for a blank chat script.")
        if not topic.startswith('~'):
            topic = '~'+topic
        if not topic.endswith('()\n'):
            topic = topic + '()\n'
        self.script += 'topic: ' + topic
        self.state = QiState.Topic
        return self

    def set_language(self, language= str):
        """
        set qiChat language
        qiChat language would set up a langauge for the robot to understand the user
        (enu is the syntax for English)
        Example: builder.set_language('enu')

        :param language: (str)the language
        :returns: builder

        """
        if not language.endswith('\n'):
            language=language+'\n'
        self.script += 'language: ' + language
        self.state = QiState.Language
        return self

    def add_concept(self, concept= str, definitions=[]):
        """
         adds a qiChat concept
         qiChat concept defines a static list of items (words and/or phrases) that refer to one idea.
         Example: builder.add_concept('greetings',['hi' 'hello' 'hey there'])

        :param concept: (str) the concept
        :param definitions: (list) the definitions
        :returns: builder
        """
        concept_def = {
            'get_name': concept
        }
        if not concept.startswith('('):
            concept='('+concept
        if not concept.endswith(')'):
            concept = concept+')'

        my_def = ' ^repeat['
        for definition in definitions:
            my_def += ' {0} '.format(definition)
        my_def=my_def+']'
        concept_def['definition'] = my_def+']'
        concept = concept+my_def+'\n'
        self.concepts[concept] = my_def
        self.script += 'concept:' + concept
        self.state = QiState.Concept
        return self

    def user_says(self, say= str):
        """
        set qiChat for user's sayings
        builds defined dialog for the user to speak towards the robot
        Example: builder.user_says('Hello')

        :param say: (str) the sayings
        :returns: builder

        """
        if not say.startswith('('):
            say= '('+say
        if not say.endswith(')\n'):
            say = say+')\n'
        self.script += 'u: ' + say
        self.state = QiState.User
        return self

    def robot_dialog(self, dialog= str):
        """
        add qiChat robot dialog
        builds defined dialog for the robot to respond to the user
        Example: builder.robot_dialog('Hello there')

        :param dialog: (str) the dialog
        :returns: builder
        """
        if not dialog.endswith('\n'):
            dialog = dialog +'\n'
        self.script += '' + dialog
        self.state= QiState.Dialog
        return self

    def build(self):
        """
        builds qiChat scripts
        :returns: qiChat script
        """
        return self.script


class SpeechEvent:
    """A speech event which invokes a callback when a particular word is recognized."""

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

