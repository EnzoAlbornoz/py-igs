# Import Dependencies
from enum import unique, IntEnum
# Define Enum
@unique
class EClippingMethod(IntEnum):
    NONE = 0
    POINT_CLIP = 1
    