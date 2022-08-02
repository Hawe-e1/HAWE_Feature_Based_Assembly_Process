from typing import Dict, List
from procgen import data_types
import procgen.product as product
import procgen.specification as specification

import re
import sympy
import sympy.abc
import sympy.logic.boolalg as boolalg
import sympy.logic.inference as inference


class FeatureModel:
    def __init__(self, feature_model: data_types.FeatureModelType):
        self.all_symbols = []

        self.structure = feature_model.structure
        self.constraints = feature_model.constraints
        self.order_constraints = feature_model.order_constraints
        self.assembly_steps = feature_model.assembly_steps
        roots = list(feature_model.structure.keys())
        assert (
            len(roots) == 1
        ), "There is more than one root of the feature model which makes it ambigous."

        self.structure_root_name = roots[0]
        self.boolean_fm = self.create_bool_from_fm(self.structure_root_name)
        self.num_feature_groups = self.count_number_of_feature_groups(self.structure[self.structure_root_name])
        print(self.num_feature_groups)

    def create_bool_from_fm(self, root:str):
        expr = self.create_bool_from_structure(self.structure[root], root)
        for constraint_dict in self.constraints:
            constraint_expr = self.create_bool_from_list(constraint_dict)
            expr = boolalg.And(expr, constraint_expr)
        return expr

    def create_bool_from_list(self, constraint:List[str]):
        assert (
            len(constraint) == 3
        ), "Only two nodes can participate in a link: " + " ".join(constraint)
        assert constraint[0] in ["req", "exc"], (
            "Not supported connection type: " + constraint[0]
        )
        x, y = sympy.symbols(constraint[1:])
        assert (
            x in self.all_symbols or y in self.all_symbols
        ), "Nodes of constraint do not exist: " + " ".join(constraint[1:])
        if constraint[0] == "req":
            return boolalg.Implies(x, y)
        elif constraint[0] == "exc":
            return boolalg.Not(boolalg.And(x, y))

    def create_bool_from_structure(self, root:data_types.StructureType, parent_name: str):
        if "abstract" in root.meta and root.meta["abstract"] and root.nodes:
            parent_symbol = sympy.symbols(parent_name)
            symb = []
            nodes = list(root.nodes.keys())
            for n in nodes:
                name = parent_name + "/" + n
                symb.append(self.create_bool_from_structure(root.nodes[n], name))
            sub_expr1 = boolalg.false
            for s in symb:
                sub_expr1 = boolalg.Or(sub_expr1, s)
            sub_expr = boolalg.Equivalent(sub_expr1, parent_symbol)

            root_node_type = root.meta["type"]
            if root_node_type == "alt":
                sub_expr2 = boolalg.true
                for i in range(len(symb)):
                    for j in range(i + 1, len(symb)):
                        sub_expr2 = boolalg.And(
                            sub_expr2, boolalg.Not(boolalg.And(symb[i], symb[j]))
                        )
                sub_expr = boolalg.And(sub_expr, sub_expr2)
            elif root_node_type == "and":
                pass
            else:
                pass

            mandatory = "mandatory" in root.meta and root.meta["mandatory"]
            for s in symb:
                if mandatory:
                    sub_expr = boolalg.And(
                        sub_expr, boolalg.Equivalent(s, parent_symbol)
                    )
                else:
                    sub_expr = boolalg.And(sub_expr, boolalg.Implies(s, parent_symbol))
            self.all_symbols.append(sympy.symbols(parent_name))
            return sub_expr
        else:
            s = sympy.symbols(parent_name)
            self.all_symbols.append(s)
            return s

    def check_fm_satisfiability(self) -> bool:
        return True if inference.satisfiable(self.boolean_fm) else False

    def check_spec_satisfy(self, specification: data_types.SpecifiationType) -> bool:
        # self.boolean_representaion
        # evaluate boolean expression if it is satisfied by the specification

        return True

    def count_number_of_feature_groups(self, root:data_types.StructureType) -> int:
        if "abstract" in root.meta and root.meta["abstract"] and root.nodes:
            vals:List[int] = []
            for n in root.nodes.values():
                vals.append(self.count_number_of_feature_groups(n))
            print(vals)
            if all(map(lambda x: x == 0, vals)):
                return 1
            else:
                return sum(vals)
        else:
            return 0

    def parse_type_code(self, type_code: str) -> specification.Specification:
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

    def create_product(
        self, specification: specification.Specification
    ) -> product.Product:
        if self.check_spec_satisfy(specification):
            for group, value in specification.__dataclass_fields__:
                # assembly_action = self.structure[][group]
                # prod = Product()
                # prod.features.add(
                #    Feature(attr, value, assembly)
                # )
                pass

            # create and return product with features
        else:
            pass
            # log error
