# Developing the SIMYAN Core SDK
*author: [ancient-sentinel](https://github.com/ancient-sentinel)*

This file contains documentation on the existing components within the SIMYAN Core
SDK, as well as provides guidance for adding further extensions to it.

## In This Document:
### [SIMYAN Services](#simyan-services)
  - [`SIMServiceManager`](#simservicemanager-in-simyanpy)
  - [`SIMMotion`](#simmotion-in-motionpy)
  - [`SIMSpeech`](#simspeech-in-speechpy)
  - [`SIMVision`](#simvision-in-visionpy)
  

### [simutils Package](#simutils-package)
  - [`motion` Package](#motion-package)
  - [`service` Module](#service-module)
  - [`speech` Module](#speech-module)
  - [`timer` Module](#timer-module)
  

### [Conventions](#conventions)
  - [Naming](#naming)

---
&nbsp;

## SIMYAN Services

&nbsp;

### `SIMServiceManager` in *simyan.py*
The SIMYAN service manager provides the means for initializing and orchestrating SIMYAN services.
By default, it provides the `SIMMotion`, `SIMSpeech`, and `SIMVision` modules, which are registered
when the `startServices()` method is called. Additional default services can be easily incorporated by
adding new `ServiceScope` registrations in the class's `__init__()` method.

---

#### Methods

* `startServices() -> qi.Void`
  
Starts and registers all default SIMYAN services. This method is thread-safe and safe to be called
by multiple applications. A particular application should not call the method multiple times before
calling `stopServices()`.
  

* `stopServices() -> qi.Void`
  
Unregisters and stops all default SIMYAN services so long as no other applications are still using 
them. This is determined by keeping track of the number of times the `startServices()` method is
called. When the number of calls to `stopServices()` equals the number of calls to `startServices()`,
the services will be stopped. This method is thread-safe and safe to be called by multiple applications.
A particular application should not call the method multiple times.


* `stop() -> qi.Void`

Stops and unregisters the SIMYAN service manager and all managed services.

---

#### Registering Additional Default Services
```python
class SIMServiceManager(object):

      def __init__(self, qiapp, dev=False):
        """
        Initializes a new SIMYAN service manager instance.

        :param qiapp: (qi.Application) The hosting qi application.
        """
        
        # ... start of method ...
        
        self.scoped_services = [
            ServiceScope(qiapp, SIMMotion),
            ServiceScope(qiapp, SIMSpeech),
            ServiceScope(qiapp, SIMVision),
            ServiceScope(qiapp, SIMMyCustomService) # Add your service to the list
        ]
        
        # ... rest of method ...
          
    # ... rest of class ...
```

---

#### Recommended Extensions
* Providing service methods to query whether a particular SIMYAN service is available, or to 
  get a list of registered SIMYAN services.
* Providing a mechanism to dynamically add SIMYAN services, either by scanning modules, or as
  parameters to `__init__()` (See the `simutils.service` module for some known issues).

&nbsp;

### `SIMMotion` in *motion.py*
The SIMYAN motion service provides a means for registering, managing, and executing various motion
sequences. A motion sequence is intended to hide the complexity of building up and managing
invocations to the `ALMotion` service, as well as automatically trigger standard actions. The service
provides globalized orchestration of motion sequence actions and functionality provided in the 
`simutils.motion` package.

---

#### Methods

* `registerContext(context: simutils.motion._context.MotionSequenceContext) -> qi.Bool`
  
Registers a motion sequence context with the service. Returns `True` if the registration was successful or
`False` if it was not. The `context` parameter should be an instance of a class derived from the
`simutils.motion._context.MotionSequenceContext` class, specific to a particular type of sequence.
Look at the `simutils.motion.absolute.AbsoluteMotionContext` as an example. During registration,
the service will check if it has any handlers which can handle motion sequences of that type.


* `hasContext(name: str) -> qi.Bool`
  
Checks whether the service has any contexts registered with
the specified name. Returns `True` if there is a context with that name registered; otherwise,
`False`.


* `removeContext(name: str) -> qi.Bool`

Removes the context with the specified `name`. Returns `True` if the context was found and removed;
otherwis, `False`.


* `supportsContextType(type: str) -> qi.Bool`

Returns a value indicating whether the specified context type is supported. It returns `True` if the
service has a handler for motion sequences of the specified type and `False`, otherwise.


* `executeSequence(context_name: str, sequence: simutils.motion.MotionSequence -> simutils.motion.ExecutionResult`

Executes the provided motion sequence according to the specified context. Returns a `simutils.motion.ExecutionResult`
which indicates whether the motion sequence was executed successfully or contains error information if
it was not. The specified `context_name` must match a registered context with the same type of motion
sequence data as the provided `sequence`. The `sequence` should be an instance of a class derived from
the `simutils.motion._sequence.MotionSequence` class, specific to the particular type of motion sequence
data. Look at the `simutils.motion.absolute.AbsoluteSequence` as an example. The service will invoke the
matching sequence handler, providing the context and sequence as inputs. 

This method is thread-safe and guarantees that only one motion sequence will be executed at a time.
Further, each sequence will be executed atomically, so no sequence will be interrupted by another part
way through execution. However, this does not prevent other direct calls to `ALMotion`, `ALRobotPosture`,
or other motion API methods from executing during an active sequence. This method is a blocking call.


* `stop()`

Stops and unregisters the SIMYAN motion service.

---

#### Registering Additional Motion Sequence Handlers
```python
class SIMMotion(object):
    def __init__(self, qiapp):
        """
        Initializes a new instance of the SIMMotion service.
        
        :param qiapp: (qi.Application) The hosting qi application.
        """
        # ... start of method ...
        
        self.handlers = [
            AbsoluteSequenceHandler(),
            CustomSequenceHandler()     # Add your handler to the list
        ]
        
        # ... rest of method ...

    # ... rest of class ...
```

#### Recommended Extensions
* Add support for additional motion sequence types. See the `simutils.motion` package documentation for
  more information.
  
&nbsp;

### `SIMSpeech` in *speech.py*
The SIMYAN speech service provides a means for subscribing to speech events and manages simultaneous
subscriptions from multiple applications/subscribers with different phrase vocabularies. It pairs with
the `simutils.speech.SpeechEvent` class to make subscription simple and easily managed.

#### Methods

* `subscribe(phrases: List(str), minimum_confidence: float) -> qi.Future`

Creates a speech event subscription for the specified phrases. It returns a future that will be called
when one of the provided phrases is recognized with at least the minimum confidence. Each phrase in the
list of phrases may contain one or more words which will be recognized as a unit. The minimum confidence
sets a threshold to ensure that the recognition system is suitably certain that the phrase was actually
heard. When a speech event occurs, the value of the subscription future is set with a tuple containing
the recognized phrase and the confidence it was recognized with.

Each subscription is for a single event and repeated recognition requires re-subscribing after
an event has been triggered. This behavior is handled transparently to the user if the 
`simutils.speech.SpeechEvent` class is used for registration, though it is not strictly required in order
to use this speech service. Unsubscribing is accomplished by requesting cancellation on the subscription
future.

* `stop() -> qi.Void`

Stops and unregisters the SIMYAN speech service.

---

### `SIMVision` in *vision.py*
&lt; Not Implemented Yet &gt;

&nbsp;

## simutils Package

### `motion` Package

The motion package contains a number of modules to support an abstraction layer for
designing, constructing, and executing complex motion sequences.

#### `_context` Module

This module contains internal motion package components for defining motion sequence
contexts. Currently, the only thing in the module is the `MotionSequenceContext` abstract
class, which should be used as the base class for all motion sequence context implementations.

#### `_handler` Module

This module contains internal motion package components for defining motion sequence
handlers. The core component in this module is the `MotionSequenceHandler` abstract class,
which should be used as the base class for all motion sequence handler implementations.
The module also contains constants and helper methods for implementing motion sequence
handlers. 

#### `_sequence` Module
#### `absolute` Module
#### `codes` Module
#### `constants` Module
#### `models` Module
#### `planar` Module
#### `preparation` Module
#### `utils` Module

### `service` Module

### `speech` Module

### `timer` Module


## Conventions

### Naming
The following conventions are used for naming code elements:

* Service classes registered within the context of a SIMYAN session should begin
  with "SIM". 
  * Example: `SIMMyServiceName`
  
* Service class method names use the following conventions:
  
  * Service methods exposed via the qi framework (using qi.bind) are camel-cased
  to match the naoqi/qi framework convention.
    * Examples:
      * `myServiceMethod(...)`
      * `method(...)`
    
  * Service methods registered as event/signal handlers are lower-cased and
  separated by underscores to match the naoqi/qi framework convention.
    * Examples:
      * `on_start(...)`
      * `on_my_event(...)`
    
  * Private service methods are lower-cased, begin with an underscore, and separated
  by underscores.
    * Examples:
      * `_my_private_method(...)`
      * `_reset(...)`
