
from dataclasses import dataclass


@dataclass
class Specification:
    actuator : str
    controller_spring : str
    dbv : str
    wv : str
    actuation : str
    magnet : str
    def get_boolean_representaion(self):  # some return type, depends on the library used for CNF
        pass