from pydantic import BaseModel
from typing import Optional, List, Union

class OperationRequest(BaseModel):
    a: float
    b: float
    operation: str

class ExpressionRequest(BaseModel):
    expression: str

class ExpressionResponse(BaseModel):
    expression: str
    result: Optional[float] = None
    error: Optional[str] = None

class CalculatorState(BaseModel):
    current_expression: str
    variables: dict