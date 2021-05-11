__version__ = "0.0.0"
__author__ = 'ancient-sentinel'

import qi
import stk.runner
import stk.events
import stk.services
import stk.logging

from loaders.absolute_specs import AbsoluteJsonSpecLoader

import simyan.app.scripts.simutils.motion.preparation as prep
from simyan.app.scripts.simutils.motion.absolute import *
from simyan.app.scripts.simyan import SIMServiceManager
from simyan.app.scripts.simutils.service import ServiceScope


class SIMDrawingExample(object):
    """A SIMYAN drawing example."""
    APP_ID = "org.uccs.simyan.SIMDrawingExample"

    def __init__(self, qiapp):
        # generic activity boilerplate
        self.qiapp = qiapp
        self.events = stk.events.EventHelper(qiapp.session)
        self.s = stk.services.ServiceCache(qiapp.session)
        self.logger = stk.logging.get_logger(qiapp.session, self.APP_ID)

        self.ssm_scope = ServiceScope(qiapp, SIMServiceManager)
        self.ssm_scope.create_scope()

        self.ssm = self.s.SIMServiceManager
        self.loader = AbsoluteJsonSpecLoader()

    def on_start(self):
        try:
            self.ssm.startServices()
            motion = self.s.SIMMotion

            shapes, failed = self.loader.load('shapes.json')
            triangle = shapes['triangle']

            self.logger.info('Creating absolute motion sequence context')
            context = AbsoluteSequenceContext(self.APP_ID, lambda: self.set_initial_pose, extensive_validation=False)

            self.logger.info('Registering sequence context')
            success = context.register(motion)
            self.logger.info('Registered: {0}'.format(success))

            self.logger.info('Executing sequence')
            context.execute_sequence(triangle.sequences[0], motion)
        except Exception as e:
            self.logger.info("Error: {0}".format(e.message))
        finally:
            self.stop()

    @qi.nobind
    def set_initial_pose(self):
        almotion = self.s.ALMotion
        alposture = self.s.ALRobotPosture

        # set exact starting position + joint stiffness
        almotion.wakeUp()
        almotion.setStiffnesses(const.CHAIN_BODY, 1.0)
        almotion.setStiffnesses(const.CHAIN_ARMS, 0.0)
        alposture.goToPosture("Stand", 0.5)
        almotion.setStiffnesses(const.CHAIN_ARMS, 0.0)
        almotion.setStiffnesses(const.CHAIN_HEAD, 0.0)

        # disable breathing movements
        breath_future = prep.async_disable_breathing(
            (const.CHAIN_ARMS, const.CHAIN_LEGS), almotion)

        # enable control of the left arm
        prep.enable_left_arm_control(almotion)

        # wait for breathing to be disabled, then return
        breath_future.wait()
        return True

    @qi.bind(returnType=qi.Void, paramsType=[])
    def stop(self):
        """Stop the service."""
        self.ssm.stopServices()
        self.ssm_scope.close_scope()
        self.logger.info("SIMDrawingExample stopped by request.")
        self.qiapp.stop()

    @qi.nobind
    def on_stop(self):
        """Cleanup (add yours if needed)"""
        self.logger.info("SIMDrawingExample finished.")


####################
# Setup and Run
####################


if __name__ == "__main__":
    stk.runner.run_activity(SIMDrawingExample)
