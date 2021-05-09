import qi
import argparse
import sys



from naoqi import ALProxy

from enum import Enum


IP ="10.42.0.60"

asr = ALProxy("ALDialog", IP, 9559)

# class QiState for qiChatBuilder
class QiState(Enum):
    Blank = 0
    Topic = 1
    Language = 2
    Concept = 3
    User = 4
    Dialog = 5


# Global variable to store HumanSpeak module instance
HumanSpeak = None
memory = None


class QiChatBuilder:
    def __init__(self):
        self.script = ''
        self.concepts = {}
        self.state = QiState.Blank

    #sets topic for qiChat
    def set_topic(self, topic):
        #if state of qiChat script has a blank topic, then raise error to set topic  for the qiChat script
        if not self.state == QiState.Blank:
            raise ValueError("Can only set topic for a blank chat script.")
        if not topic.startswith('~'):
            topic = '~'+topic
        if not topic.endswith('()\n'):
            topic = topic + '()\n'
        self.script += 'topic: ' + topic
        self.state = QiState.Topic
        return self

    #sets language for qiChat
    def set_language(self, language):
        # if state of qiChat does not have a language not set up, the raise error to set up language for the the qiChat script
        if not self.state == QiState.Topic:
           raise ValueError ("Can only set language for a blank chat script.")

        if not language.endswith('\n'):
            language=language+'\n'
        self.script += 'language: ' + language
        self.state = QiState.Language
        return self

    # sets concept for qiChat
    def add_concept(self, concept, definitions=[]):
        #add a concept dictionary
        concept_def = {
            'name': concept
        }

        # if the state of qiChat does not have a topic, language, and concept set up,
        # then raise error to set up a topic, language, and concept for qiChat script
        if not self.state in (QiState.Topic, QiState.Language, QiState.Concept) :
            raise ValueError("qiChat must set up a concept for both user and robot ")
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

    # sets user says for qiChat
    def user_says(self, say):
        # if the state of qiChat for user says is greater than a blank script,
        # then  set up topic to add the user says for qiChat script
        if not self.state > QiState.Blank:
            raise ValueError("qiChat must define a topic for user.")
        if not say.startswith('('):
            say= '('+say
        if not say.endswith(')\n'):
            say = say+')\n'
        self.script += 'u: ' + say
        self.state = QiState.User
        return self

    #sets robot dialog for qiChat
    def robot_dialog(self, dialog):
        # if the state of qiChat for robot dialog  is greater than a blank script,
        # then  set up topic to add robot dialog  for qiChat script
        if not self.state >  QiState.Blank:
            raise ValueError("qiChat must define a topic for robot .")
        if not dialog.endswith('\n'):
            dialog = dialog +'\n'
        self.script += '' + dialog
        self.state= QiState.Dialog
        return self


    # builds the qiChat scripts
    def build(self):
        return self.script




def main(session):

    # Getting the service ALDialog
    ALDialog = session.service("ALDialog")
    ALDialog.setLanguage("English")


    builder = QiChatBuilder()
    builder.set_topic('Drawing')
    builder.set_language('enu')
    builder.add_concept('image', ['line', 'square', 'triangle','circle'])
    builder.user_says('Can you draw?')
    builder.robot_dialog('Yes,I can draw')

    # register a callback with the speech service that is
    # listening for the shape to draw
    # services.SIMSpeech.listenFor([list of words], justOnce=T/F, callback=selectShape)
    #
    # def selectShape(shape):
    #   save shape to a variable

    builder.user_says('Draw a _~image')
    builder.robot_dialog('Ok,I will draw a $1')
    script = builder.build()
    #print(script)

    # Loading the topics directly as text strings
    topic_name_1 = ALDialog.loadTopicContent(script)


    # Activating the loaded topics
    ALDialog.activateTopic(topic_name_1)


    # Starting the dialog engine - we need to type an arbitrary string as the identifier
    # We subscribe only ONCE, regardless of the number of topics we have activated
    ALDialog.subscribe('my_dialog_example')

    try:
        raw_input("\nSpeak to the robot using rules from both the activated topics. Press Enter when finished:")
    finally:
        # stopping the dialog engine
        ALDialog.unsubscribe('my_dialog_example')

        # Deactivating all topics
        ALDialog.deactivateTopic(topic_name_1)


        # now that the dialog engine is stopped and there are no more activated topics,
        # we can unload all topics and free the associated memory
        ALDialog.unloadTopic(topic_name_1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", type=str, default="10.42.0.60",
                        help="Robot's IP address. If on a robot or a local Naoqi - use '10.42.0.60' (this is the default value).")
    parser.add_argument("--port", type=int, default=9559,
                        help="port number, the default value is OK in most cases")

    args = parser.parse_args()
    session = qi.Session()
    try:
        session.connect("tcp://{}:{}".format(args.ip, args.port))
    except RuntimeError:
        print ("\nCan't connect to Naoqi at IP {} (port {}).\nPlease check your script's arguments."
               " Run with -h option for help.\n".format(args.ip, args.port))
        sys.exit(1)
    main(session)





