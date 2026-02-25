from pydantic import BaseModel, Field, ValidationError
from typing import Annotated

# test 1
class Customer(BaseModel):
  id: int
  email: str
  is_active: bool 
  
# test 2
class Transaction(BaseModel):
  amount: Annotated[float, Field(gt=0.0)]
  currency: Annotated[str, Field(min_length=3)]