
import procgen

if __name__ == "__main__":
    type_codes = procgen.utils.load_typcodes_from_file_path("data/example_type_codes.txt")
    print(type_codes[0])
    fm = procgen.feature_model.FeatureModel("data/feature_model.json")
    for tc in type_codes:
        print(tc)
        specification = fm.parse_type_code(tc)
        print(specification)
    
