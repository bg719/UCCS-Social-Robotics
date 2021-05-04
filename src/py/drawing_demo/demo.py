__version__ = "0.0.0"
__author__ = 'ancient-sentinel'

import functools

import qi
import stk.runner
import stk.events
import stk.services
import stk.logging
import random

from loaders.absolute_specs import AbsoluteJsonSpecLoader

# import simutils.motion.preparation as prep
# import simutils.motion.constants as const
# from simutils.motion.absolute import *

import simyan.app.scripts.simutils.motion.preparation as prep
from simyan.app.scripts.simutils.motion.absolute import *
from simyan.app.scripts.simyan import SIMServiceManager
from simyan.app.scripts.simutils.service import ServiceScope
from simyan.app.scripts.simutils.speech import SpeechEvent, QiChatBuilder


class SIMDrawingDemo(object):
    """A SIMYAN drawing activity demo."""
    APP_ID = "org.uccs.simyan.SIMDrawingDemo"

    def __init__(self, qiapp):
        # generic activity boilerplate
        self.qiapp = qiapp
        self.events = stk.events.EventHelper(qiapp.session)
        self.s = stk.services.ServiceCache(qiapp.session)
        self.logger = stk.logging.get_logger(qiapp.session, self.APP_ID)

        # todo: remove these
        self.ssm_scope = ServiceScope(qiapp, SIMServiceManager)
        self.ssm_scope.create_scope()

        # NAO services
        self.almotion = self.s.ALMotion
        self.dialog = self.s.ALDialog
        self.posture = self.s.ALRobotPosture
        self.tts = self.s.ALTextToSpeech

        # SIMYAN services
        self.ssm = self.s.SIMServiceManager
        self.speech = None
        self.motion = None

        # Demo state
        self.drawing_specs = {}
        self.loaders = {
            const.CTYPE_ABSOLUTE: AbsoluteJsonSpecLoader()
        }
        self.language = "English"
        self.quit = False
        self.max_reprompts = 3
        self.arm = const.EF_LEFT_ARM
        self.seconds_to_clean_board = 2

    def on_start(self):
        try:
            self.ssm.startServices()
            self.speech = self.s.SIMSpeech
            self.motion = self.s.SIMMotion

            self.load_drawing_specs()
            self.logger.info("Drawing Specs: {0}".format(self.drawing_specs.keys()))

            self.start_demo()
        except Exception as e:
            self.logger.info("Error starting demo: {0}".format(e.message))
        finally:
            self.stop()

    def start_demo(self):
        topic = None
        try:
            self.logger.info("Starting demo.")
            self.listen_for_trigger()

            self.logger.info("Explaining activity...")
            self.explain_activity()

            self.logger.info("Beginning main drawing activity...")
            self.main_activity()
        except Exception as e:
            self.logger.error("Encountered error: {0}".format(e.message))
        finally:
            self.stop_chat(topic, True)

    def listen_for_trigger(self):
        def heard(phrase):
            pass

        heard_trigger = SpeechEvent(["let's draw something"], heard)

        if not heard_trigger.register(self.speech):
            raise DrawingDemoException(
                "Could not register speech event with SIMYAN speech service.")

        self.logger.info("Listening for trigger phrase...")
        heard_trigger.wait(30)

    def explain_activity(self):
        # builder = QiChatBuilder()
        # builder.set_topic('drawing')
        # builder.set_language(self.language)
        # script = builder.build()
        # self.chat(script)

        self.tts.say("Awesome! I love drawing!")
        objects = self.drawing_specs.keys()
        objects = ", ".join(objects[:-1]) + ", or {0}".format(objects[-1])
        self.tts.say("I can draw a {0}".format(objects))

    def main_activity(self):
        while not self.quit:
            drawing = self.select_drawing()

            if drawing not in self.drawing_specs:
                self.invalid_selection(drawing)
                continue

            self.confirm_selection(drawing)
            self.draw(self.drawing_specs[drawing])
            self.emote()
            self.prepare_repeat()

    def select_drawing(self, reprompt=0):
        if reprompt > self.max_reprompts:
            raise DrawingDemoException(
                'Maximum number of drawing selection re-prompts reached.')

        class Nonlocal:
            selection = None

        def set_selection(phrase):
            Nonlocal.selection = phrase

        hear_selection = SpeechEvent(self.drawing_specs.keys(), set_selection)

        self.tts.say("What would you like me to draw?")

        if not hear_selection.register(self.speech):
            raise DrawingDemoException(
                "Could not register speech event with SIMYAN speech service.")

        hear_selection.wait(10)

        timer = self.timer(0.1)
        timer.wait()

        if not Nonlocal.selection:
            return self.select_drawing(reprompt + 1)

        return Nonlocal.selection

    def invalid_selection(self, selection):
        self.tts.say("I'm sorry, but I don't know how to draw a {0}".format(selection))

    def draw(self, spec):
        sequence = next(s for s in spec.sequences if s.effector == self.arm)

        if not sequence:
            raise DrawingDemoException(
                "No sequence for the current arm in drawing specification: {0}".format(spec.name))

        if isinstance(sequence, AbsoluteSequence):
            context = AbsoluteSequenceContext(self.APP_ID, lambda: self.set_initial_pose(), extensive_validation=False)
        else:
            raise DrawingDemoException(
                "Unexpected sequence type: {0}".format(type(sequence)))

        if not context.register(self.motion):
            raise DrawingDemoException(
                "Failed to register {0} context with the motion service.".format(type(context)))

        result = context.execute_sequence(sequence, self.motion)

        breath_future = prep.async_enable_breathing((const.CHAIN_ARMS, const.CHAIN_LEGS), self.almotion)

        context.unregister(self.motion)

        breath_future.wait()

        if not result.success:
            raise DrawingDemoException(
                "Error executing motion sequence. Status: {0} - Message: {1}".format(result.status, result.message))

    def emote(self):
        emotes = [
            "That was fun!",
            "I enjoyed that! Maybe we should do it again?",
            "Wow! I love drawing!",
            "We should do that again!",
            "I'm having so much fun!"
        ]
        pick = random.choice(emotes)
        self.tts.say(pick)

    def prepare_repeat(self):
        self.tts.say("Would you like me to draw again?")

        class Nonlocal:
            selection = None

        def set_selection(phrase):
            Nonlocal.selection = phrase

        affirmative = ('yes', 'yeah', 'sure', 'ok')
        negative = ('no', 'nope')
        hear_selection = SpeechEvent(affirmative + negative, set_selection)

        if not hear_selection.register(self.speech):
            raise DrawingDemoException(
                "Could not register speech event with SIMYAN speech service.")

        hear_selection.wait(10)

        timer = self.timer(0.1)
        timer.wait()

        if Nonlocal.selection not in affirmative:
            self.tts.say("Ok, we'll stop drawing for now.")
            self.quit = True
            return

        self.tts.say("Awesome! I'll give you a couple seconds to wipe the board for me.")

        timer = self.timer(self.seconds_to_clean_board)
        timer.wait()

        self.tts.say("Thanks! Let's draw some more!")

    def confirm_selection(self, selection):
        confirmations = [
            "Ok, I'll draw a {0}",
            "I'd love to draw a {0}",
            "Great! I'll draw a {0}"
        ]
        pick = random.choice(confirmations)
        self.tts.say(pick.format(selection))

    def chat(self, script):
        topic = self.dialog.loadTopicContent(script)
        self.dialog.activateTopic(topic)
        self.dialog.subscribe(self.APP_ID)
        return topic

    def stop_chat(self, topic, really=False):
        if really:
            self.dialog.unsubscribe(self.APP_ID)
            self.dialog.deactivateTopic(topic)
            self.dialog.unloadTopic(topic)
        return True


    @qi.nobind
    def load_drawing_specs(self):
        self.logger.info("Loading drawing specifications.")
        specs, failed = self.loaders[const.CTYPE_ABSOLUTE].load('shapes.json')
        self.drawing_specs.update(specs)

    @qi.nobind
    def set_initial_pose(self):
        self.logger.info("Setting initial pose for motion sequence.")

        # set exact starting position + joint stiffness
        self.almotion.wakeUp()
        self.almotion.setStiffnesses(const.CHAIN_BODY, 1.0)
        self.almotion.setStiffnesses(const.CHAIN_ARMS, 0.0)
        self.posture.goToPosture(const.POSE_STAND, 0.5)
        self.almotion.setStiffnesses(const.CHAIN_ARMS, 0.0)
        self.almotion.setStiffnesses(const.CHAIN_HEAD, 0.0)

        # disable breathing movements
        breath_future = prep.async_disable_breathing(
            (const.CHAIN_ARMS, const.CHAIN_LEGS), self.almotion)

        # enable control of the left arm
        prep.enable_left_arm_control(self.almotion)

        # wait for breathing to be disabled, then return
        breath_future.wait()
        return True

    @qi.bind(returnType=qi.Void, paramsType=[])
    def stop(self):
        """Stop the service."""
        self.ssm.stopServices()
        # self.ssm_scope.close_scope()
        self.logger.info("SIMDrawingDemo stopped by request.")
        self.qiapp.stop()

    @qi.nobind
    def on_stop(self):
        """Cleanup (add yours if needed)"""
        self.logger.info("SIMDrawingDemo finished.")

    @qi.nobind
    def timer(self, seconds):
        timer = qi.Promise()
        qi.async(functools.partial(timer.setValue, True), delay=int(seconds*1000000))
        return timer.future()


class DrawingDemoException(Exception):

    def __init__(self, message):
        self.message = message


####################
# Setup and Run
####################


if __name__ == "__main__":
    stk.runner.run_activity(SIMDrawingDemo)
