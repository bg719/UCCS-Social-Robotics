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

    def __init__(self, qiapp, language='English'):
        self.qiapp = qiapp
        self.events = stk.events.EventHelper(qiapp.session)
        self.s = stk.services.ServiceCache(qiapp.session)
        self.logger = stk.logging.get_logger(qiapp.session, self.APP_ID)

        self.asr = self.s.ALSpeechRecognition
        self.memory = self.s.ALMemory
        self.cid = None
        self.language = language
        self.vocab = {}
        self.lock = threading.Lock()
        self.pending_removal = []

    @qi.bind(returnType=qi.Future, paramsType=[qi.List(qi.String)])
    def subscribe(self, words):
        if len(words) == 0:
            return _SubscriptionInfo.error()

        info = _SubscriptionInfo(words)

        self.lock.acquire()
        for word in words:
            if word in self.vocab:
                self.vocab[word].append(info)
            else:
                self.vocab[word] = [info]

        self._update_vocabulary()
        self.lock.release()

        return info.promise.future()

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

    @qi.nobind  # todo: verify this still works
    def on_word_recognized(self, eventargs):
        self.logger.info(eventargs)
        word = eventargs[0][6:-6]
        confidence = eventargs[1]

        self.lock.acquire()
        self.asr.pause(True)

        if word not in self.vocab:  # check might not be needed
            self.asr.pause(False)
            self.lock.release()
            return

        for subscriber in self.vocab[word]:
            self.pending_removal.append(subscriber)
            if not subscriber.is_canceled():
                subscriber.set_value(word, confidence)

        self._unsubscribe(self.pending_removal, pause=False)

        self.asr.pause(False)
        self.lock.release()

    @qi.nobind
    def _register(self):
        self.cid = self.events.subscribe(
            "WordRecognized", "SIMSpeech", self.on_word_recognized)
        self.asr.pause(True)
        self.asr.setLanguage(self.language)
        self.asr.pause(False)

    @qi.nobind
    def _unregister(self):
        if self.cid is not None:
            self.events.disconnect("WordRecognized", self.cid)
            self.cid = None

    @qi.nobind
    def _unsubscribe(self, subscribers, pause=True):
        for info in subscribers:
            for word in info.words:
                subscribed = self.vocab[word]
                subscribed.remove(info)
                if len(subscribed) == 0:
                    self.vocab.pop(word)
        self._update_vocabulary(pause)

    @qi.nobind
    def _update_vocabulary(self, pause=True):
        if self.cid is None:
            self._register()
        if any(self.vocab):
            if pause:
                self.asr.pause(True)

            self.asr.setVocabulary(self.vocab.keys(), True)

            if pause:
                self.asr.pause(False)
        else:
            self._unregister()


class _SubscriptionInfo:

    def __init__(self, words):
        self.promise = qi.Promise()
        self.words = words
        self.value_set = False

    def is_canceled(self):
        if self.promise.isCancelRequested():
            self.promise.setCanceled()
            return True
        return False

    def set_value(self, word, confidence):
        if not self.value_set:
            self.promise.setValue((word, confidence))
            self.value_set = True

    @staticmethod
    def error():
        instance = _SubscriptionInfo(())
        instance.promise.setError('Word list cannot be empty.')
        return instance.promise.future()



####################
# Setup and Run
####################


if __name__ == "__main__":
    stk.runner.run_service(SIMSpeech)
