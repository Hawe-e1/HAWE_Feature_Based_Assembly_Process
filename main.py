import procgen
import uvicorn


if __name__ == "__main__":
    uvicorn.run("procgen.api:app", port=8000, log_level="info")

    type_codes = procgen.utils.load_typcodes_from_file_path("data/example_type_codes.txt")
    #print(type_codes[0])
    feature_model_json = procgen.utils.load_json_from_file_path("data/feature_model.json")
    feature_model = procgen.data_types.FeatureModel(feature_model_json)
    fm = procgen.feature_model.FeatureModel(feature_model)
    print(fm.check_fm_satisfiability())
    #for tc in type_codes:
    #    print(tc)
    #    specification = fm.parse_type_code(tc)
    #    print(specification)
    
