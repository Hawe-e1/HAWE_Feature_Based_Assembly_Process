import procgen.data_types as data_types
import procgen.feature_model as feature_model
from fastapi import FastAPI, HTTPException

app = FastAPI()


@app.post("/check/feature_model")
async def check_fm(fm_json: data_types.FeatureModelType):
    sat: bool
    try:
        fm = feature_model.FeatureModel(fm_json)
        sat = fm.check_fm_sat()
    except Exception as e:
        raise HTTPException(status_code=500, detail="Integral error " + str(e))
    return sat


@app.post("/check/type_code_satisfy")
async def check_type_code(
    fm_json: data_types.FeatureModelType, spec: data_types.SpecificationType
):
    sat: bool
    try:
        fm = feature_model.FeatureModel(fm_json)
        sat = fm.check_spec_sat(spec)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Integral error " + str(e))
    return sat


@app.post("/get/number_of_feature_groups")
async def get_num_groups(fm_json: data_types.FeatureModelType):
    num: int
    try:
        fm = feature_model.FeatureModel(fm_json)
        num = fm.get_number_of_feature_groups()

    except Exception as e:
        raise HTTPException(status_code=500, detail="Integral error " + str(e))
    return num


@app.post("/get/assembly_steps")
async def get_assembly_steps(
    fm_json: data_types.FeatureModelType, spec: data_types.SpecificationType
):
    assembly_steps:data_types.AssemblyProcessType
    try:
        fm = feature_model.FeatureModel(fm_json)
        assembly_steps = fm.get_assembly_process(spec)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Integral error " + str(e))
    return assembly_steps
