import procgen.utils
import procgen.data_types
import procgen.feature_model

import sympy

if __name__ == "__main__":
    feature_model_json = procgen.utils.load_json_from_file_path(
        "data/very_small_feature_model.json"
    )
    feature_model = procgen.data_types.FeatureModelType(**feature_model_json)
    fm = procgen.feature_model.FeatureModel(feature_model)

    spec = procgen.data_types.SpecificationType(
        features={
            "Actuation/AG1": "E",
            "Actuation/AG2": "P",
            "Actuation/AG3": "F",
            "Actuation/AG4": "MM",
            "Actuation/AG7": "UNF",
            "Actuation/AG8": "empty",
        }
    )
    spec = procgen.data_types.SpecificationType(features={"A": "B"})
    print(spec)
    print(fm.get_bool_from_spec(spec))
    print(list(fm.get_possible_spec_sat(spec)))
    print(fm.check_spec_sat(spec))

    print(list(fm.check_fm_sat(all_models=True)))
    print()
    A, B, C = sympy.symbols("A,A/B,A/C")
    manual_expression_opt_and = sympy.Equivalent((B | C), A) & ~(B & C)
    manual_expression_opt_alt = (
        sympy.Implies(B, A)
        & sympy.Implies(C, A)
        & sympy.Equivalent(B | C, A)
        & ~(B & C)
    )
    manual_expression_man_and = (
        sympy.Equivalent(B, A) & sympy.Equivalent(C, A) & sympy.Equivalent((B | C), A)
    )
    manual_expression_man_alt = (
        sympy.Equivalent(B, A)
        & sympy.Equivalent(C, A)
        & sympy.Equivalent(B | C, A)
        & ~(B & C)
    )
    expression = fm.create_bool_from_fm()
    print(expression)
    print(manual_expression_man_and)
    print()
    print()
    [
        print(x)
        for x in list(sympy.logic.inference.satisfiable(expression, all_models=True))
    ]
    print()
    [
        print(x)
        for x in list(
            sympy.logic.inference.satisfiable(
                manual_expression_man_and, all_models=True
            )
        )
    ]
