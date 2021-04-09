__version__ = "0.0.0"
__author__ = 'anguyen7-99'

from enum import Enum


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
            'name': concept
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