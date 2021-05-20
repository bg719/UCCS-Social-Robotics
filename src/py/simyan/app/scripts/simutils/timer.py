__version__ = "0.0.0"
__author__ = 'ancient-sentinel'

import qi
import functools


def async_timer(seconds):
    """
    An asynchronous timer which finishes after the specified number of
    seconds.

    :param seconds: (float) The timer duration in seconds.
    :return: (qi.Future) A future which will finish after the
        specified number of seconds have elapsed.
    """
    timer = qi.Promise()
    qi.async(functools.partial(timer.setValue, True), delay=int(seconds * 1000000))
    return timer.future()
