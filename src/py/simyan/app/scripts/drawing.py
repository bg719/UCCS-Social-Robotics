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
from simutils.service import ServiceScope
from simyan import SIMServiceManager


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

        self.ssm_scope = ServiceScope(qiapp, SIMServiceManager)
        self.ssm_scope.create_scope(dev=True)
        self.ssm = self.s.SIMServiceManager

        self.spec_loaders = []
        self.drawing_specs = {}

    def on_start(self):
        try:
            # self.ssm.startServices()

            with open('shapes.json', 'r') as outfile:
                data = outfile.read()
            shapes = json.loads(data)

            motion = self.s.ALMotion
            posture = self.s.ALRobotPosture

            def initial_pose():
                # initial position
                print('waking')
                motion.wakeUp()
                motion.setStiffnesses("Body", 1.0)
                motion.setStiffnesses("LArm", 0.0)
                motion.setStiffnesses("RArm", 0.0)
                posture.goToPosture("Stand", 0.5)
                motion.setStiffnesses("RArm", 0.0)
                motion.setStiffnesses("LArm", 0.0)
                motion.setStiffnesses("Head", 0.0)

                # set breathing
                print('turning off breathing')
                set_breathing(False, motion)
                time.sleep(2)

                # move the left arm
                print('enabling effector')
                motion.wbEnableEffectorControl(const.EF_LEFT_ARM, True)
                motion.setStiffnesses(const.EF_LEFT_ARM, 1.0)
                return True

            self.logger.info('Creating absolute motion sequence context')
            context = AbsoluteSequenceContext(self.APP_ID, initial_pose, extensive_validation=False)
            self.logger.info('Registering sequence context')
            success = context.register(self.s.SIMMotion)
            self.logger.info('Registered: {0}'.format(success))

            self.logger.info('Creating sequence')
            triangle = shapes['triangle']['leftHand']
            seq = AbsoluteSequence(
                triangle['effector'],
                triangle['frame'],
                triangle['axisMask']
            )
            duration = triangle['duration']

            for kf in triangle['keyframes']:
                added = seq.next_position_keyframe(kf['point'], duration)
                print('Added: {0} - {1}'.format(added, kf))

            self.logger.info('Executing sequence')
            self.logger.info(self.s.SIMMotion)
            context.execute_sequence(seq, self.s.SIMMotion)
        except Exception as e:
            self.logger.info(e.message)
        finally:
            self.stop()

    @qi.bind(returnType=qi.Void, paramsType=[])
    def stop(self):
        """Stop the service."""
        self.ssm.stopServices()
        self.ssm_scope.close_scope()
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
