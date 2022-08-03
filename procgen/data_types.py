from pydantic import BaseModel
from typing import Dict, List, Literal, Optional


class MetaType(BaseModel):
    name: str
    abstract: bool = False
    type: Literal["and"] | Literal["alt"] = "and"
    mandatory: bool = False
    assembly_action: Optional[str]
    id: str = "0"
    travel: Optional[List[str]]


class StructureType(BaseModel):
    meta: MetaType
    nodes: Optional[Dict[str, "StructureType"]]


StructureType.update_forward_refs()


class ConstraintType(BaseModel):
    type: Literal["exc"] | Literal["req"]
    variables: List[str]


class AssemblyActionStepType(Dict[str, List[str]]):
    pass


class AssemblyActionOrderType(List[str]):
    pass


class OrderConstraintExpressionType(BaseModel):
    type: Literal["and"] | Literal["or"]
    variables: List[str]
    order: AssemblyActionOrderType


class OrderConstraintsType(BaseModel):
    default: AssemblyActionOrderType
    constraints: List[OrderConstraintExpressionType]


class FeatureModelType(BaseModel):
    structure: Dict[str, StructureType]
    constraints: List[ConstraintType]
    order_constraints: OrderConstraintsType
    assembly_steps: AssemblyActionStepType


class UnparsedSpecificationType(BaseModel):
    features: Dict[str, str]


class SpecificationType(BaseModel):
    features: Dict[str, List[str]]


class FeatureType(BaseModel):
    group: str
    selected_feature: str
    assembly_action: str


class ProductType(BaseModel):
    features: List[FeatureType]
    assembly_order: AssemblyActionOrderType


class AssemblyProcessType(List[AssemblyActionStepType]):
    pass
