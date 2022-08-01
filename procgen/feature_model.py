from typing import List
import procgen.product as product
import procgen.specification as specification
import procgen.utils as utils

import re
import sympy
import sympy.abc
import sympy.logic.boolalg as boolalg
import sympy.logic.inference as inference

class FeatureModel:
    def __init__(self, model_path: str):
        self.all_symbols = []
        feature_model = utils.load_json_from_file_path(model_path)
        self.structure = feature_model["structure"]
        self.constraints = feature_model["constraints"]
        self.order_constraints = feature_model["order_constraints"]
        self.assembly_steps = feature_model["assembly_steps"]
        root = list(feature_model["structure"].keys())
        assert len(root) == 1, "There is more than one root of the feature model which makes it ambigous."

        self.boolean_fm = self.create_bool_from_fm(root[0])

    def create_bool_from_fm(self, root):
        expr = self.create_bool_from_structure(self.structure[root], root)
        for constraint_dict in self.constraints:
            constraint_expr = self.create_bool_from_list(constraint_dict)
            expr = boolalg.And(expr, constraint_expr)
        return expr
    
    def create_bool_from_list(self, constraint):
        assert len(constraint) == 3, "Only two nodes can participate in a link: " + " ".join(constraint)
        assert constraint[0] in ["req", "exc"], "Not supported connection type: " + constraint[0]
        x, y = sympy.symbols(constraint[1:])
        assert x in self.all_symbols or y in self.all_symbols, "Nodes of constraint do not exist: " + " ".join(constraint[1:])
        if constraint[0] == "req":
            return boolalg.Implies(x, y)
        elif constraint[0] == "exc":
            return boolalg.Not(boolalg.And(x, y))

    def create_bool_from_structure(self, root, parent_name:str):
        if "abstract" in root["meta"] and root["meta"]["abstract"]:
            parent_symbol = sympy.symbols(parent_name)
            symb = []
            nodes = list(root.keys())
            nodes.remove("meta")
            for n in nodes:
                name = parent_name + "/" + n
                symb.append(self.create_bool_from_structure(root[n], name))
            sub_expr1 = boolalg.false
            for s in symb:
                sub_expr1 = boolalg.Or(sub_expr1, s)
            sub_expr = boolalg.Equivalent(sub_expr1, parent_symbol)
            
            root_node_type = root["meta"]["type"]
            if root_node_type == "alt":
                sub_expr2 = boolalg.true
                for i in range(len(symb)):
                    for j in range(i+1,len(symb)):
                        sub_expr2 = boolalg.And(
                            sub_expr2,
                            boolalg.Not(boolalg.And(symb[i], symb[j])))
                sub_expr = boolalg.And(sub_expr, sub_expr2)
            elif root_node_type == "and":
                pass
            else:
                pass

            mandatory = "mandatory" in root["meta"] and root["meta"]["mandatory"]
            for s in symb:
                if mandatory:
                    sub_expr = boolalg.And(sub_expr,
                        boolalg.Equivalent(s, parent_symbol)
                    )
                else:
                    sub_expr = boolalg.And(
                        sub_expr, boolalg.Implies(s, parent_symbol)
                    )
            return sub_expr
        else:
            s = sympy.symbols(parent_name)
            self.all_symbols.append(s)
            return s

    def check_fm_satisfiability(self) -> bool:
        return True if inference.satisfiable(self.boolean_fm) else False

    def check_specification(self, specification: specification.Specification) -> bool:
        # self.boolean_representaion
        # evaluate boolean expression if it is satisfied by the specification

        return True

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
            for group, value in specification.__dataclass_fields__:
                #assembly_action = self.structure[][group]
                #prod = Product()
                #prod.features.add(
                #    Feature(attr, value, assembly)
                #)
                pass

            # create and return product with features
        else:
            pass
            # log error