__version__ = "0.0.0"
__author__ = 'ancient-sentinel'

import qi
import constants as const

from functools import partial


def disable_head_control(motion_proxy, stiffness=None):
    """
    Disables control of the head effector and sets the final joint
    stiffness.

    :param motion_proxy: (ALMotion) The motion proxy or service.
    :param stiffness: (float) A value between 0 and 1 to which the
        joint stiffness will be set, or None to skip setting the
        stiffness.
    """
    return _set_effector_control(const.EF_HEAD, False, motion_proxy, stiffness)


def disable_left_arm_control(motion_proxy, stiffness=None):
    """
    Disables control of the left arm effector and sets the final joint
    stiffness.

    :param motion_proxy: (ALMotion) The motion proxy or service.
    :param stiffness: (float) A value between 0 and 1 to which the
        joint stiffness will be set, or None to skip setting the
        stiffness.
    """
    return _set_effector_control(const.EF_LEFT_ARM, False, motion_proxy, stiffness)


def disable_right_arm_control(motion_proxy, stiffness=None):
    """
    Disables control of the right hand effector and sets the final joint
    stiffness.

    :param motion_proxy: (ALMotion) The motion proxy or service.
    :param stiffness: (float) A value between 0 and 1 to which the
        joint stiffness will be set, or None to skip setting the
        stiffness.
    """
    return _set_effector_control(const.EF_RIGHT_ARM, False, motion_proxy, stiffness)


def enable_head_control(motion_proxy, stiffness=1.0):
    """
    Enables control of the head effector and sets the initial joint
    stiffness.

    :param motion_proxy: (ALMotion) The motion proxy or service.
    :param stiffness: (float) A value between 0 and 1 to which the
        joint stiffness will be set, or None to skip setting the
        stiffness.
    """
    return _set_effector_control(const.EF_HEAD, True, motion_proxy, stiffness)


def enable_left_arm_control(motion_proxy, stiffness=1.0):
    """
    Enables control of the left arm effector and sets the initial joint
    stiffness.

    :param motion_proxy: (ALMotion) The motion proxy or service.
    :param stiffness: (float) A value between 0 and 1 to which the
        joint stiffness will be set, or None to skip setting the
        stiffness.
    """
    return _set_effector_control(const.EF_LEFT_ARM, True, motion_proxy, stiffness)


def enable_right_arm_control(motion_proxy, stiffness=1.0):
    """
    Enables control of the right arm effector and sets the initial joint
    stiffness.

    :param motion_proxy: (ALMotion) The motion proxy or service.
    :param stiffness: (float) A value between 0 and 1 to which the
        joint stiffness will be set, or None to skip setting the
        stiffness.
    """
    return _set_effector_control(const.EF_RIGHT_ARM, True, motion_proxy, stiffness)


def async_disable_breathing(effectors, motion_proxy):
    """
    Disables the "breathing" motions for the specified effectors, then
    delays for 2 seconds to wait for completion.

    :param effectors: (Iterable[str]) The effectors.
    :param motion_proxy: (ALMotion) The motion proxy or service.
    :return: (qi.Future) A future that can be waited upon to
        ensure the action has completed.
    """
    promise = qi.Promise()
    disable_breathing(effectors, motion_proxy)
    qi.async(partial(promise.setValue, None), delay=2000)
    return promise.future()


def async_enable_breathing(effectors, motion_proxy):
    """
    Enables the "breathing" motions for the specified effectors, then
    delays for 2 seconds to wait for completion.

    :param effectors: (Iterable[str]) The effectors.
    :param motion_proxy: (ALMotion) The motion proxy or service.
    :return: (qi.Future) A future that can be waited upon to
        ensure the action has completed.
    """
    promise = qi.Promise()
    enable_breathing(effectors, motion_proxy)
    qi.async(partial(promise.setValue, None), delay=2000)
    return promise.future()


def disable_breathing(effectors, motion_proxy):
    """
    Disables the "breathing" motions for the specified effectors.

    WARNING: May take up to 2 seconds to take effect. Recommend using
    the async method and waiting on the future it returns.

    :param effectors: (List[str]) The effectors.
    :param motion_proxy: (ALMotion) The motion proxy or service.
    """
    effectors = set(effectors)
    if not all(effector in const.EFFECTORS for effector in effectors):
        raise ValueError("Invalid effector(s) in set.")

    for effector in effectors:
        motion_proxy.setBreathing(effector, True)


def enable_breathing(effectors, motion_proxy):
    """
    Enables the "breathing" motions for the specified effectors.

    WARNING: May take up to 2 seconds to take effect. Recommend using
    the async method and waiting on the future it returns.

    :param effectors: (List[str]) The effectors.
    :param motion_proxy: (ALMotion) The motion proxy or service.
    """
    effectors = set(effectors)
    if not all(effector in const.EFFECTORS for effector in effectors):
        raise ValueError("Invalid effector(s) in set.")

    for effector in effectors:
        motion_proxy.setBreathing(effector, False)


def _set_effector_control(effector, enabled, motion_proxy, stiffness):
    """
    Sets the effector control enabled state and the associated joint
    stiffness.

    :param effector: (str) The effector.
        Only valid for the arms and head.
    :param enabled: (bool) The enabled state.
    :param motion_proxy: (ALMotion) The motion proxy or service.
    :param stiffness: (float) A value between 0 and 1 to which the
        joint stiffness will be set, or None to skip setting the
        stiffness.
    :return:
    """
    if not (0 <= stiffness <= 1 or stiffness is None):
        raise ValueError(
            "Initial stiffness must be a value between 0 and 1 or None.")
    if effector not in (const.EF_HEAD, const.EF_LEFT_ARM, const.EF_RIGHT_ARM):
        raise ValueError("Invalid effector. Only supported by arms and head.")
    motion_proxy.wbEnableEffectorControl(effector, enabled)
    if stiffness:
        motion_proxy.setStiffnesses(effector, stiffness)