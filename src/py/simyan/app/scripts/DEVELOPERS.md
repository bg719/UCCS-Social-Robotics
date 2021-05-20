# Developing the SIMYAN Core SDK
*authors: [ancient-sentinel](https://github.com/ancient-sentinel), [chomuth](https://github.com/chomuth)*

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

This module contains the motion sequence components for executing absolute motion sequences (i.e., sequences
defined by exact Cartesian positions or transforms). It provides a sequence, context, and handler
class which implement the full motion abstraction pattern. It can serve both as an example for how the
pattern can be implemented for other types of motion sequences, as well as can be used as the base for
derived implementations which can convert their inputs into Cartesian positions or transforms.

Important Notes:

* Setting `with_previous` to `True` for either `next_position_keyframe()` or `next_transform_keyframe()` will
  result in an exception in the handler if the previous keyframe is not the same type (i.e., positional or 
  transformational, respectively).
  

* It is recommended to use the `next_position_keyframe()` or `next_transform_keyframe()` for appending all
  keyframes unless there is a significant need to specify a different start position. When a start position
  is specified which is different from the ending position of the previous keyframe, the handler must try
  to infer the duration for the motion transition from the end of the previous keyframe to the start of the
  current one. The current implementation is naive and uses a constant 3-second duration, though it could be
  improved to use the current positions/transforms of the robot to generate a more informed value. In general,
  any motion sequence which counts upon precise timing should not provide keyframes which define a starting
  point. Instead, use a distinct keyframe (with the duration specified) to move to the "start" position and
  then move to the desired position.

##### Classes

#### `class AbsoluteSequence(MotionSequence)`

This class implements the `simutils.motion._sequenc.MotionSequence` abstract class and provides class
methods for building up an absolute motion sequence. 

* `new_position_keyframe(start: Iterable[float], end: Iterable[float], duration: float, effector: str
  frame: int, axis_mask: int, with_previous: bool) -> bool` - A method which appends a new positional 
  keyframe to the motion sequence. The lengths of the start and end position vectors must both be 6.
  It returns `True` if the keyframe was added successfully and `False` otherwise.
  

* `next_position_keyframe(end: Iterable[float], duration: float, effector: str, frame: int, axis_mask: int,
  with_previous: bool) -> bool` - A method which appends a new positional keyframe to the motion sequence.
  The final position at the end of the previous keyframe (or the initial position of the robot if this is the
  first keyframe added) is used as the starting position for the keyframe being added. The lengths of the start
  and end position vectors must both be 6. It returns `True` if the keyframe was added successfully and
  `False` otherwise.
  

* `new_transfrom_keyframe(start: Iterable[float], end: Iterable[float], duration: float, effector: str,
  frame: int, axis_mask: int, with_previous: bool) -> bool` - A method which appends a new transformational
  keyframe to the motion sequence. The lengths of the start and end transform vectors must both be 12.
  It returns `True` if the keyframe was added successfully and `False` otherwise.
  

* `next_trasform_keyframe(end: Iterable[float], duration: float, effector: str, frame: int, axis_mask: int,
  with_previous: bool) -> bool` - A method which appends a new transformational keyframe to the motion sequence.
  The final position at the end of the previous keyframe (or the initial position of the robot if this is the
  first keyframe added) is used as the starting position for the keyframe being added. The lengths of the start
  and end transform vectors must both be 12. It returns `True` if the keyframe was added successfully and `False`
  otherwise.


* `add_keyframe(keyframe: simutils.motion.models.KeyFrame) -> bool` - A method which appends the
  provided keyframe to the sequence. It returns `True` if the keyframe was added successfully and 
  `False` otherwise.
  

* `get_keyframes() -> List[simutils.motion.models.KeyFrame)` - A method which gets the list of keyframes
  which comprise the motion sequence.
  
  
* `check_keyframe(keyframe: simutils.motion.models.KeyFrame) -> bool (static)` - A method which checks whether
  the specified keyframe is valid for an absolute motion sequence. It returns `True` if the keyframe is valid
  and `False` otherwise.
  
&nbsp;

#### `class AbsoluteSequenceContext(MotionSequenceContext)`

This class implements the `simutils.motion._context.MotionSequenceContext` abstract class and provides methods
and properties for defining, managing, and registering an absolute motion sequence context.

* `extensive_validation: bool (abstract)` - A property indicating whether the context performs extensive validation
  before sending motion sequences to be executed by the `SIMMotion` service. The intent of extensive validation
  is to attempt to catch any errors detactable by the client before attempting execution.
  

* `check_sequence(sequence: AbsoluteSequence, extensive: bool) -> bool (abstract)` - A
  method for checking a sequence and optionally performing extensive validation. This method is called
  automatically by the `execute_sequence` method. If `extensive` is `False`, the only validation performed is
  to ensure that the specified `sequence` is an instance of `AbsoluteSequence`. If `extensive` is `True`, then
  each keyframe of the sequence is re-checked after verifying that the sequence is an instance of `AbsoluteSequence`.
  It returns `True` if the sequence is valid and `False` otherwise.
    

* `execute_sequence(sequence: AbsoluteSequence, motion_service: SIMMotion)
  -> simutils.motion.models.ExecutionResult` - A method which performs validation on the provided sequence
  and then sends the sequence to the `SIMMotion` service for execution.
  

* `get_bounds() -> object (abstract)` - A method which returns contextual boundary information for
  executing a motion sequence. `None` indicates that the context's region is unbounded. This method is
  invoked by the selected motion sequence handler in the `SIMMotion` service. NOT SUPPORTED BY CURRENT
  IMPLEMENTATION.
  

* `get_ctype() -> str (abstract)` - A method which returns the context type of the context. The context
  type is used by the `SIMMotion` service to select a handler. Returns `simutils.motion.constants.CTYPE_ABSOLUTE`.
  

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

#### `class AbsoluteSequenceHandler(MotionSequenceHandler)`

This class implements the `simutils.motion._handler.MotionSequenceHandler` abstract class and provides the ability
to execute absolute motion sequences.

* `handle_sequence(sequence: AbsoluteSequence, context: AbsoluteSequenceContext, motion_proxy: ALMotion,
  posture_proxy: ALRobotPosture) -> simutils.motion.models.ExecutionResult (abstract)` - A method which handles the
  execution of the specified motion sequence within the scope of the provided motion sequence context.
  

* `handles_type(ctype: str) -> bool (abstract)` - A method which determines whether the handler can handle
  the specified motion sequence context type. Returns true if the provided `ctype` is 
  `simutils.motion.constants.CTYPE_ABSOLUTE`.
  
&nbsp;

#### `codes` Module

This module contains status code definitions for different statuses returned from motion sequence handlers
and the `SIMMotion` service when a sequence is executed.

##### Constants

* `SUCCESS = 0` - A value representing successful execution of a motion sequence.


* `GEN_ERROR = -1` - A value representing a general (unspecified) error during execution of a motion sequence.


* `BAD_ARG = -4` - A value representing an error due to a bad argument.


* `BAD_OP = -5` - A value representing an error due to a bad or invalid operation.


* `NO_CTX = -100` - A value returned from the `SIMMotion` service indicating that there is no context registered
  with the specified name.
  

* `BAD_SEQ = -101` - A value returned from the `SIMMotion` service indicating that a bad motion sequence was given.

&nbsp;

#### `constants` Module

This module contains motion constants for both the SIMYAN motion utility framework and the NAO motion API.

##### Constants

* `FRAME_TORSO = 0` - This frame is attached to the robot's torso reference, so it moves with
  the robot as he walks and changes orientation as he leans. This space is
  useful when you have very local tasks that make sense in the orientation
  of the torso frame.
  

* `FRAME_WORLD = 1` - This frame is in reference to a fixed origin that is never altered,
  specifically, the world-position where the robot starts. It is left behind
  when the robot walks, and will be different in z-rotation after the robot
  has turned. This space is useful for calculations which require an external,
  absolute frame of reference.
  

* `FRAME_ROBOT = 2` - This frame is average of the two feet positions projected around a vertical
  z-axis. This space is useful because the x-axis is always forwards, so
  it provides a natural, ego-centric reference.

  
* `FRAMES` - A tuple containing all the defined spatial frames.


* `MVT_RELATIVE` - Specifies that movement is relative to the current position.


* `MVT_ABSOLUTE` - Specifies that movement is in reference to absolute position.


* `COMMANDS = 0`


* `SENSORS = 1`


* `AXIS_MASK_X = 1` - Mask for x-axis.


* `AXIS_MASK_Y = 2` - Mask for y-axis.


* `AXIS_MASK_Z = 4` - Mask for z-axis.


* `AXIS_MASK_WX = 8` - Mask for x-axis rotation.


* `AXIS_MASK_WY = 16` - Mask for y-axis rotation.


* `AXIS_MASK_WZ = 32` - Mask for z-axis rotation.


* `AXIS_MASK_ALL = 63` - Mask for x, y, z, wx, wy, and wz axes.


* `AXIS_MASK_VEL = 7` - Mask for x, y, and z axes.


* `AXIS_MASK_ROT = 56` - Mask for wx, wy, and wz rotation axes.


* `TO_RAD = 0.01745329` - The conversion factor for converting degrees to radians.


* `TO_DEG = 57.295779513082323` - The conversion factor for converting radians to degrees.


* `EF_HEAD = 'Head'` - The identifier for the robot's head effector.


* `EF_LEFT_ARM = 'LArm'` - The identifier for the robot's left arm effector.


* `EF_LEFT_LEG = 'LLeg'` - The identifier for the robot's left leg effector.


* `EF_RIGHT_ARM = 'RArm'` - The identifier for the robot's right arm effector.


* `EF_RIGHT_LEG = 'RLeg'` - The identifier for the robot's right leg effector.


* `EF_TORSO = 'Torso'` - The identifier for the robot's torso effector.


* `EFFECTORS` - A tuple containing all the robot's effectors.


* `CHAIN_BODY = 'Body'` - The identifier for the body chain.


* `CHAIN_LEGS = 'Legs'` - The identifier for both leg chains.


* `CHAIN_ARMS = 'Arms'` - The identifier for both arm chains.


* `CHAIN_LEFT_ARM = 'LArm'` - The identifier for the left arm chain.


* `CHAIN_RIGHT_ARM = 'RArm'` - The identifier for the right arm chain.


* `CHAIN_HEAD = 'Head'` - The identifier for the head chain.


* `CHAINS` - A tuple containing all the robot's chain names.


* `POSE_STAND = 'Stand'` - The identifier for the predefined standing pose.


* `POSE_STAND_INIT = 'StandInit'` - The identifier for the predefined initial standing pose.


* `POSE_STAND_ZERO = 'StandZero'` - The identifier for the predefined zeroed standing pose.


* `POSE_CROUCH = 'Crouch'` - The identifier for the predefined crouching pose.


* `POSE_SIT = 'Sit'` - The identifier for the predefined sitting pose.


* `POSE_SIT_RELAX = 'SitRelax'` - The identifier for the predefined relaxed sitting pose.


* `POSE_LYING_BELLY = 'LyingBelly'` - The identifier for the predefined pose lying on the belly.


* `POSE_LYING_BACK = 'LyingBack'` - The identifier for the predefined pose lying on the back. 


* `PREDEFINED_POSES` - A tuple containing all the predefined poses.


* `FOOT_HEIGHT = 0.04519` - Foot height in meters.


* `HAND_OFFSET_X = 0.05775` - Hand offset in the x-axis in meters.


* `HAND_OFFSET_Z = 0.01231` - Hand offset in the z-axis in meters.


* `CTYPE_ABSOLUTE = 'absolute'` - Absolute context type. Used for absolute position or transform sequence contexts.


* `CTYPE_ANY = 'any'` - Any context type.


* `CTYPE_NONE = 'none'` - No context type.


* `CTYPE_PLANAR = 'planar'` - Planar context type. Used for planar position sequence contexts.


* `CTYPES` - A list containing defined context types.


* `KFTYPE_NONE = 'none'` - No keyframe type.


* `KFTYPE_ABSOLUTE_POSITION = 'absolute.position'` - Absolute position keyframe type. Indicates that the values of
  the keyframe are absolute positions.
  

* `KFTYPE_ABSOLUTE_TRANSFORM = 'absolute.transform'` - Absolute transform keyframe type. Indicates that the values
  of the keyframe are absolute transforms.


* `KFTYPE_PLANAR = 'planar'` - Planar keyframe type. Indicates that the values are coordinate pairs.


* `KFTYPES` - A list containing defined keyframe types.

&nbsp;

#### `models` Module

This module contains models for the SIMYAN motion utility framework.

##### Classes

#### `class ExecutionResult`

This class contains the result information from executing a motion sequence.

* `success_result(message: str, status: int) -> ExecutionResult (static)` - A method which creates a success
  execution result instance.
  

* `error_result(message: str, status: int) -> ExecutionResult (static)` - A method which creates an error
  execution result instance.

  
* `invalid_arg(arg_name: str) -> ExecutionResult (static)` - A method which creates an error result for an
  invalid argument.
  

* `invalid_kftype(kftype: str) -> ExecutionResult (static)` - A method which creates an error result for a keyframe
  with an invalid keyframe type.
  

* `keyframe_exception(exception: KeyframeException) -> ExectutionResult (static)` - A method which creates an error
  result from a keyframe exception.
  

* `no_such_context(context_name: str) -> ExecutionResult (static)` - A method which creates an error result because
  of a non-existent (unregistered) context.
  
&nbsp;

#### `class KeyFrame`

This class defines a motion keyframe.

* `start: List[float]` - A property which stores the value of the starting location.


* `end: List[float]` - A property which stores the value of the ending location.


* `duration: float` - A property which stores the duration of the keyframe.


* `effector: str` - A property which stores the effector targeted by the keyframe.


* `frame: int` - A property which stores the spatial reference frame. (Must be in `simutils.motion.constants.FRAMES`)


* `axis_mask: int` - A property which stores the axis mask. (Must be in `simutils.motion.constants.AXIS_MASKS`)


* `kftype: str` - A property which specifies the keyframe type. (See `simutils.motion.constants.KFTYPES`)


* `with_previous: bool` - A property which indicates whether this keyframe should execute concurrently with the
  previous keyframe.
  
&nbsp;

#### `class Plane`

This class provides the ability to define a plane in 3-space using a point in the plane and a vector which is
normal to the plane.

* `point: List[List[float]]` - A property which stores the value of the point.


* `normal: List[List[float]]` - A property which stores the value of the normal vector.


* `from_points(points: Iterable[Iterable[float]]) -> Plane (static)` - A method which determines the plane which
  passes through the set of three points provided.
  

* `create_from_points(p1: Iterable[float], p2: Iterable[float], p3: Iterable[float]) -> Plane (static)` - A method
  which determines the plane which passes through the three points.
  

#### `planar` Module

INCOMPLETE!!! This module contains the motion sequence components for executing planar motion sequences (i.e., 
sequences defined by coordinate-pair points). It provides a sequence, context, and handler
class which implement the full motion abstraction pattern. 

#### `preparation` Module

This module contains helper methods for preparing the robot to execute motion sequences.

#### Helper Methods

* `disable_head_control(motion_proxy: ALMotion, stiffness: float)` - A method which disables control of the head
  effector and sets the final joint stiffness.
  

* `disable_left_arm_control(motion_proxy: ALMotion, stiffness: float)` - A method which disables control of the
  left arm effector and sets the final joint stiffness.
  

* `disable_right_arm_control(motion_proxy: ALMotion, stiffness: float)` - A method which disables control of the
  right arm effector and sets the final joint stiffness.
  

* `enable_head_control(motion_proxy: ALMotion, stiffness: float)` - A method which enables control of the head 
  effector and sets the initial joint stiffness.
  

* `enable_left_arm_control(motion_proxy: ALMotion, stiffness: float)` - A method which enables control of the left
  arm effector and sets the initial joint stiffness.
  

* `enable_right_arm_control(motion_proxy: ALMotion, stiffness: float)` - A method which enables control of the right
  arm effector and sets the initial joint stiffness.
  

* `async_disable_breathing(chains: Iterable[str], motion_proxy: ALMotion) -> qi.Future` - A method which disables
  the "breathing" motions for the specified chains, then delays for 2 seconds to wait for completion. Returns a
  future which completes after the 2-second delay is finished.
  

* `async_enable_breathing(chains: Iterable[str], motion_proxy: ALMotion) -> qi.Future` - A method which enables
  the "breathing" motions for the specified chains, then delays for 2 seconds to wait for completion. Returns a
  future which completes after the 2-second delay is finished.
  

* `disable_breathing(chains: Iterable[str], motion_proxy: ALMotion)` - A method which disables the "breathing" motions
  for the specified chains, but does not provide any delay to ensure completion of the action.
  

* `enable_breathing(chains: Iterable[str], motion_proxy: ALMotion)` - A method which enables the "breathing" motions
  for the specified chains, but does not provide any delay to ensure completion of the action.

#### `utils` Module

This module contains utility helper methods for the motion module.

##### Helper Methods

* `to_point(p: Union[Iterable[float], float], n: int)` - A method which attempts to convert the parameter `p` into a
  point in `n`-space. Parameters which result in a valid point definition include:
    * Numeric iterables with `n` elements,
    * The value 0 (corresponding with the origin).

&nbsp;

### `service` Module

This module contains a helper class for registering and managing custom service modules.

##### Classes

#### `class ServiceScope`

This class provides a managed scope for a service registered within the context of an existing qi.Application.

* `create_scope()` - A method which creates an instance of the service and registers it with the application
  session. It automatically calls the `on_start()` method of the service module if it is defined.
  

* `close_scope()` - A methods which unregisters the service instance from the application session and disposes
  the instance. It automatically calls the `on_stop()` method of the service module if it is defined.


* `is_started() -> bool` - A method which returns a value indicating whether a scope has been created and the
  service started.
  
&nbsp;

### `speech` Module

A module which provides helper classes for utilizing the NAO speech APIs.

#### Classes

#### `class QiState(Enum)`:
*See Wiki documentation.*

&nbsp;

#### `class QiChatBuilder`:
*See Wiki documentation.*

&nbsp;

#### `class SpeechEvent`:

This class represents a speech event which invokes a callback when a particular phrase is recognized.

* `is_subscribed() -> bool` - A method which returns a value indicating whether the speech event is subscribed.
  Returns `True` if the event is registered, otherwise `False`.


* `register(speech_service: SIMSpeech) -> bool` - A method which registers the speech event with the provided
  speech service. It returns `True` if the registration was successful, otherwise `False`.
  

* `unregister() -> bool` - A method which unregisters the speech event from the speech service it is subscribed
  to. It returns `True` if the event was unregistered successfully, otherwise `False`.
  

* `wait(timeout: float) -> qi.FutureState` - A method which waits for the speech event to occur. if a timeout is
  specified, the event subscription will be canceled after that period if it has not already occurred.
  
&nbsp;

#### `class SpeechEventException(Exception)`

A class which represents an exception raised due to a speech event error.

* `message: str` - A property which stores the error message.

&nbsp;

### `timer` Module

A module which contains an asynchronous timer helper method.

#### Helper Methods

* `async_timer(seconds: float) -> qi.Future` - A method which creates an asynchronous timer which finishes after the
  specified number of seconds. It is recommended to use this timer instead of putting threads to sleep, particularly
  for processes running directly on the robot. Putting threads to sleep incurs a significant performance hit on the
  robot's processor and should be avoided whenever possible.


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
