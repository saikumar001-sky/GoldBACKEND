
from enum import Enum

class Gender(str, Enum):
    MALE:str = "Male"
    FEMALE:str = "Female"
    
class MartialStatus(str, Enum):
    SINGLE:str = "Single"
    MARRIED:str = "Married"