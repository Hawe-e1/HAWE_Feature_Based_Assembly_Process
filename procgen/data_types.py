from pydantic import BaseModel
from typing import Dict, List, Optional, OrderedDict


class StructureType(BaseModel):
    meta: Dict[str, str | bool]
    nodes: Optional[Dict[str, "StructureType"]]


StructureType.update_forward_refs()


class OrderConstraintType(BaseModel):
    expr: List[str]
    order: List[int]


class FeatureModelType(BaseModel):
    structure: Dict[str, StructureType]
    constraints: List[List[str]]
    order_constraints: List[OrderConstraintType]
    assembly_steps: Dict[str, List[str]]


class SpecificationType(BaseModel):
    features: Dict[str, str]


class FeatureType(BaseModel):
    group: str
    assembly_action: str


class ProductType(BaseModel):
    features: List[FeatureType]
    assembly_order: List[int]


class AssemblyProcessType(BaseModel):
    assembly: OrderedDict[str, List[str]]
