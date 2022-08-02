from typing import Dict, List, OrderedDict, Set, Tuple
from procgen import data_types

import sympy
import sympy.abc
import sympy.logic.boolalg as boolalg
import sympy.logic.inference as inference


class FeatureModel:
    def __init__(self, feature_model: data_types.FeatureModelType):
        self.structure = feature_model.structure
        self.constraints = feature_model.constraints
        self.order_constraints = feature_model.order_constraints
        self.assembly_steps = feature_model.assembly_steps
        roots = list(feature_model.structure.keys())
        if len(roots) != 1:
            raise ValueError(
                "There is not exactly one root of the feature model which makes it ambigous. Number of roots: "
                + str(len(roots))
            )
        self.structure_root_name = roots[0]

    def create_bool_from_fm(self):
        expr = self.create_bool_from_structure(
            self.structure[self.structure_root_name], self.structure_root_name
        )
        for constraint_dict in self.constraints:
            constraint_expr = self.create_bool_from_list(constraint_dict, expr.atoms())
            expr = boolalg.And(expr, constraint_expr)
        return expr

    def create_bool_from_list(
        self, constraint: List[str], all_symbols: Set[sympy.Symbol]
    ) -> boolalg.Implies | boolalg.Not:
        if len(constraint) != 3:
            raise ValueError(
                "Only two nodes can participate in a link: " + " ".join(constraint)
            )

        x, y = sympy.symbols(constraint[1:])
        if x not in all_symbols or y not in all_symbols:
            raise ValueError(
                "Nodes of constraint do not exist: " + " ".join(constraint[1:])
            )

        if constraint[0] == "req":
            return boolalg.Implies(x, y)
        elif constraint[0] == "exc":
            return boolalg.Not(boolalg.And(x, y))
        else:
            raise ValueError("Did not recognise constraint type: " + constraint[0])

    def create_bool_from_structure(
        self, root: data_types.StructureType, parent_name: str
    ):
        if "abstract" in root.meta and root.meta["abstract"] and root.nodes:
            parent_symbol: sympy.Symbol = sympy.symbols(parent_name)
            symb: List[sympy.Symbol] = []
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

            # BUG: This is not correct, here we assume that all children have mandatory flags
            mandatory = "mandatory" in root.meta and root.meta["mandatory"]
            for s in symb:
                if mandatory:
                    sub_expr = boolalg.And(
                        sub_expr, boolalg.Equivalent(s, parent_symbol)
                    )
                else:
                    sub_expr = boolalg.And(sub_expr, boolalg.Implies(s, parent_symbol))
            return sub_expr
        else:
            s: sympy.Symbol = sympy.symbols(parent_name)
            return s

    def check_fm_sat(
        self, *, all_models: bool = False
    ) -> bool | Dict[sympy.Symbol, bool]:
        boolean_fm = self.create_bool_from_fm()
        models = inference.satisfiable(boolean_fm, all_models=all_models)
        if not all_models:
            return True if models else False
        else:
            return models

    def create_bool_from_spec(
        self, spec: data_types.SpecificationType
    ) -> Dict[str, bool]:
        group_names = self.get_names_of_feature_groups()
        boolean_spec: Dict[str, bool] = {}
        for feat, val in spec.features.items():
            if feat in group_names:
                boolean_spec.update({feat + "/" + val: True})
            else:
                raise ValueError("Group name is not a specifiable feature: " + feat)
        return boolean_spec

    def extend_bool_spec_from_fm(
        self,
        root: data_types.StructureType,
        parent_name: str,
        boolean_spec: Dict[str, bool],
        connection_type: str = "",
    ) -> Dict[str, bool]:
        if "abstract" in root.meta and root.meta["abstract"] and root.nodes:
            if (
                "type" not in root.meta
                or not isinstance(root.meta["type"], str)
                or root.meta["type"] not in ["and", "alt"]
            ):
                raise ValueError(
                    'The "type" information in "meta" is either missing, not a string, or not "and" or "alt": '
                    + parent_name
                    + "\n"
                    + str(root.meta)
                )
            else:
                subs: Dict[str, bool] = {}
                for name, node in root.nodes.items():
                    subs.update(
                        self.extend_bool_spec_from_fm(
                            node,
                            parent_name + "/" + name,
                            boolean_spec,
                            root.meta["type"],
                        )
                    )
                return subs
        else:
            if parent_name in boolean_spec:
                return {parent_name: boolean_spec[parent_name]}
            elif parent_name not in boolean_spec and connection_type == "alt":
                return {parent_name: False}
            else:
                return {}

    def get_bool_from_spec(self, spec: data_types.SpecificationType) -> Dict[str, bool]:
        boolean_spec = self.create_bool_from_spec(spec)
        boolean_spec = self.extend_bool_spec_from_fm(
            self.structure[self.structure_root_name],
            self.structure_root_name,
            boolean_spec,
        )
        return boolean_spec

    def get_possible_spec_sat(self, spec: data_types.SpecificationType):
        boolean_fm = self.create_bool_from_fm()
        boolean_spec_for_sub = self.create_bool_from_spec(spec)
        boolean_fm = boolean_fm.subs(list(boolean_spec_for_sub.items()))

        return inference.satisfiable(boolean_fm, all_models=True)

    def check_spec_sat(self, spec: data_types.SpecificationType) -> bool:
        models = self.get_possible_spec_sat(spec)
        return True if next(models) else False

    def get_names_of_feature_groups(self) -> List[str]:
        return self.collect_names_of_feature_groups(
            self.structure[self.structure_root_name], self.structure_root_name
        )

    def collect_names_of_feature_groups(
        self, root: data_types.StructureType, parent_name: str
    ) -> List[str]:
        if "abstract" in root.meta and root.meta["abstract"] and root.nodes:
            vals: List[Tuple[str, List[str]]] = []
            for name, node in root.nodes.items():
                vals.append(
                    (parent_name, self.collect_names_of_feature_groups(node, name))
                )
            if all(map(lambda x: x[1] == [], vals)):
                return [parent_name]
            else:
                return [
                    parent_name + "/" + child
                    for parent_name, children_names in vals
                    for child in children_names
                ]
        else:
            return []

    def create_product(
        self, spec: data_types.SpecificationType
    ) -> data_types.ProductType:
        if self.check_spec_sat(spec):
            for feature_spec in spec.features:

                pass
            # create and return product with features
        else:
            raise ValueError(
                "The specification is not consistent, it is impossible to satisfy the feature model with the given type code."
            )

    def get_assembly_process(
        self, spec: data_types.SpecificationType
    ) -> data_types.AssemblyProcessType:
        prod = self.create_product(spec)
        order = self.create_assembly_order(prod)
        return self.create_assembly_process(prod, order)

    def create_assembly_order(
        self, prod: data_types.ProductType
    ) -> OrderedDict[str, List[str]]:
        pass

    def create_assembly_process(
        self, prod: data_types.ProductType, order
    ) -> data_types.AssemblyProcessType:
        pass
