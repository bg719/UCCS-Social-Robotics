__version__ = "0.0.0"
__author__ = 'anguyen7-99, ancient-sentinel'

import qi
from enum import Enum
from inspect import getargspec


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

    def __init__(self, words, callback):
        """
        Initializes a new speech event.

        :param words: ([Iterable[str]]) The list of words to be recognized.
        :param callback: (Callable) A callback function which takes one or
            two arguments. The first argument will always be the word that
            was recognized. If the function accepts a second argument, the
            confidence value will be passed as the second parameter.
        """
        if not callable(callback):
            raise ValueError('Callback must be a callable function.')

        self.callback = callback
        self.words = list(words)
        self.is_subscribed = False

        self._arg_count = len(getargspec(callback).args)
        self._id = None
        self._promise = qi.Promise()
        self._future = self._promise.future()
        self._future.addCallback(self._call)
        self._speech_service = None

        if self._arg_count not in (1, 2):
            raise ValueError('Callback must take only one or two arguments.')

    def register(self, speech_service):
        """
        Registers this speech event to the provided speech service.

        :param speech_service: (SIMSpeech) The speech service.
        :return: True if the registration was successful; otherwise, False.
        """
        if speech_service:
            self._speech_service = speech_service
            self._id = speech_service.subscribe(self.words, self._promise)
            self.is_subscribed = True
            return True
        else:
            return False

    def unregister(self):
        """
        Unregisters this speech event from the speech service.

        :return: True if the event was unregistered successfully;
            otherwise, False.
        """
        if self.is_subscribed and self._id is not None:
            self.is_subscribed = False
            return self._speech_service.unsubscribe(self._id)
        else:
            return False

    def _call(self, future):
        """
        Calls the registered callback with the value set for the
        future.

        :param future: (qi.Future) The speech event future.
        """
        if future.hasValue():
            if self._arg_count == 1:
                self.callback(future.value()[0])
            else:
                self.callback(*future.value())
