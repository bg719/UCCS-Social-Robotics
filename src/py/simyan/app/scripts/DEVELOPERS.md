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
                        

## SIMYAN Services

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
The SIMYAN vision service provides many helpful methods that can be used to learn more about the NAO's
environment and to make specific conversions that may be needed in the future.

#### Methods

* `detectPixels(img: qi.String, pixel_color: qi.Struct, r_range: qi.UInt8, g_range: qi.UInt8, b_range: qi.UInt8) -> qi.List(qi.Struct)`

This method detects all the pixels within a specified RGB range then returns all the pixel locations
that are detected. The RGB range that is used is based off the input paramaters `pixel_color`, `r_range`,
`g_range`, and `b_range`. The range is construted by using the r, g, and b values found in `pixel_color`
as the center points then adding and subtracting `r_range`, `g_range`, and `b_range` from the center points
to get the boundaries. The parameter `img` is refering to the path of the that you would like to search.

* `getBoundary(detected_pixels: qi.List(qi.Struct)) -> qi.List(qi.Struct)`

This method detects the inner boundaries of a list of x, y coordinates and returns the top, bottom, left,
and right boundaries respectively. The only parameter that this method takes is `detected_pixels` which
should be a list of x and y coordinates. 

* `rescale(edges: qi.List(qi.Struct), scale: qi.List(qi.UInt8)) -> qi.List(qi.Struct)`

This method rescales a list of edges by a specified scaling factor. The parameter `edges` should be a list
of structs that contain a beginning x and y coordinate along with an ending x and y coordinate. The parameter
`scale` should be a list of 2 integers that represent an x and y scaling factor respectively.

&nbsp;

## simutils Package

### `motion` Package

The motion package contains a number of modules to support an abstraction layer for
designing, constructing, and executing complex motion sequences.

&nbsp;

#### `_context` Module

This module contains internal motion package components for defining motion sequence
contexts. Currently, the only thing in the module is the `MotionSequenceContext` abstract
class, which should be used as the base class for all motion sequence context implementations.


##### Classes

`class MotionSequenceContext (abstract)`

This class serves as the base class for all motion sequence context implementations. It defines
a couple of abstract methods and properties to standardize contextual information, regardless of
the particulars of the implementation.

* `extensive_validation: bool (abstract)` - A property indicating whether the context performs extensive validation
  before sending motion sequences to be executed by the `SIMMotion` service. The intent of extensive validation
  is to attempt to catch any errors detactable by the client before attempting execution.
  

* `check_sequence(sequence: simutils.motion._sequence.MotionSequence, extensive: bool) -> bool (abstract)` - A
  method for checking a sequence and optionally performing extensive validation. This method is called
  automatically by the `execute_sequence` method.
    

* `execute_sequence(sequence: simutils.motion._sequence.MotionSequence, motion_service: SIMMotion)
  -> simutils.motion.models.ExecutionResult` - A method which performs validation on the provided sequence
  and then sends the sequence to the `SIMMotion` service for execution.
  

* `get_bounds() -> object (abstract)` - A method which returns contextual boundary information for
  executing a motion sequence. `None` indicates that the context's region is unbounded. This method is
  invoked by the selected motion sequence handler in the `SIMMotion` service.
  

* `get_ctype() -> str (abstract)` - A method which returns the context type of the context. The context
  type is used by the `SIMMotion` service to select a handler.
  

* `get_name() -> str (abstract)` - A method which returns the name of the context. The context name is used
  to save a reference to the context when it is registered with the `SIMMotion` service.
  

* `get_or_set_initial_pose() -> Union[str, bool] (abstract)` - A method which either returns the string identifier
  for a named robot pose (see `simutils.motion.contants` items starting with `POSE_`) or attempts to set
  the initial position itself. In the second case, the method returns `True` if the position was set successfully
  or `False` if it was not. The motion sequence handler should not attempt to execute a sequence if this method
  returns `False`.
  

* `register(motion_service: SIMMotion) -> bool` - A method which registers the context with the provided
  motion service. Returns `True` if registration was successful and `False` if it was not.
  

* `unregister(motion_service: SIMMotion) -> bool` - A method which unregisters the context from the provided
  motion service. Returns `True` if the context was formerly registered and successfully removed; otherwise,
  it returns `False`.

&nbsp;

#### `_handler` Module

This module contains internal motion package components for defining motion sequence
handlers. The core component in this module is the `MotionSequenceHandler` abstract class,
which should be used as the base class for all motion sequence handler implementations.
The module also contains constants and helper methods for implementing motion sequence
handlers.

##### Terms and Definitions

* *invocation type* - A value used to decide which `ALMotion` method to invoke. The
  `simutils.motion.absolute.AbsoluteSequenceHandler` uses the keyframe type as the invocation type.
  Keyframes with the 'absolute.position' type will result in invocation of the `ALMotion.positionInterpolations`
  method, and the 'absolute.transform' type will result in invocations of the `ALMotion.transfromInterpolations`
  method.


* *invocation list* - A list of invocations to `ALMotion` methods that is built up in order to execute
  the set of keyframes comprising a motion sequence.


* *invocation entry* - A single entry in an *invocation list*. It is a tuple containing the *invocation type*
  and then the list of *invocation arguments*.


* *invocation arguments* - The list of arguments for a single invocation to an `ALMotion` method.

##### Constants

* `TYPE = 0` - A constant value representing the index of the invocation type in an invocation list entry.


* `ARGS = 1` - A constant value representing the index of the invocation argument list in an invocation
  list entry.
  

* `EFFECTORS = 0` - A constant value representing the index of the effectors vector in an invocation
  argument list for either `ALMotion.positionInterpolations` or `ALMotion.transformInterpolations`.


* `FRAMES = 1` - A constant value representing the index of the frames vector in an invocation argument
  list for either `ALMotion.positionInterpolations` or `ALMotion.transformInterpolations`.


* `PATHS = 2` - A constant value representing the index of the paths vector in an invocation argument
  list for either `ALMotion.positionInterpolations` or `ALMotion.transformInterpolations`.
  

* `MASKS = 3` - A constant value representing the index of the masks vector in an invocation argument
  list for either `ALMotion.positionInterpolations` or `ALMotion.transformInterpolations`.
  

* `TIMES = 4` - A constant value representing the index of the times vector in an invocation argument
  list for either `ALMotion.positionInterpolations` or `ALMotion.transformInterpolations`.
  

##### Helper Methods

* `new_invocation_args() -> Tuple(List, List, List, List, List)` - Returns a new, empty invocation argument
  set for either `ALMotion.positionInterpolations` or `ALMotion.transformInterpolations`. 
  

* `are_equal(p1: List[float], p2: List[float], thresholds: Union[float, Iterable[float, Iterable[float]]])
  -> bool` - Determines whether `p1` and `p2` are equal within the specified threshold(s).
  

##### Classes

`class KeyframeException(Exception)`

An exception raised due to keyframe errors while attempting to execute a motion sequence.

* `type_mismatch(current: simutils.motion.models.KeyFrame, previous: simutils.motion.models.KeyFrame)
  -> KeyframeException (static)` - Creates a new exception instance with an error indicating a keyframe
  type mismatch between `current` and `previous`.
  
&nbsp;

`class KeyframeTypeError(ValueError)`

An error due to an invalid keyframe type encountered while attempting to execute a motion sequence.

&nbsp;

`class MotionSequenceHandler (abstract)`

This class serves as the base class for all motion sequence handler implementations. It defines
a couple of abstract methods and properties to standardize handler interface, regardless of
the particulars of the implementation.

* `handle_sequence(sequence: simutils.motion._sequence.MotionSequence, context:
  simutils.motion._context.MotionSequenceContext, motion_proxy: ALMotion, posture_proxy: ALRobotPosture)
  -> simutils.motion.models.ExecutionResult (abstract)` - A method which handles the execution of the
  specified motion sequence within the scope of the provided motion sequence context.
  

* `handles_type(ctype: str) -> bool (abstract)` - A method which determines whether the handler can handle
  the specified motion sequence context type.

&nbsp;

#### `_sequence` Module

This module contains internal motion package components for defining motion sequences. Currently, the
only thing in the module is the `MotionSequence` abstract class, which should be used as the base class
for all motion sequence implementations.

##### Classes

#### `class MotionSequence (abstract)`

This class serves as the base class for all motion sequence implementations. It defines
a couple of abstract methods and properties to standardize sequence interface, regardless of
the particulars of the implementation.

* `add_keyframe(keyframe: simutils.motion.models.KeyFrame) -> bool` - A method which appends the
  provided keyframe to the sequence. It returns `True` if the keyframe was added successfully and 
  `False` otherwise.
  

* `get_keyframes() -> List[simutils.motion.models.KeyFrame)` - A method which gets the list of keyframes
  which comprise the motion sequence.

&nbsp;

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
