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