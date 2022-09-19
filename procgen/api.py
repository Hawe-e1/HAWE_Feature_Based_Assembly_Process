"""
@Authors: A’Qilah Ahmad Dahalan, Jaime Aparicio Estrems, Benjamin Baffy, Sumit Gore, Matteo Mastroguiseppe
@Date: 2022.09.19
@Links: https://github.com/Hawe-e1/HAWE_Feature_Based_Assembly_Process
"""

from typing import Dict, List
import procgen.data_types as data_types
import procgen.feature_model as feature_model
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.concurrency import run_in_threadpool

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"status": "Stable"}


@app.post("/check/feature_model", response_model=bool)
async def check_fm(fm_json: data_types.FeatureModelType):
    try:
        fm = feature_model.FeatureModel(fm_json)
        sat = await run_in_threadpool(fm.check_fm_sat)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Integral error " + str(e))
    return sat


@app.post("/check/type_code_satisfy", response_model=bool)
async def check_type_code(
    fm_json: data_types.FeatureModelType, spec: data_types.UnparsedSpecificationType
):
    sat: bool
    try:
        fm = feature_model.FeatureModel(fm_json)
        parsed_spec = fm.parse_specification(spec)
        sat = fm.check_spec_sat(parsed_spec)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Integral error " + str(e))
    return sat


@app.post("/get/number_of_feature_groups", response_model=int)
async def get_num_groups(fm_json: data_types.FeatureModelType):
    num: int
    try:
        fm = feature_model.FeatureModel(fm_json)
        num = len(fm.get_names_of_feature_groups())

    except Exception as e:
        raise HTTPException(status_code=500, detail="Integral error " + str(e))
    return num


@app.post("/get/feature_group_names", response_model=List[str])
async def get_feature_group_names(fm_json: data_types.FeatureModelType):
    feature_group_names: List[str]
    try:
        fm = feature_model.FeatureModel(fm_json)
        feature_group_names = fm.get_names_of_feature_groups()

    except Exception as e:
        raise HTTPException(status_code=500, detail="Integral error " + str(e))
    return feature_group_names


@app.post("/get/assembly_steps", response_model=List[Dict[str, List[str]]])
async def get_assembly_steps(
    fm_json: data_types.FeatureModelType, spec: data_types.UnparsedSpecificationType
):
    assembly_steps: data_types.AssemblyProcessType
    try:
        fm = feature_model.FeatureModel(fm_json)
        parsed_spec = fm.parse_specification(spec)
        assembly_steps = fm.get_assembly_process(parsed_spec)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Integral error " + str(e))
    return assembly_steps
