from datetime import datetime

import logfire

from pydantic import BaseModel

logfire.configure()
logfire.instrument_pydantic()  


class Delivery(BaseModel):
    timestamp: datetime
    dimensions: tuple[int, int]


# this will record details of a successful validation to logfire
m = Delivery(timestamp='2020-01-02T03:04:05Z', dimensions=['10', '20'])
print(repr(m.timestamp))
#> datetime.datetime(2020, 1, 2, 3, 4, 5, tzinfo=TzInfo(UTC))
print(m.dimensions)
#> (10, 20)

Delivery(timestamp='2020-01-02T03:04:05Z', dimensions=['10'])


# =====================================

#     ACTUAL LEARNING STARTS HERE

# =====================================

from pydantic import BaseModel

class User(BaseModel):
  id: int
  username: str 
  is_active: bool 
  
messy_obj = {
  "id": "123",
  "username": "jay stance",
  "is_active": "yes"
}

bad_messy_data = {
  "id": "lsknosi",
  "username": "jay stance",
  "is_active": "yes"
} 

try:
  user_data = User(**bad_messy_data)
  print(user_data)
except ValidationError as e:
  print(e)
  

user_data = User(**messy_obj)
print(user_data)


from pydantic import BaseModel 

class Employee(BaseModel):
  id: int 
  name: str
  department: str = "Software Engineering"
  manager_name: str | None = None
  
new_employee = Employee(id=123, name='jay stance')
print(new_employee)

print(new_employee.model_dump())

print(new_employee.model_dump_json())


from dataclasses import dataclass

@dataclass
class User():
  name: str
  age: int
  
jay_user = User("jay stance", 20)