
import procgen

if __name__ == "__main__":
    type_codes = procgen.utils.load_typcodes_from_file_path("data/example_type_codes.txt")
    #print(type_codes[0])
    feature_model = utils.load_json_from_file_path("data/small_feature_model.json")
    fm = procgen.feature_model.FeatureModel(feature_model)
    print(fm.check_fm_satisfiability())
    #for tc in type_codes:
    #    print(tc)
    #    specification = fm.parse_type_code(tc)
    #    print(specification)
    
