import procgen.data_types as data_types
import procgen.feature_model as feature_model
from fastapi import FastAPI, HTTPException

app = FastAPI()


@app.post("/check_feature_model")
async def check_fm(fm_json : data_types.FeatureModelType):
    sat: bool
    try:
        fm = feature_model.FeatureModel(fm_json)
        sat = fm.check_fm_satisfiability()
    except Exception as e:
        raise HTTPException(status_code=500, detail="Integral error " + str(e))
    return {"sat" : sat}

@app.post("/check_type_code_satisfy")
async def check_type_code(fm_json : data_types.FeatureModelType, spec : data_types.SpecifiationType):
    sat: bool
    try:
        fm = feature_model.FeatureModel(fm_json)
        sat = fm.check_spec_satisfy(spec)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Integral error " + str(e))
    return {"sat" : sat}