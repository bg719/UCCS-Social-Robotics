import time
import qi
from naoqi import ALProxy
from naoqi import ALBroker
from naoqi import ALModule
from stk.events import EventHelper
from optparse import OptionParser
NAO_IP = "10.42.0.60"

# Global variable to store the SpeechEventListener module instance
SpeechEventListener = None
memory = None

class SpeechEventModule(ALModule):
    def __init__(self, name, tts):
        ALModule.__init__(self, name)
        self.name = name
        self.tts = tts

        global asr
        asr = ALProxy("ALSpeechRecognition", NAO_IP, 9559)
        asr.pause(True)
        asr.setLanguage("English")
        vocabulary = ["circle", "line", "triangle", "square"]
        asr.setVocabulary(vocabulary, True)
        asr.pause(False)
        global memory
        memory = ALProxy('ALMemory', NAO_IP, 9559)
        memory.subscribeToEvent("WordRecognized", name, "onWordRecognized")
    def onWordRecognized(self,value):
        asr.pause(True)
        self.tts.say("I heard: {0}".format(value[0]))
        print(value)
        asr.pause(False)

    def stop(self):
        memory.unsubscribeToEvent("WordRecognized", "{0}.onWordRecognized".format(self.name))

def main():
    # NAO parser
    parser = OptionParser()
    parser.add_option("--pip",
                      help="Parent broker port. The IP address or your robot",
                      dest="pip")
    parser.add_option("--pport",
                      help="Parent broker port. The port NAOqi is listening to",
                      dest="pport",
                      type="int")
    parser.set_defaults(
        pip=NAO_IP,
        pport=9559)
    (opts, args_) = parser.parse_args()
    pip = opts.pip
    pport = opts.pport

    tts = ALProxy("ALTextToSpeech", NAO_IP, 9559)
    # We need this broker to be able to construct
    # NAOqi modules and subscribe to other modules
    # The broker must stay alive until the program exists
    myBroker = ALBroker("myBroker",
                        "0.0.0.0",  # listen to anyone
                        0,  # find a free port and use it
                        pip,  # parent broker IP
                        pport)  # parent broker port
    global SpeechEventListener
    SpeechEventListener = SpeechEventModule("SpeechEventListener", tts)
    try:
        tts.say("Say something I know")
        while True:
            # Start the speech recognition engine with user Test_ASR
            asr.subscribe("Test_ASR")
            time.sleep(3)


            asr.unsubscribe("Test_ASR")
    except KeyboardInterrupt:
        print("Interrupted by user, shutting down")
        myBroker.shutdown()
        exit(0)
    finally:
        asr.unsubscribe("Test_ASR")
        SpeechEventListener.stop()

if __name__ == "__main__":
    main()