from dataclasses import dataclass

@dataclass
class User():
  name: str
  age: int
  
jay_user = User("jay stance", 20)