__version__ = "0.0.0"
__author__ = 'ancient-sentinel'

import qi
import functools


def async_timer(seconds):
    timer = qi.Promise()
    qi.async(functools.partial(timer.setValue, True), delay=int(seconds * 1000000))
    return timer.future()
