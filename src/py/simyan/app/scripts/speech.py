__version__ = "0.0.0"

import qi

import stk.runner
import stk.events
import stk.services
import stk.logging
import threading
import time

from simutils.speech import _SpeechSubscription


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
        self.id_count = 0
        self.language = language
        self.vocab = {}
        self.subscribers = {}
        self.lock = threading.Lock()
        self.pending_removal = []
        self.need_reset = []

    @qi.bind(returnType=qi.Object, paramsType=[qi.List(qi.String)])
    def subscribe(self, words):
        if len(words) == 0:
            return _SpeechSubscription.error()

        id = self.id_count
        self.id_count += 1
        info = SubscriptionInfo(id, words)
        info.reactivate.addCallback(self.reactivate)

        for word in words:
            if word in self.vocab:
                self.vocab[word].append(info)
            else:
                self.vocab[word] = [info]

        self.subscribers[id] = info
        self._update_vocabulary()
        return info.subscription

    @qi.bind(returnType=qi.Bool, paramsType=[qi.Int8])
    def unsubscribe(self, id):
        if id not in self.subscribers:
            return False
        # info = self.subscribers.pop(id)
        # for word in info.words:
        #     entry = self.vocab[word]
        #     entry.remove(info)
        #     if len(entry) == 0:
        #         self.vocab.pop(word)
        # self._update_vocabulary()
        self._unsubscribe([id])
        return True

    @qi.nobind
    def reactivate(self, future):
        self.lock.acquire()
        if future.hasValue():
            id, choice, promise = future.value()
            info = self.subscribers[id]
            last = info == self.pending_removal[-1]

            if choice:
                self.pending_removal.remove(info)
                self.need_reset.append((info, promise))
                # info.reset()
                # promise.setValue(True)

            if last:
                print('unsubscribing')
                print(self.pending_removal)
                self._unsubscribe((s.id for s in self.pending_removal))

                for i, p in self.need_reset:
                    i.reset()
                    p.setValue(True)
        self.lock.release()

    @qi.bind(returnType=qi.Void, paramsType=[])
    def stop(self):
        """Stop the service."""
        self.logger.info("SIMSpeech stopped by request.")
        self.qiapp.stop()

    @qi.nobind
    def on_stop(self):
        """Cleanup (add yours if needed)"""
        self._unregister()
        self.logger.info("SIMSpeech finished.")

    def on_word_recognized(self, eventargs):
        self.lock.acquire()
        self.logger.info(eventargs)

        self.asr.pause(True)

        word = eventargs[0][6:-6]
        confidence = eventargs[1]

        if word in self.vocab:
            for subscriber in self.vocab[word]:
                self.pending_removal.append(subscriber)
                subscriber.set_value(word, confidence)

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
    def _unsubscribe(self, ids, pause=True):
        for id in ids:
            info = self.subscribers.pop(id)
            for word in info.words:
                entry = self.vocab[word]
                entry.remove(info)
                if len(entry) == 0:
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


class SubscriptionInfo:

    def __init__(self, id, words):
        self.id = id
        self.promise = qi.Promise()
        self.words = words
        self.subscription = _SpeechSubscription(id)
        self.reactivate = self.subscription.reset(self.promise.future())
        self.value_set = False

    def reset(self):
        self.promise = qi.Promise()
        self.reactivate = self.subscription.reset(self.promise.future())
        self.value_set = False

    def set_value(self, word, confidence):
        if not self.value_set:
            self.promise.setValue((word, confidence))
            self.value_set = True


####################
# Setup and Run
####################


if __name__ == "__main__":
    stk.runner.run_service(SIMSpeech)
