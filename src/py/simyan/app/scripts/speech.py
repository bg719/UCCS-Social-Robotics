__version__ = "0.0.0"

import qi

import stk.runner
import stk.events
import stk.services
import stk.logging
import threading


class SIMSpeech(object):
    """A SIMYAN NAOqi service providing supplemental speech services."""
    APP_ID = "org.uccs.simyan.SIMSpeech"

    def __init__(self, qiapp):
        self.qiapp = qiapp
        self.events = stk.events.EventHelper(qiapp.session)
        self.s = stk.services.ServiceCache(qiapp.session)
        self.logger = stk.logging.get_logger(qiapp.session, self.APP_ID)

        self.asr = self.s.ALSpeechRecognition
        self.memory = self.s.ALMemory
        self.cid = None
        self.language = 'English'
        self.vocab = {}
        self.lock = threading.Lock()

    @qi.bind(returnType=qi.Object, paramsType=[qi.List(qi.String), qi.Float])
    def subscribe(self, phrases, minimum_confidence):
        if len(phrases) == 0 or not (0 < minimum_confidence <= 1):
            return _SubscriptionInfo.error()

        info = _SubscriptionInfo(phrases, minimum_confidence)

        self.lock.acquire()
        for phrase in phrases:
            if phrase in self.vocab:
                self.vocab[phrase].append(info)
            else:
                self.vocab[phrase] = [info]

        self._update_vocabulary()
        self.lock.release()
        return info.future()

    @qi.bind(returnType=qi.Void, paramsType=[])
    def stop(self):
        """Stop the service."""
        self.logger.info("SIMSpeech stopped by request.")
        self.qiapp.stop()

    @qi.nobind
    def on_stop(self):
        """Cleanup (add yours if needed)"""
        for subscriber in set().union(self.vocab.values()):
            subscriber.promise.setCanceled()

        self._unregister()
        self.logger.info("SIMSpeech finished.")

    @qi.nobind
    def on_word_recognized(self, eventargs):
        # self.logger.info(eventargs)
        phrase = eventargs[0]  # if word spotting is set True, need eventargs[0][6:-6]
        confidence = eventargs[1]

        self.lock.acquire()
        self.asr.pause(True)

        if phrase not in self.vocab:
            self.asr.pause(False)
            self.lock.release()
            return

        pending_removal = []
        for subscriber in self.vocab[phrase]:
            if not subscriber.is_canceled() \
                    and subscriber.set_value(phrase, confidence):
                pending_removal.append(subscriber)

        self._unsubscribe(pending_removal, pause=False)

        self.asr.pause(False)
        self.lock.release()

    @qi.nobind
    def _register(self):
        self.cid = self.events.subscribe(
            "WordRecognized", "SIMSpeech", self.on_word_recognized)
        self.asr.pause(True)
        self.asr.setLanguage(self.language)
        self.asr.pause(False)
        self.asr.subscribe(self.APP_ID)

    @qi.nobind
    def _unregister(self):
        if self.cid is not None:
            self.events.clear()
            self.cid = None
            self.asr.unsubscribe(self.APP_ID)

    @qi.nobind
    def _unsubscribe(self, subscribers, pause=True):
        if len(subscribers) == 0:
            return

        for info in subscribers:
            for phrase in info.phrases:
                if phrase in self.vocab:
                    subscribed = self.vocab[phrase]
                    subscribed.remove(info)
                    if len(subscribed) == 0:
                        self.vocab.pop(phrase)
        self._update_vocabulary(pause)

    @qi.nobind
    def _update_vocabulary(self, pause=True):
        if self.cid is None:
            self._register()
        if any(self.vocab):
            if pause:
                self.asr.pause(True)

            self.asr.setVocabulary(self.vocab.keys(), False)

            if pause:
                self.asr.pause(False)


class _SubscriptionInfo:

    def __init__(self, phrases, minimum_confidence):
        self.promise = qi.Promise()
        self.phrases = phrases
        self.minimum_confidence = minimum_confidence
        self.value_set = False

    def future(self):
        return _SubscriptionFuture(self.promise.future())

    def is_canceled(self):
        if self.promise.isCancelRequested():
            self.promise.setCanceled()
            return True
        return False

    def set_value(self, phrase, confidence):
        if not self.value_set and confidence >= self.minimum_confidence:
            self.promise.setValue((phrase, confidence))
            self.value_set = True
            return True
        else:
            return False

    @staticmethod
    def error():
        instance = _SubscriptionInfo(())
        instance.promise.setError('Word list cannot be empty.')
        return instance.promise.future()


class _SubscriptionFuture:

    def __init__(self, future):
        self.future = future


####################
# Setup and Run
####################


if __name__ == "__main__":
    stk.runner.run_service(SIMSpeech)
