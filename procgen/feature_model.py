from typing import Dict, List, Set, Tuple
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
        self.structure_root_id = roots[0]
        self.structure_root_name = self.structure[self.structure_root_id].meta.name
        self.root = self.structure[self.structure_root_id]

    def create_bool_from_fm(self):
        expr, _, _ = self.create_bool_from_structure(
            self.root, self.structure_root_name
        )
        for constraint_dict in self.constraints:
            constraint_expr = self.create_bool_from_list(constraint_dict, expr.atoms())
            expr = boolalg.And(expr, constraint_expr)
        return expr

    def create_bool_from_list(
        self, constraint: data_types.ConstraintType, all_symbols: Set[sympy.Symbol]
    ) -> boolalg.Implies | boolalg.Not:
        if len(constraint.variables) < 2:
            raise ValueError(
                "At least two nodes can participate in a link: "
                + " ".join(constraint.variables)
            )

        x, *y = sympy.symbols(constraint.variables[1:])
        if x not in all_symbols or any([yi not in all_symbols for yi in y]):
            raise ValueError(
                "Nodes of constraint do not exist: " + " ".join(constraint.variables)
            )

        if constraint.type == "req":
            return boolalg.Implies(x, y)
        elif constraint.type == "exc":
            return boolalg.Not(boolalg.And(x, y))
        else:
            raise ValueError("Did not recognise constraint type: " + constraint.type)

    def create_bool_from_structure(
        self, root: data_types.StructureType, parent_name: str
    ):
        """Recursively reates a sympy boolean expression from the feature model

        Args:
            root (data_types.StructureType): The root of the model
            parent_name (str): The name of the root, later called

        Raises:
            ValueError: On malformed or missing data

        Returns:
            sympy boolean expression
        """
        if root.meta.abstract and root.nodes:
            parent_symbol: sympy.Symbol = sympy.symbols(parent_name)
            sub_expr = []
            for node in root.nodes.values():
                qualified_name = parent_name + "/" + node.meta.name
                sub_expr.append(self.create_bool_from_structure(node, qualified_name))

            # rules
            # mandatory / optional connection
            mandatory = boolalg.true
            optional = boolalg.true
            for s, mand, _ in sub_expr:
                if mand:
                    mand_eq = boolalg.Equivalent(s, parent_symbol)
                    mandatory = boolalg.And(mandatory, mand_eq)
                else:
                    opt_imp = boolalg.Implies(s, parent_symbol)
                    optional = boolalg.And(optional, opt_imp)
            mand_opt_expr = boolalg.And(mandatory, optional)

            # any kind of subfeatures
            or_sub_expr = boolalg.false
            for s, _, _ in sub_expr:
                or_sub_expr = boolalg.Or(or_sub_expr, s)
            subfeature_expr = boolalg.Equivalent(or_sub_expr, parent_symbol)
            if root.meta.type == "alt":
                # alternative subfeatures
                alt_expr = boolalg.true
                for i in range(len(sub_expr)):
                    for j in range(i + 1, len(sub_expr)):
                        alt_expr = boolalg.And(
                            alt_expr,
                            boolalg.Not(boolalg.And(sub_expr[i][0], sub_expr[j][0])),
                        )
            elif root.meta.type == "and":
                alt_expr = boolalg.true
            else:
                alt_expr = boolalg.true

            ret_expression = boolalg.And(
                parent_symbol, mand_opt_expr, subfeature_expr, alt_expr
            )

            return ret_expression, root.meta.mandatory, True

        else:
            ret_expression = sympy.symbols(parent_name)
            return ret_expression, root.meta.mandatory, False

    def check_fm_sat(
        self, *, all_models: bool = False
    ) -> bool | Dict[sympy.Symbol, bool]:
        """Checks whether a given feature model a satisfiable

        Args:
            all_models (bool, optional): Flag to decide whether all the possible models are returned, or just a boolean value. Defaults to False.

        Returns:
            bool | Dict[sympy.Symbol, bool]: The result of the check
        """
        boolean_fm = self.create_bool_from_fm()
        models = inference.satisfiable(boolean_fm, all_models=all_models)
        if not all_models:
            return True if models else False
        else:
            return models

    def extend_bool_spec_from_fm(
        self,
        root: data_types.StructureType,
        parent_name: str,
        boolean_spec: Dict[str, bool],
        connection_type: str = "",
        fill_not_choosen_with_false: bool = False,
    ) -> Dict[str, bool]:
        if root.meta.abstract and root.nodes:
            subs: Dict[str, bool] = {}
            # if root.meta.mandatory:
            #    subs.update({parent_name: True})
            for node in root.nodes.values():
                subs.update(
                    self.extend_bool_spec_from_fm(
                        node,
                        parent_name + "/" + node.meta.name,
                        boolean_spec,
                        root.meta.type,
                        fill_not_choosen_with_false,
                    )
                )
            return subs
        else:
            if parent_name in boolean_spec:
                return {parent_name: boolean_spec[parent_name]}
            elif parent_name not in boolean_spec and connection_type == "alt":
                return {parent_name: False}
            elif (
                parent_name not in boolean_spec
                and connection_type == "and"
                and fill_not_choosen_with_false
            ):
                return {parent_name: False}
            else:
                return {}

    def parse_specification(
        self, unparsed_spec: data_types.UnparsedSpecificationType
    ) -> data_types.SpecificationType:
        parsed_spec_dict: Dict[str, List[str]] = {}
        for feat_name, feat_specs in unparsed_spec.features.items():
            parsed_spec_dict[feat_name] = feat_specs.split(" ")
        return data_types.SpecificationType(features=parsed_spec_dict)

    def get_bool_from_spec(
        self,
        spec: data_types.SpecificationType,
        *,
        fill_not_choosen_with_false: bool = False,
    ) -> Dict[str, bool]:
        """Creates a substitution into a boolean expression based on a specification and the feature model

        Args:
            spec (data_types.SpecificationType): The specificatino
            fill_not_choosen_with_false (bool, optional): Flag to chose how to handle varuables without substitution, fill them with False. Defaults to False.

        Returns:
            Dict[str, bool]: The retourned
        """

        group_names = self.get_names_of_feature_groups()
        print(group_names)
        if group_names is None:
            raise ValueError("There is no specifiable group within the feature model.")
        boolean_spec: Dict[str, bool] = {}
        for feat, specs in spec.features.items():
            if feat in group_names:
                for val in specs:
                    boolean_spec.update({feat + "/" + val: True})
            else:
                raise ValueError("Group name is not a specifiable feature: " + feat)

        boolean_spec = self.extend_bool_spec_from_fm(
            self.root,
            self.structure_root_name,
            boolean_spec,
            fill_not_choosen_with_false=fill_not_choosen_with_false,
        )
        return boolean_spec

    def get_possible_spec_sat(
        self,
        spec: data_types.SpecificationType,
        *,
        fill_not_choosen_with_false: bool = False,
    ):
        """Returns whether the specification satisfies the feature model

        Args:
            spec (data_types.SpecificationType): The specification
            fill_not_choosen_with_false (bool, optional): Flag to chose how to handle varuables without substitution, fill them with False . Defaults to False.

        Returns:
            satisfiability : sympy logic inference satisfiable
        """
        boolean_fm = self.create_bool_from_fm()
        boolean_spec_for_sub = self.get_bool_from_spec(
            spec, fill_not_choosen_with_false=fill_not_choosen_with_false
        )
        boolean_fm = boolean_fm.subs(list(boolean_spec_for_sub.items()))
        return inference.satisfiable(boolean_fm, all_models=True)

    def check_spec_sat(self, spec: data_types.SpecificationType) -> bool:
        models = self.get_possible_spec_sat(spec)
        return True if next(models) else False

    def get_names_of_feature_groups(self) -> List[str]:
        group_names = self.collect_names_of_feature_groups(
            self.root, self.structure_root_name
        )
        if group_names is not None:
            return group_names
        else:
            return []

    def collect_names_of_feature_groups(
        self, root: data_types.StructureType, parent_name: str
    ) -> List[str] | None:
        """Recursively collects the names of the nodes which can be specified by a specification

        Args:
            root (data_types.StructureType): The root of the feature model
            parent_name (str): The name of the root node

        Returns:
            List[str] | None: The names of the nodes
        """
        if root.meta.abstract and root.nodes:
            vals: List[Tuple[str, List[str]]] = []
            for node in root.nodes.values():
                children_names = self.collect_names_of_feature_groups(
                    node, node.meta.name
                )
                if children_names is not None:
                    vals.append((parent_name, children_names))
            if any(map(lambda x: x[1] == [], vals)):
                return [parent_name] + [
                    parent_name + "/" + child
                    for parent_name, children_names in vals
                    if children_names != []
                    for child in children_names
                ]
            else:
                return [
                    parent_name + "/" + child
                    for parent_name, children_names in vals
                    for child in children_names
                ]
        elif not root.meta.abstract:
            return []
        else:
            return None

    def create_features_for_product(
        self, spec: data_types.SpecificationType
    ) -> List[data_types.FeatureType]:
        if self.check_spec_sat(spec):
            features: List[data_types.FeatureType] = []
            for node_path, feature_spec in spec.features.items():
                node_path_list = node_path.split("/")[1:]
                node = self.recurse_into_fm(self.root, node_path_list)
                if node.nodes:
                    for selected_feature_name in feature_spec:
                        selected_feature = None
                        for possible_node in node.nodes.values():
                            if possible_node.meta.name == selected_feature_name:
                                selected_feature = possible_node
                                break
                        if selected_feature is None:
                            raise ValueError(
                                "Node not found with name: " + selected_feature_name
                            )

                        if selected_feature.meta.assembly_action:
                            assembly_action = selected_feature.meta.assembly_action
                        else:
                            raise ValueError(
                                "Assembly action not specified for feature: "
                                + node_path
                            )
                        features.append(
                            data_types.FeatureType(
                                group=node_path,
                                selected_feature=selected_feature_name,
                                assembly_action=assembly_action,
                            )
                        )
                else:
                    pass
            return features
        else:
            raise ValueError(
                "The specification is not consistent, it is impossible to satisfy the feature model with the given type code."
            )

    def recurse_into_fm(
        self, root: data_types.StructureType, list_of_nodes: List[str]
    ) -> data_types.StructureType:
        if len(list_of_nodes) == 0:
            return root
        else:
            node_name = list_of_nodes[0]
            if root.nodes:
                for possible_node in root.nodes.values():
                    if possible_node.meta.name == node_name:
                        return self.recurse_into_fm(possible_node, list_of_nodes[1:])

            raise IndexError("The node key list is not correct")

    def create_assembly_order(
        self, spec: data_types.SpecificationType
    ) -> data_types.AssemblyActionOrderType:
        default_order = self.order_constraints.default
        temp_orders: Dict[str, Set[int]] = {action: set() for action in default_order}
        spec_feature_names: Set[str] = set()
        for group, features in spec.features.items():
            for feat in features:
                spec_feature_names.add("/".join([group, feat]))

        for constraint in self.order_constraints.constraints:
            if len(default_order) != len(constraint.order):
                raise ValueError(
                    "The length of the constraint does not match the length of the default order: "
                    + " ".join(constraint.order)
                )
            variables = set(constraint.variables)
            var_in_feat = [var in spec_feature_names for var in variables]
            if (constraint.type == "and" and variables and all(var_in_feat)) or (
                constraint.type == "or" and variables and any(var_in_feat)
            ):
                for i, action in enumerate(constraint.order):
                    if action in temp_orders:
                        temp_orders[action].add(i)
                    else:
                        ValueError(
                            "The order constraint contains an unkown action: " + action
                        )
        print(temp_orders)
        final_order: List[str] = ["" for _ in range(len(default_order))]
        for action, indicies in temp_orders.items():
            if len(indicies) == 0:
                final_order[default_order.index(action)] = action
            elif len(indicies) == 1:
                final_order[list(indicies)[0]] = action
            else:
                raise ValueError("Unsatisfiable order constraints.")
        return data_types.AssemblyActionOrderType(final_order)

    def create_product(
        self, spec: data_types.SpecificationType
    ) -> data_types.ProductType:
        features = self.create_features_for_product(spec)
        order = self.create_assembly_order(spec)
        return data_types.ProductType(features=features, assembly_order=order)

    def create_assembly_process(
        self, prod: data_types.ProductType
    ) -> data_types.AssemblyProcessType:
        """Creaets an assembly process from a specification using the assembly actions

        Args:
            prod (data_types.ProductType): The product that will be used for the assembly

        Raises:
            ValueError: If the assembly action specified in the feature is not present in the assembly actions list

        Returns:
            data_types.AssemblyProcessType: The final assembly process
        """
        assembly_actions: List[data_types.AssemblyActionStepType] = [
            data_types.AssemblyActionStepType({}) for _ in range(len(prod.features))
        ]
        for fet in prod.features:
            if fet.assembly_action not in prod.assembly_order:
                raise ValueError("Unkown assembly action: " + fet.assembly_action)
            final_action = fet.assembly_action.replace("_", fet.selected_feature)
            assembly_actions[prod.assembly_order.index(fet.assembly_action)].update(
                {final_action: self.assembly_steps[fet.assembly_action]}
            )
        return data_types.AssemblyProcessType(assembly_actions)

    def get_assembly_process(
        self, spec: data_types.SpecificationType
    ) -> data_types.AssemblyProcessType:
        prod = self.create_product(spec)
        return self.create_assembly_process(prod)
