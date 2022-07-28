
import procgen

if __name__ == "__main__":
    type_codes = procgen.utils.load_typcodes_from_file("data\example_type_codes.txt")
    print(type_codes[0])
    specification = procgen.type_code_parser.parse_type_code(type_codes[0])
    print(specification)
    procgen.feature_model.FeatureModel("data/model.xml")

