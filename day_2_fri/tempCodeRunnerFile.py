from pydantic.dataclasses import dataclass


@dataclass
class User():
  name: str
  age: int
  
bad_user = User(123, True)

print(type(bad_user.name))

jay_user = User("jay stance", 20)