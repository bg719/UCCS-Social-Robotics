__version__ = "0.0.0"
__author__ = 'ancient-sentinel'

import qi
import stk.runner
import stk.events
import stk.services
import stk.logging
import functools
import random

from loaders.absolute_specs import AbsoluteJsonSpecLoader

import simyan.app.scripts.simutils.motion.preparation as prep
from simyan.app.scripts.simutils.motion.absolute import *
from simyan.app.scripts.simyan import SIMServiceManager
from simyan.app.scripts.simutils.service import ServiceScope
from simyan.app.scripts.simutils.speech import SpeechEvent
from simyan.app.scripts.simutils.timer import async_timer


class SIMDrawingDemo(object):
    """A SIMYAN drawing activity demo."""
    APP_ID = "org.uccs.simyan.SIMDrawingDemo"

    def __init__(self, qiapp):
        # generic STK activity boilerplate
        self.qiapp = qiapp
        self.events = stk.events.EventHelper(qiapp.session)
        self.s = stk.services.ServiceCache(qiapp.session)
        self.logger = stk.logging.get_logger(qiapp.session, self.APP_ID)

        # NOTE: The service manager and it's services currently must
        # run on the same machine as the demo activity. Resolution of
        # returned qi.Objects from some service methods fails if they
        # are not both being hosted on the same machine. The workaround
        # here is to load the SIMYAN service manager as part of the demo
        # startup.
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
        """
        Performs additional initializations and starts the demo.
        """
        try:
            # Start the SIMYAN services. If the SIMServiceManager's
            # scope is not managed by this activity, it is still safe
            # to call this method in order to ensure that all services
            # are running and available.
            self.ssm.startServices()
            self.speech = self.s.SIMSpeech
            self.motion = self.s.SIMMotion

            # Load the drawing specifications
            self.load_drawing_specs()
            self.logger.info("Drawing Specs: {0}".format(self.drawing_specs.keys()))

            # Start the demo
            self.start_demo()
        except Exception as e:
            self.logger.info("Error starting demo: {0}".format(e.message))
        finally:
            self.stop()

    def start_demo(self):
        """Starts the drawing demo and then begins the main activity."""
        try:
            # First, listen for the trigger phrase
            self.logger.info("Starting demo.")
            self.listen_for_trigger()

            # Then, explain the activity to the person
            self.logger.info("Explaining activity...")
            self.explain_activity()

            # Begin the main activity
            self.logger.info("Beginning main drawing activity...")
            self.main_activity()
        except Exception as e:
            self.logger.error("Encountered error: {0}".format(e.message))
            return

    def listen_for_trigger(self):
        # Define a function callback for the trigger phrase speech event
        def heard(phrase):
            self.logger.info('Heard: {0}'.format(phrase))

        # Create the speech event for the trigger phrase
        heard_trigger = SpeechEvent("let's draw something", heard)

        # Attempt to register the speech event with the SIMSpeech service
        if not heard_trigger.register(self.speech):
            raise DrawingDemoException(
                "Could not register speech event with SIMYAN speech service.")

        # Wait for the trigger phrase to be heard, but only allow up
        # to a 30 second wait
        self.logger.info("Listening for trigger phrase...")
        heard_trigger.wait(30)

    def explain_activity(self):
        """Verbally explain the activity."""
        self.tts.say("Awesome! I love drawing!")

        # Get the names of the things the robot can draw
        objects = self.drawing_specs.keys()
        objects = ", ".join(objects[:-1]) + ", or {0}".format(objects[-1])

        # Tell the person what can be drawn
        self.tts.say("I can draw a {0}".format(objects))

    def main_activity(self):
        """Executes the main drawing demo activity."""
        while not self.quit:
            # Prompt the person to select something to draw
            drawing = self.select_drawing()

            # Ensure the robot has a specification to draw the requested object
            if drawing not in self.drawing_specs:
                self.invalid_selection(drawing)
                continue

            # Verbally confirm the selection
            self.confirm_selection(drawing)

            # Draw the picture
            self.draw(self.drawing_specs[drawing])

            # Express an emotion
            self.emote()

            # Prepare to repeat the activity
            self.prepare_repeat()

    def select_drawing(self, reprompt=0):
        """Prompts the user to select a drawing and captures the user's response."""
        if reprompt > self.max_reprompts:
            raise DrawingDemoException(
                'Maximum number of drawing selection re-prompts reached.')

        # Due to Python 2.7 scoping, we have to use a bit of a hack to
        # save the selection from the callback function to a variable in
        # the outer scope. Declaring a class with a class variable provides
        # a means to do so.
        class Nonlocal:
            selection = None

        # Define the callback to capture the person's selection
        def set_selection(phrase):
            Nonlocal.selection = phrase

        # Create the speech event to hear the selection. We pass the names
        # of the objects the robot knows how to draw as the vocabulary the
        # speech service should be listening for.
        hear_selection = SpeechEvent(self.drawing_specs.keys(), set_selection)

        self.tts.say("What would you like me to draw?")

        # Register the speech event
        if not hear_selection.register(self.speech):
            raise DrawingDemoException(
                "Could not register speech event with SIMYAN speech service.")

        # Wait at most 10 seconds for a response
        hear_selection.wait(10)

        # We have to wait briefly for the callback to be invoked and the
        # selection to be set
        timer = async_timer(0.1)
        timer.wait()

        # Confirm we have a selection
        if not Nonlocal.selection:
            return self.select_drawing(reprompt + 1)

        # Return the selection
        return Nonlocal.selection

    def invalid_selection(self, selection):
        """Handles an invalid selection."""
        self.tts.say("I'm sorry, but I don't know how to draw a {0}".format(selection))

    def draw(self, spec):
        """Draws an image based on its specification."""

        # Grab the sequence whose effector matches the arm currently being used
        sequence = next(s for s in spec.sequences if s.effector == self.arm)

        if not sequence:
            raise DrawingDemoException(
                "No sequence for the current arm in drawing specification: {0}".format(spec.name))

        # Currently, only absolute sequences are supported, but custom motion sequences
        # can be implemented using tools in the simutils.motion package.
        if isinstance(sequence, AbsoluteSequence):
            # Create a sequence context to register with the SIMMotion service
            context = AbsoluteSequenceContext(self.APP_ID, lambda: self.set_initial_pose(), extensive_validation=False)
        else:
            raise DrawingDemoException(
                "Unexpected sequence type: {0}".format(type(sequence)))

        # Attempt to register the context
        if not context.register(self.motion):
            raise DrawingDemoException(
                "Failed to register {0} context with the motion service.".format(type(context)))

        # Setup a delayed action which will have the robot speak the description of
        # the drawing as it's about to begin actually drawing it
        qi.async(functools.partial(lambda d: self.tts.say(d), spec.description), delay=9000000)

        # Execute the motion sequence
        result = context.execute_sequence(sequence, self.motion)

        # Re-enable breathing motions which were paused by set_initial_pose()
        breath_future = prep.async_enable_breathing((const.CHAIN_ARMS, const.CHAIN_LEGS), self.almotion)

        # Unregister the motion sequence context
        context.unregister(self.motion)

        # Wait for breathing to be fully re-enabled
        breath_future.wait()

        if not result.success:
            raise DrawingDemoException(
                "Error executing motion sequence. Status: {0} - Message: {1}".format(result.status, result.message))

    def emote(self):
        """Express an emotion."""
        emotes = [
            "That was fun!",
            "I enjoyed that! Maybe we should do it again!",
            "Wow! I love drawing!",
            "We should do that again!",
            "I'm having so much fun!"
        ]
        pick = random.choice(emotes)
        self.tts.say(pick)

    def prepare_repeat(self):
        """Prepare to repeat the main activity."""
        self.tts.say("Would you like me to draw again?")

        class Nonlocal:
            selection = None

        def set_selection(phrase):
            Nonlocal.selection = phrase

        # Listen for both affirmative and negative answers
        affirmative = ('yes', 'yeah', 'sure', 'ok')
        negative = ('no', 'nope')
        hear_selection = SpeechEvent(affirmative + negative, set_selection)

        if not hear_selection.register(self.speech):
            raise DrawingDemoException(
                "Could not register speech event with SIMYAN speech service.")

        hear_selection.wait(10)

        timer = async_timer(0.1)
        timer.wait()

        # If we didn't get an affirmative to continue, then quit
        if Nonlocal.selection not in affirmative:
            self.tts.say("Ok, we'll stop drawing for now.")
            self.quit = True
            return

        self.tts.say("Awesome! I'll give you a couple seconds to wipe the board for me.")

        # Give the person a chance to wipe the board
        timer = async_timer(self.seconds_to_clean_board)
        timer.wait()

        self.tts.say("Thanks! Let's draw some more!")

    def confirm_selection(self, selection):
        """Verbally confirms a drawing selection."""
        confirmations = [
            "Ok, I'll draw a {0}",
            "I'd love to draw a {0}",
            "Great! I'll draw a {0}"
        ]
        pick = random.choice(confirmations)
        self.tts.say(pick.format(selection))

    @qi.nobind
    def load_drawing_specs(self):
        """Loads the available drawing specifications."""
        self.logger.info("Loading drawing specifications.")

        # For now we just load the shapes.json file
        specs, failed = self.loaders[const.CTYPE_ABSOLUTE].load('shapes.json')
        self.drawing_specs.update(specs)

    @qi.nobind
    def set_initial_pose(self):
        """
        Sets the initial pose for a drawing sequence. This method is automatically
        invoked by the motion sequence handler from the SIMMotion service.

        :return: True when the position is fully set.
        """
        self.logger.info("Setting initial pose for motion sequence.")

        # Set exact starting position + joint stiffness
        self.almotion.wakeUp()
        self.almotion.setStiffnesses(const.CHAIN_BODY, 1.0)
        self.almotion.setStiffnesses(const.CHAIN_ARMS, 0.0)
        self.posture.goToPosture(const.POSE_STAND, 0.5)
        self.almotion.setStiffnesses(const.CHAIN_ARMS, 0.0)
        self.almotion.setStiffnesses(const.CHAIN_HEAD, 0.0)

        # Disable breathing movements
        breath_future = prep.async_disable_breathing(
            (const.CHAIN_ARMS, const.CHAIN_LEGS), self.almotion)

        # Enable control of the left arm
        prep.enable_left_arm_control(self.almotion)

        # Wait for breathing to be disabled, then return
        breath_future.wait()
        return True

    @qi.bind(returnType=qi.Void, paramsType=[])
    def stop(self):
        """Stop the service."""
        self.ssm.stopServices()

        # Remove this call if the SIMServiceManager is not managed
        # by this application
        self.ssm_scope.close_scope()

        self.logger.info("SIMDrawingDemo stopped by request.")
        self.qiapp.stop()

    @qi.nobind
    def on_stop(self):
        """Cleanup (add yours if needed)"""
        self.logger.info("SIMDrawingDemo finished.")


class DrawingDemoException(Exception):
    """An exception raised due to a drawing demo error."""

    def __init__(self, message):
        """
        Initializes a new drawing demo exception.

        :param message: (str) The message describing the error.
        """
        self.message = message


####################
# Setup and Run
####################


if __name__ == "__main__":
    stk.runner.run_activity(SIMDrawingDemo)
