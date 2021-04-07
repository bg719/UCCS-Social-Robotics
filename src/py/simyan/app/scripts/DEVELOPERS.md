# Developing the SIMYAN Core SDK
This file contains documentation on the existing components within the SIMYAN Core
SDK, as well as provides guidance for adding further extensions to it.

*author: [ancient-sentinel](https://github.com/ancient-sentinel)*


## Core Components

### SIMActivityManager - *main.py*

### SIMMotorControl - *movement.py*

### SIMSpeech - *speech.py*

### SIMVision - *vision.py*


## Utilities

### ServiceScope - *simutils/service.py*

### MotionSequence - *simutils/motion.py*

### MotionSequenceContext - *simutils/motion.py*

### PlanarSequence - *simutils/motion.py*

### PlanarSequenceContext - *simutils/motion.py*


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
