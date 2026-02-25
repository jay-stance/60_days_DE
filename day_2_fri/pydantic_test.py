from pydantic import BaseModel, Field, ConfigDict, field_validator, model_validator
from typing import Annotated
from datetime import datetime

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


# test 11
class LogEvent(BaseModel):
  
  message: str
  created_at: datetime = Field(default_factory=datetime.now)
  

# test 12

from pydantic import computed_field

class Employee(BaseModel):
  first_name: str
  last_name: str
  
  @computed_field
  @property
  def full_name(self): 
    return f"${self.first_name} ${self.last_name}"
  
emp = Employee(first_name="Jane", last_name="Doe")
print(emp.full_name)  # Jane Doe


# test 13

class RawDataRow(BaseModel):
    category: str

    @model_validator(mode="after")
    def trim_category(self):
        # Strip leading/trailing whitespace
        self.category = self.category.strip()
        return self
      

# test 14

class AuditLog(BaseModel):
  model_config = {"frozen": True}
  
  event: str
  created_at: datetime
  
  
# test 15

from pydantic import BaseModel, field_validator
from uuid import UUID, uuid4

class Session(BaseModel):
    session_id: UUID

    @field_validator("session_id")
    @classmethod
    def ensure_uuid4(cls, value: UUID):
        if value.version != 4:
            raise ValueError("session_id must be a UUID4")
        return value
      
      
# test 16

class PatientRecord(BaseModel):
  patient_id: str
  name: str
  social_security: str 
  
p1_record = PatientRecord("idsois", "Edu Brazil", "hh667")
p1_record.model_dump(exclude={"social_security"})

# test 17

# Custom HexColor type: string starting with '#' and exactly 7 chars
HexColor = Annotated[str, Field(regex=r"^#[0-9A-Fa-f]{6}$")]

class Theme(BaseModel):
    color_code: HexColor
    
    
# task 18

class ServerNode(BaseModel):
    node_id: str
    status: str = "offline"
    
node1 = ServerNode(node_id="node-123")
print(node1)

node2 = node1.model_copy(update={"status": "online"}) 

# whenever you pass something inside all these model functions, the arguments usually uses diction/set symbols


# test 19

from typing import Union, Annotated, Literal

class PageView(BaseModel):
    event_type: Literal["view"]
    url: str

class Click(BaseModel):
    event_type: Literal["click"]
    button_id: str
    
StreamEvent = Annotated[
    Union[PageView, Click],
    Field(discriminator="event_type")
]
  
  
# test 20

from pydantic import BaseModel, Field, field_validator
from typing import Annotated, List


class Metadata(BaseModel):
    tags: List[str]
    source: str = "unknown"

    @field_validator("tags", mode="before")
    @classmethod
    def lowercase_tags(cls, value):
        return [tag.lower() for tag in value]


class ValidateRequest(BaseModel):
    request_id: Annotated[str, Field(alias="req-id")]
    metadata: Metadata
    scores: List[float]

    @field_validator("scores")
    @classmethod
    def validate_scores(cls, value):
        for score in value:
            if score > 100:
                raise ValueError("Scores cannot exceed 100")
        return value