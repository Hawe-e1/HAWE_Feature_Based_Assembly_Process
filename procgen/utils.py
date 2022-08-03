import json

from typing import List


def load_typcodes_from_file_path(file_path: str) -> List[str]:
    type_codes: List[str] = []
    with open(file_path, "r") as file:
        type_codes.extend(map(lambda x: x.strip("\n"), file.readlines()))
    return type_codes


def load_json_from_file_path(file_path: str):
    with open(file_path, "r") as file:
        return json.loads(file.read())


def pprint_dict(d, indent: int = 4):
    print(json.dumps(d, sort_keys=True, indent=indent))


def get_all_substrings(input_string: str) -> List[str]:
    length = len(input_string)
    subs = [input_string[i : j + 1] for i in range(length) for j in range(i, length)]
    subs = sorted(subs, key=lambda s: len(s), reverse=True)
    return subs
