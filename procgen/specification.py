
from dataclasses import dataclass
from typing import Dict, List

@dataclass
class Specification:
    controller : str = ""
    controller_spring : str = ""
    wv : str = ""
    dbv : str = ""
    actuation : str = ""
    magnet : str = ""