from time import time
import procgen.utils
import procgen.data_types
import procgen.feature_model

import sympy

if __name__ == "__main__":
    feature_model_json = procgen.utils.load_json_from_file_path(
        "data/small_feature_model.json"
    )
    feature_model = procgen.data_types.FeatureModelType(**feature_model_json)
    fm = procgen.feature_model.FeatureModel(feature_model)

    spec = procgen.data_types.SpecificationType(
        features={
            "R/A1": "B1",
            "R": "A2",
        }
    )

    # spec = procgen.data_types.SpecificationType(features={"A": "B"})
    # print(fm.create_bool_from_fm())
    fm.get_names_of_feature_groups()
    print()
    print(fm.get_bool_from_spec(spec, fill_not_choosen_with_false=True))

    print(list(fm.get_possible_spec_sat(spec, fill_not_choosen_with_false=True)))

    print(len(list(fm.get_possible_spec_sat(spec, fill_not_choosen_with_false=True))))

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
    # expression = fm.create_bool_from_fm()
