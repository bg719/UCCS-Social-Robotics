__version__ = "0.0.0"
__author__ = 'ancient-sentinel'

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
        """
        Initializes a new instance of the SIMSpeech service.

        :param qiapp: (qi.Application) The hosting qi application.
        """
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
        """
        Returns an object with a future that will be called when
        one of the provided phrases is recognized with at least
        the minimum confidence.

        :param phrases: (List[str]) The list of phrases.
        :param minimum_confidence: (float) The minimum confidence
            to set the value of the future.
        :return:
        """
        if len(phrases) == 0:
            return _SubscriptionInfo.error('Word list cannot be empty.')
        elif not (0 < minimum_confidence <= 1):
            return _SubscriptionInfo.error('Confidence must be a value between 0 and 1.')

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
        """Cleanup service resources."""
        for subscriber in set().union(self.vocab.values()):
            subscriber.promise.setCanceled()

        self._unregister()
        self.logger.info("SIMSpeech finished.")

    @qi.nobind
    def on_word_recognized(self, eventargs):
        """
        The callback registered to the ALMotion "WordRecognized"
        event. Invokes the callback for each subscriber of a
        recognized phrase.

        :param eventargs: ((str, confidence)) A tuple containing
            the recognized phrase and the confidence.
        """
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
        """
        Registers this service with ALMemory so that `on_word_recognized`
        will be invoked when the "WordRecognized" event is raised, and sets
        the language for the ALSpeechRecognition service.
        """
        self.cid = self.events.subscribe(
            "WordRecognized", "SIMSpeech", self.on_word_recognized)
        self.asr.pause(True)
        self.asr.setLanguage(self.language)
        self.asr.pause(False)
        self.asr.subscribe(self.APP_ID)

    @qi.nobind
    def _unregister(self):
        """
        Unregisters this service from ALMemory and ALSpeechRecognition.
        """
        if self.cid is not None:
            try:
                self.events.clear()  # always throws an exception
            except:
                pass
            self.cid = None
            self.asr.unsubscribe(self.APP_ID)

    @qi.nobind
    def _unsubscribe(self, subscribers, pause=True):
        """
        Unsubscribes the provided list of subscribers and updates
        the vocabulary for ALSpeechRecognition.

        :param subscribers: (List[_SubscriberInfo])
            The list of subscribers to unsubscribe.
        :param pause: (bool) Set True if this is not being called
            while the ALSpeechRecognition service is already paused.
        :return:
        """
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
        """
        Updates the vocabulary of the ALSpeechRecognition service with
        the list of key phrases from the `vocab` dictionary.

        :param pause: (bool) Indicates whether to pause and then
            resume the ALSpeechRecognition service or not. Set True
            if this is not being called while ALSpeechRecognition is
            already paused.
        """
        if self.cid is None:
            self._register()
        if any(self.vocab):
            if pause:
                self.asr.pause(True)

            self.asr.setVocabulary(self.vocab.keys(), False)

            if pause:
                self.asr.pause(False)


class _SubscriptionInfo:
    """Contains subscription information for a registered speech event."""

    def __init__(self, phrases, minimum_confidence):
        """
        Initializes a new subscription info for the speech event with
        the specified phrases and minimum confidence.

        :param phrases: (List[str]) The list of phrases.
        :param minimum_confidence: (float) The minimum confidence needed
            to invoke the associated promise.
        """
        self.promise = qi.Promise()
        self.phrases = phrases
        self.minimum_confidence = minimum_confidence
        self.value_set = False

    def future(self):
        """Returns an object containing the `qi.Future` for this subscription."""
        return _SubscriptionFuture(self.promise.future())

    def is_canceled(self):
        """
        Checks if this subscription is canceled.

        :return: True if canceled; otherwise, False.
        """
        if self.promise.isCancelRequested():
            self.promise.setCanceled()
            return True
        return False

    def set_value(self, phrase, confidence):
        """
        Attempts to set the value on the associated promise with the
        provided phrase and confidence.

        :param phrase: (str) The phrase.
        :param confidence: (float) The confidence.
        :return: True if the promise's value was set; otherwise, False.
        """
        if not self.value_set and confidence >= self.minimum_confidence:
            self.promise.setValue((phrase, confidence))
            self.value_set = True
            return True
        else:
            return False

    @staticmethod
    def error(message):
        """
        Creates an error subscription instance and returns the object
        containing the future for the subscription.

        :param message: (str) The error message.
        :return: The object containing the future for the error
            subscription.
        """
        instance = _SubscriptionInfo((), -1)
        instance.promise.setError(message)
        return instance.future()


class _SubscriptionFuture:
    """An object to pass a future via the qi broker."""

    def __init__(self, future):
        """
        Initializes a new subscription future object.

        :param future: (qi.Future) The future.
        """
        self.future = future


####################
# Setup and Run
####################


if __name__ == "__main__":
    stk.runner.run_service(SIMSpeech)
