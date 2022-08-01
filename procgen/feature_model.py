import procgen.product as product
import procgen.specification as specification
import procgen.utils as utils

import re
import json
import xml.etree.ElementTree as ET

class FeatureModel:
    def __init__(self, model_path: str):
        # parse xml
        # check
        # self.boolean_representaion = self.create_boolean_expression_from_feature_model()
        feature_model = utils.load_json_from_file_path(model_path)
        self.structure = feature_model["structure"]
        self.constraints = feature_model["constraints"]
        self.order_constraints = feature_model["order_constraints"]

    def create_boolean_expression_from_feature_model(self): # some return type, depends on the library used for CNF
        pass

    def check_feature_model(self) -> bool:
        pass
        # self.boolean_representaion
        # evaluate boolean expression, return whether it is satisfiable

    def check_specification(self, specification: specification.Specification) -> bool:
        pass
        # self.boolean_representaion
        # evaluate boolean expression if it is satisfied by the specification

    def parse_type_code(self, type_code:str) -> specification.Specification:
        groups = re.split(r"\s|/|(?!\s)-(?!\s)", type_code)
        spec = specification.Specification()
        spec.controller = groups.pop(0)
        spec.controller_spring = groups.pop(0)
        pr = self.structure["PSx"]["SpoolBlock"]["PressureRelief"]
        for _ in range(2):
            for feature in pr:
                if feature != "meta":
                    f = feature.strip(".")
                    matches = re.match(f + r"\d{1,3}", groups[0])
                    if matches:
                        spec.dbv += "" if spec.dbv == "" else " "
                        spec.dbv += groups.pop(0)
        spec.wv = groups.pop(0)
        spec.actuation = groups.pop(0)
        spec.magnet = groups.pop(0) if groups else ""
        return spec


    def create_product(self, specification: specification.Specification) -> product.Product:
        if self.check_specification(specification):
            pass
            # create and return product with features
        else:
            pass
            # log error