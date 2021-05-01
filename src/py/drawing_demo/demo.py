__version__ = "0.0.0"
__author__ = 'ancient-sentinel'

import qi
import stk.runner
import stk.events
import stk.services
import stk.logging

from loaders.absolute_specs import AbsoluteJsonSpecLoader

# import simutils.motion.preparation as prep
# import simutils.motion.constants as const
# from simutils.motion.absolute import *

import simyan.app.scripts.simutils.motion.preparation as prep
from simyan.app.scripts.simutils.motion.absolute import *
from simyan.app.scripts.simyan import SIMServiceManager
from simyan.app.scripts.simutils.service import ServiceScope
from simyan.app.scripts.simutils.speech import SpeechEvent


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

        # Standard services
        self.almotion = self.s.ALMotion
        self.posture = self.s.ALRobotPosture

        # SIMYAN services
        self.ssm = self.s.SIMServiceManager
        self.speech = self.s.SIMSpeech
        self.motion = self.s.SIMMotion

        # Demo state
        self.drawing_specs = {}
        self.loaders = {
            const.CTYPE_ABSOLUTE: AbsoluteJsonSpecLoader()
        }
        self.quit = False
        self.max_reprompts = 3
        self.arm = const.EF_LEFT_ARM

    def on_start(self):
        try:
            self.ssm.startServices()

            # shapes, failed = self.loader.load('shapes.json')
            # triangle = shapes['triangle']
            #
            # self.logger.info('Creating absolute motion sequence context')
            # context = AbsoluteSequenceContext(self.APP_ID, lambda: self.set_initial_pose, extensive_validation=False)
            #
            # self.logger.info('Registering sequence context')
            # success = context.register(self.motion)
            # self.logger.info('Registered: {0}'.format(success))
            #
            # self.logger.info('Executing sequence')
            # context.execute_sequence(triangle.sequences[0], self.motion)

            self.start_demo()
        except Exception as e:
            self.logger.info("Error starting demo: {0}".format(e.message))
        finally:
            self.stop()

    def start_demo(self):
        self.greet_person()
        self.explain_activity()

        try:
            self.main_activity()
        except Exception as e:
            self.logger.error("Encountered error: {0}".format(e.message))

    def greet_person(self):
        pass

    def explain_activity(self):
        pass

    def main_activity(self):
        while not self.quit:
            drawing = self.select_drawing()

            if drawing not in self.drawing_specs:
                self.invalid_selection()
                continue

            self.draw(self.drawing_specs[drawing])
            self.emote()
            self.prepare_repeat()

    def select_drawing(self, reprompt=0):
        if reprompt > self.max_reprompts:
            raise DrawingDemoException('Maximum number of drawing selection re-prompts reached.')

        selection = None

        def set_selection(phrase):
            selection = phrase

        hear_selection = SpeechEvent(self.drawing_specs.keys(), set_selection)

        # todo: prompt person to pick shape

        if not hear_selection.register(self.speech):
            raise DrawingDemoException("Could not register speech event with SIMYAN speech service.")

        hear_selection.wait(5)

        if not selection:
            return self.select_drawing(reprompt + 1)

        return selection

    def invalid_selection(self):
        pass

    def draw(self, spec):
        sequence = next(s for s in spec.sequences if s.effector == self.arm)

        if not sequence:
            raise DrawingDemoException(
                "No sequence for the current arm in drawing specification: {0}".format(spec.name))

        if isinstance(sequence, AbsoluteSequence):
            context = AbsoluteSequenceContext(self.APP_ID, lambda: self.set_initial_pose, extensive_validation=False)
        else:
            raise DrawingDemoException("Unexpected sequence type: {0}".format(type(sequence)))

        if not context.register(self.motion):
            raise DrawingDemoException(
                "Failed to register {0} context with the motion service.".format(type(context)))

        result = context.execute_sequence(sequence, self.motion)

        if not result.success:
            raise DrawingDemoException(
                "Error executing motion sequence. Status: {0} - Message: {1}".format(result.status, result.message))

    def emote(self):
        pass

    def prepare_repeat(self):
        pass

    @qi.nobind
    def load_drawing_specs(self):
        self.logger.info("Loading drawing specifications.")
        specs, failed = self.loaders[const.CTYPE_ABSOLUTE].load('shapes.json')
        self.drawing_specs.update(specs)

    @qi.nobind
    def set_initial_pose(self):
        # set exact starting position + joint stiffness
        self.almotion.wakeUp()
        self.almotion.setStiffnesses(const.CHAIN_BODY, 1.0)
        self.almotion.setStiffnesses(const.CHAIN_ARMS, 0.0)
        self.posture.goToPosture("Stand", 0.5)
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


class DrawingDemoException(Exception):

    def __init__(self, message):
        self.message = message


####################
# Setup and Run
####################


if __name__ == "__main__":
    stk.runner.run_activity(SIMDrawingDemo)
