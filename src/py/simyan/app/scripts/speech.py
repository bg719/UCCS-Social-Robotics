__version__ = "0.0.0"

import qi

import stk.runner
import stk.events
import stk.services
import stk.logging


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

    @qi.bind(returnType=qi.Int8, paramsType=[qi.List(qi.String), qi.Object])
    def subscribe(self, words, promise):
        # vocab with no subscribers
        for word in words:
            if word in self.vocab:
                self.vocab[word].append(promise)
            else:
                self.vocab[word] = [promise]
        id = self.id_count
        self.id_count += 1
        self.subscribers[id] = promise, words
        self._update_vocabulary()
        return id

    @qi.bind(returnType=qi.Bool, paramsType=[qi.Int8])
    def unsubscribe(self, id):
        if id not in self.subscribers:
            return False
        promise, words = self.subscribers.pop(id)
        for word in words:
            entry = self.vocab[word]
            entry.remove(promise)
            if len(entry) == 0:
                self.vocab.pop(word)
        self._update_vocabulary()
        return True

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
        self.logger.info(eventargs)
        self.asr.pause(True)
        word = eventargs[0][6:-6]
        confidence = eventargs[1]
        self.logger.info(word)
        if word in self.vocab:
            for promise in self.vocab[word]:
                promise.setValue((word, confidence))
        self.asr.pause(False)

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
    def _update_vocabulary(self):
        if self.cid is None:
            self._register()
        if any(self.vocab):
            self.asr.pause(True)
            self.asr.setVocabulary(self.vocab.keys(), True)
            self.asr.pause(False)
        else:
            self._unregister()


####################
# Setup and Run
####################


if __name__ == "__main__":
    stk.runner.run_service(SIMSpeech)
