"""
See documentation for additional constants and information:

- Frames: https://developer.softbankrobotics.com/nao-naoqi-2-1/naoqi-developer-guide/naoqi-framework/naoqi-apis/naoqi-motion/almotion/cartesian
- Effectors: https://developer.softbankrobotics.com/nao-naoqi-2-1/nao-documentation/nao-technical-guide/nao-technical-overview/effector-chain#nao-effector
- Dimensions: https://developer.softbankrobotics.com/nao-naoqi-2-1/nao-documentation/nao-technical-guide/nao-h25/h25-links
"""

__version__ = "0.0.0"

# FRAMES
FRAME_TORSO = 0
"""
This get_frame is attached to the robot's torso reference, so it moves with
the robot as he walks and changes orientation as he leans. This space is
useful when you have very local tasks that make sense in the orientation
of the torso get_frame.
"""

FRAME_WORLD = 1
"""
This get_frame is in reference to a fixed origin that is never altered,
specifically, the world-position where the robot starts. It is left behind
when the robot walks, and will be different in z-rotation after the robot
has turned. This space is useful for calculations which require an external,
absolute get_frame of reference.
"""

FRAME_ROBOT = 2
"""
This get_frame is average of the two feet positions projected around a vertical
z-axis. This space is useful because the x-axis is always forwards so
it provides a natural, ego-centric reference.
"""

# MOVEMENT
MVT_RELATIVE = 0
MVT_ABSOLUTE = 1

# ANGLE TYPE
COMMANDS = 0,
SENSORS = 1

# AXIS MASK
AXIS_MASK_X = 1
AXIS_MASK_Y = 2
AXIS_MASK_Z = 4
AXIS_MASK_WX = 8
AXIS_MASK_WY = 16
AXIS_MASK_WZ = 32
AXIS_MASK_ALL = 63
AXIS_MASK_VEL = 7
AXIS_MASK_ROT = 56

# COMPUTING
TO_RAD = 0.01745329
TO_DEG = 57.295779513082323

# EFFECTORS
EF_HEAD = 'Head'
"""
The identifier for the robot's head effector.

Position: 
    At the neck joint.

End Transform: 
    [0.0, 0.0, 0.0]
"""

EF_LEFT_ARM = 'LArm'
"""
The identifier for the robot's left arm effector.

Position: 
    Inside the hand.
    
End Transform:
    [HAND_OFFSET_X, 0.0, -HAND_OFFSET_Z]
"""

EF_LEFT_LEG = 'LLeg'
"""
The identifier for the robot's left leg effector.

Position:
    Below the ankle.
    
End Transform:
    [0.0, 0.0, -FOOT_HEIGHT]
"""

EF_RIGHT_ARM = 'RArm'
"""
The identifier for the robot's right arm effector.

Position: 
    Inside the hand.
    
End Transform:
    [HAND_OFFSET_X, 0.0, -HAND_OFFSET_Z]
"""

EF_RIGHT_LEG = 'RLeg'
"""
The identifier for the robot's right leg effector.

Position:
    Below the ankle.
    
End Transform:
    [0.0, 0.0, -FOOT_HEIGHT]
"""

EF_TORSO = 'Torso'
"""
The identifier for the robot's torso effector.

Position:
    A reference point in the torso.

End Transform:
    [0.0, 0.0, 0.0]
"""

# DIMENSIONS
FOOT_HEIGHT = 0.04519
"""Foot height (m)."""

HAND_OFFSET_X = 0.05775
"""Hand offset in the x-axis (m)."""

HAND_OFFSET_Z = 0.01231
"""Hand offset in the z-axis (m)."""

# CONTEXT TYPES
CTYPE_ANY = 'any'
CTYPE_NONE = 'none'
CTYPE_PLANAR = 'planar'

# KEYFRAME TYPES
KFTYPE_ANY = 'any'
KFTYPE_NONE = 'none'
KFTYPE_PLANAR = 'planar'
