from pydantic import BaseModel, Field, ConfigDict, field_validator, model_validator
from typing import Annotated

# test 1
class Customer(BaseModel):
  id: int
  email: str
  is_active: bool 
  
# test 2
class Transaction(BaseModel):
  amount: Annotated[float, Field(gt=0.0)]
  currency: Annotated[str, Field(min_length=3, max_length=3)]
  
# test 3
class Product(BaseModel):
  product_id: int
  price: float
  
class Order(BaseModel):
  order_id: int
  items: list[Product]
  
# test 4
class User(BaseModel):
  first_name: Annotated[str, Field(alias="first-name")]
  
# to get such that both first-name and first_name work, you have to use configdict
class User(BaseModel):
  model_config = ConfigDict(populate_by_name=True)
  
  first_name: Annotated[str, Field(alias="first-name")]
  
# When Serializing Back to JSON

# If you want to send it back using the original API format:

# user.model_dump(by_alias=True)

# Output:

# {
#   "first-name": "Jay"
# }

# test 5

class inventoryCount(BaseModel):
  model_config = ConfigDict(strict=True)
  
  item_count: int
  
  
# test 6

# The extra setting must be one of:

# "allow"
# "ignore"
# "forbid"

class WebhookPayload(BaseModel):
  model_config = ConfigDict(extra="forbid")
  
  event_id: str
  timestamp: str
  
# test 7

class NetworkDevice(BaseModel):
    ip_address: str

    @field_validator("ip_address")
    @classmethod
    def validate_ip(cls, value: str) -> str:
        if not value.startswith("192.168."):
            raise ValueError("IP address must start with '192.168.'")
        return value
      
      
# test 8 

# Why model_validator?
# Because:

# - field_validator validates one field at a time
# - model_validator has access to the whole model
# - You need both start_date and end_date to compare

class subscription(BaseModel):
  start_date: str
  end_date: str
  
  @model_validator(mode="after")
  def check_dates(self):
    if(self.end_date <= self.start_date):
      raise ValueError("end date must greater than start date")
    return self 
    

# test 9

# Why Use Pydantic for Env Config?

#   - Automatic type coercion (str → int, float, bool, etc.)
#   - Validation rules (ranges, regex, required fields)
#   - Centralized config object — easier to pass around
#   - Supports aliases and .env files automatically
#   - Less boilerplate / cleaner / safer than manual os.getenv

from pydantic_settings import BaseSettings

class DataBaseConfig(BaseSettings):
  db_host: str
  db_user: str
  db_port: int 
  
  class Config:
        env_prefix = ""  # no prefix; matches exact env var names
        env_file = ".env"  # optional: also load from .env file    
        
        
# task 10

from pydantic import SecretStr

class DataBaseConfig(BaseSettings):
  db_host: str
  db_user: str
  db_port: int 
  db_password: SecretStr
  
  class Config:
        env_prefix = ""  # no prefix; matches exact env var names
        env_file = ".env"  # optional: also load from .env file    

config = DataBaseConfig()
password = config.db_password.get_secret_value()  # how to get the actual password