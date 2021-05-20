"""
See documentation for additional constants and information:

Frames:
    - https://developer.softbankrobotics.com/nao-naoqi-2-1/naoqi-developer-guide/naoqi-framework/naoqi-apis/naoqi-motion/almotion/cartesian
Effectors:
    - https://developer.softbankrobotics.com/nao-naoqi-2-1/nao-documentation/nao-technical-guide/nao-technical-overview/effector-chain#nao-effector
Dimensions:
    - https://developer.softbankrobotics.com/nao-naoqi-2-1/nao-documentation/nao-technical-guide/nao-h25/h25-links
Predefined Postures:
    - https://developer.softbankrobotics.com/nao-naoqi-2-1/nao-documentation/nao-technical-guide/nao-technical-overview/predefined-postures
"""

__version__ = "0.0.0"
__author__ = 'ancient-sentinel'

# FRAMES
FRAME_TORSO = 0
"""
This frame is attached to the robot's torso reference, so it moves with
the robot as he walks and changes orientation as he leans. This space is
useful when you have very local tasks that make sense in the orientation
of the torso frame.
"""

FRAME_WORLD = 1
"""
This frame is in reference to a fixed origin that is never altered,
specifically, the world-position where the robot starts. It is left behind
when the robot walks, and will be different in z-rotation after the robot
has turned. This space is useful for calculations which require an external,
absolute frame of reference.
"""

FRAME_ROBOT = 2
"""
This frame is average of the two feet positions projected around a vertical
z-axis. This space is useful because the x-axis is always forwards, so
it provides a natural, ego-centric reference.
"""

FRAMES = (FRAME_TORSO, FRAME_WORLD, FRAME_ROBOT)
"""The set of all spatial frames."""

# MOVEMENT
MVT_RELATIVE = 0
"""Specifies that movement is relative to the current position."""

MVT_ABSOLUTE = 1
"""Specifies that movement is in reference to absolute position."""

# ANGLE TYPE
COMMANDS = 0,
SENSORS = 1

# AXIS MASK
AXIS_MASK_X = 1
"""Mask x-axis."""

AXIS_MASK_Y = 2
"""Mask y-axis."""

AXIS_MASK_Z = 4
"""Mask z-axis."""

AXIS_MASK_WX = 8
"""Mask x-axis rotation."""

AXIS_MASK_WY = 16
"""Mask y-axis rotation."""

AXIS_MASK_WZ = 32
"""Mask z-axis rotation."""

AXIS_MASK_ALL = 63
"""Mask x, y, z, wx, wy, and wz axes."""

AXIS_MASK_VEL = 7
"""Mask x, y, and z axes."""

AXIS_MASK_ROT = 56
"""Mask wx, wy, and wz rotation axes."""

# COMPUTING
TO_RAD = 0.01745329
"""The conversion factor for converting degrees to radians."""

TO_DEG = 57.295779513082323
"""The conversion factor for converting radians to degrees."""

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

EFFECTORS = (
    EF_HEAD, EF_TORSO,
    EF_LEFT_ARM, EF_LEFT_LEG,
    EF_RIGHT_ARM, EF_RIGHT_LEG
)
"""The set of all of the robot's effectors."""

# CHAINS
CHAIN_BODY = "Body"
"""The identifier for the body chain."""

CHAIN_LEGS = "Legs"
"""The identifier for the legs chain."""

CHAIN_ARMS = "Arms"
"""The identifier for the arms chain."""

CHAIN_LEFT_ARM = "LArm"
"""The identifier for the left arm chain."""

CHAIN_RIGHT_ARM = "RArm"
"""The identifier for the right arm chain."""

CHAIN_HEAD = "Head"
"""The identifier for the head chain."""

CHAINS = (
    CHAIN_BODY, CHAIN_HEAD,
    CHAIN_LEGS, CHAIN_ARMS,
    CHAIN_LEFT_ARM, CHAIN_RIGHT_ARM
)
"""The set of all of the robot's chain names."""

# PREDEFINED POSTURES
POSE_STAND = 'Stand'
"""The identifier for the predefined standing pose."""

POSE_STAND_INIT = 'StandInit'
"""The identifier for the predefined initial standing pose."""

POSE_STAND_ZERO = 'StandZero'
"""The identifier for the predefined zeroed standing pose."""

POSE_CROUCH = 'Crouch'
"""The identifier for the predefined crouching pose."""

POSE_SIT = 'Sit'
"""The identifier for the predefined sitting pose."""

POSE_SIT_RELAX = 'SitRelax'
"""The identifier for the predefined relaxed sitting pose."""

POSE_LYING_BELLY = 'LyingBelly'
"""The identifier for the predefined pose lying on the belly."""

POSE_LYING_BACK = 'LyingBack'
"""The identifier for the predefined pose lying on the back."""

PREDEFINED_POSES = (
    POSE_STAND, POSE_STAND_INIT, POSE_STAND_ZERO,
    POSE_CROUCH, POSE_SIT, POSE_SIT_RELAX,
    POSE_LYING_BACK, POSE_LYING_BELLY
)
"""The list of all predefined poses/postures."""


# DIMENSIONS
FOOT_HEIGHT = 0.04519
"""Foot height (m)."""

HAND_OFFSET_X = 0.05775
"""Hand offset in the x-axis (m)."""

HAND_OFFSET_Z = 0.01231
"""Hand offset in the z-axis (m)."""

# CONTEXT TYPES
CTYPE_ABSOLUTE = 'absolute'
"""Absolute context type. Used for absolute position or transform sequence contexts."""

CTYPE_ANY = 'any'
"""Any context type."""

CTYPE_NONE = 'none'
"""No context type."""

CTYPE_PLANAR = 'planar'
"""Planar context type. Used for planar position sequence contexts."""

CTYPES = [
    CTYPE_ABSOLUTE, CTYPE_ANY,
    CTYPE_NONE, CTYPE_PLANAR
]
"""The list of defined context types."""

# KEYFRAME TYPES
KFTYPE_NONE = 'none'
"""No keyframe type."""

KFTYPE_ABSOLUTE_POSITION = 'absolute.position'
"""Absolute position keyframe type. Indicates that the values of the keyframe are absolute positions."""

KFTYPE_ABSOLUTE_TRANSFORM = 'absolute.transform'
"""Absolute transform keyframe type. Indicates that the values of the keyframe are absolute transforms."""

KFTYPE_PLANAR = 'planar'
"""Planar keyframe type. Indicates that the values are coordinate pairs."""

KFTYPES = [
    KFTYPE_NONE, KFTYPE_ABSOLUTE_POSITION,
    KFTYPE_ABSOLUTE_TRANSFORM, KFTYPE_PLANAR
]
"""The list of defined keyframe types."""
