__version__ = "0.0.0"
__author__ = 'ancient-sentinel'

import qi
import json
import time
import stk.runner
import stk.events
import stk.services
import stk.logging
from simutils.motion.absolute import *


def set_breathing(enabled, motion_proxy):
    """
    Turn robot breathing animation on/off
    """
    if type(enabled) is bool:
        motion_proxy.setBreathEnabled("LArm", enabled)
        motion_proxy.setBreathEnabled("RArm", enabled)
        motion_proxy.setBreathEnabled("Legs", enabled)
    else:
        raise TypeError("Argument must be boolean")


class SIMDrawingDemo(object):
    """A SIMYAN drawing activity demo."""
    APP_ID = "org.uccs.simyan.SIMDrawingDemo"

    def __init__(self, qiapp):
        # generic activity boilerplate
        self.qiapp = qiapp
        self.events = stk.events.EventHelper(qiapp.session)
        self.s = stk.services.ServiceCache(qiapp.session)
        self.logger = stk.logging.get_logger(qiapp.session, self.APP_ID)

        self.spec_loaders = []
        self.drawing_specs = {}

    def on_start(self):
        try:
            with open('shapes.json', 'r') as outfile:
                data = outfile.read()
            shapes = json.loads(data)

            motion = self.s.ALMotion
            posture = self.s.ALRobotPosture

            def initial_pose():
                # initial position
                motion.wakeUp()
                motion.setStiffnesses("Body", 1.0)
                motion.setStiffnesses("LArm", 0.0)
                motion.setStiffnesses("RArm", 0.0)
                posture.goToPosture("Stand", 0.5)
                motion.setStiffnesses("RArm", 0.0)
                motion.setStiffnesses("LArm", 0.0)
                motion.setStiffnesses("Head", 0.0)

                # set breathing
                set_breathing(False, motion)
                time.sleep(2)

                # move the left arm
                motion.wbEnableEffectorControl(const.EF_LEFT_ARM, True)
                motion.setStiffnesses(const.EF_LEFT_ARM, 1.0)
                return True

            context = AbsoluteSequenceContext(self.qiapp.session, self.APP_ID, initial_pose, extensive_validation=False)
            context.register()

            triangle = shapes['triangle']
            seq = AbsoluteSequence(
                triangle['leftHand']['effectors'],
                triangle['frame'],
                triangle['axisMask']
            )
            duration = triangle['duration']

            triangle = triangle['leftHand']
            for kf in triangle['keyframes']:
                seq.next_position_keyframe(kf['point'], duration)

            context.execute_sequence(seq)
        finally:
            self.stop()



    @qi.bind(returnType=qi.Void, paramsType=[])
    def stop(self):
        """Stop the service."""
        self.logger.info("SIMDrawingDemo stopped by request.")
        self.qiapp.stop()

    @qi.nobind
    def on_stop(self):
        """Cleanup (add yours if needed)"""
        self.logger.info("SIMDrawingDemo finished.")


####################
# Setup and Run
####################


if __name__ == "__main__":
    stk.runner.run_activity(SIMDrawingDemo)
