import procgen.product as product
import procgen.specification as specification

import xml.etree.ElementTree

class FeatureModel:
    def __init__(self, xml_model: xml.etree.ElementTree.ElementTree):
        pass
        # parse xml
        # check
        # self.boolean_representaion = self.create_boolean_expression_from_feature_model()

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

    def create_product(self, specification: specification.Specification) -> product.Product:
        if self.check_specification(specification):
            pass
            # create and return product with features
        else:
            pass
            # log error