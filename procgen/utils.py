

from typing import List


def load_typcodes_from_file(file_path:str) -> List[str]:
    type_codes:List[str] = []
    with open(file_path, "r") as file:
        type_codes.extend(map(lambda x: x.strip("\n"), file.readlines()))
    return type_codes