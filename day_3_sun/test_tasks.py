import pytest 

def clean_webhook_payload(payload: dict):
  return {
      "user_id": int(payload.get("USER_ID", 0)),
      "event_type": payload.get("Event_Type", "").lower(),
      "status": "processed"
  }
  
@pytest.mark.clean_payload  
@pytest.mark.parametrize("input_value, expected_output", [
  (1, 1),
  ('1', 1),
], ids=[
  "correct user id",
  "user id is a numeric string",
])  
def test_clean_webhook_payload_userId(input_value, expected_output):
  cleaned_payload = clean_webhook_payload({"USER_ID": input_value, "Event_Type": 'party'})
  assert cleaned_payload["user_id"] == expected_output

  
@pytest.mark.clean_payload
@pytest.mark.parametrize("input_value, expected_output", [
  ("test", "test"),
  ("Party", "party")
], ids=[
  "event type is a number",
  "first letter of event type is cpaital latter"
])  
def test_clean_webhook_payload_eventId(input_value, expected_output):
  cleaned_payload = clean_webhook_payload({"USER_ID": 1, "Event_Type": input_value})
  assert cleaned_payload["event_type"] == expected_output
  
  
# ============================

#         TEST 2

# ============================

# raises error 

@pytest.mark.clean_payload
def test_clean_webhook_event_rejects_integers():
  
  # you have to use pytest specific took, with pytest.raises
  with pytest.raises(AttributeError):
    clean_webhook_payload({"USER_ID": 1, "Event_Type": 1})
    
    
# ============================

#. Test 3: The Float Trap Test

# ============================

def calculate_ad_spend(cpc: float, clicks: int):
  return cpc * clicks
  
@pytest.mark.test_3
def test_calculate_ad_spend():
  ad_spend = calculate_ad_spend(0.1, 3)
  assert ad_spend == pytest.approx(0.3)
  
  
# ============================

#. Test 4: The Grid Test

# ============================

import pandas as pd

def filter_adults(df: pd.DataFrame):
    # Keeps only rows where age is 18 or older, and resets the row numbers
    adults = df[df['age'] >= 18].copy()
    return adults.reset_index(drop=True)
  

# To test DataFrames, you must test the entire grid at once to ensure no rows were dropped or duplicated.  

@pytest.mark.test_df
def test_filter_adults():
  
  input_value = pd.DataFrame({
    "name": ['jay', "stance", "Alice", "Bob"],
    "age": [16, 32, 18, 8]
  })
  
  expected_output = pd.DataFrame({
    "name": ["stance", "Alice"],
    "age": [32, 18]
  })
  
  output_value = filter_adults(input_value)
  # assert df.at[0, "name"] == "stance".    junior level testing
  pd.testing.assert_frame_equal(output_value, expected_output)
  
  
# ============================

#. Test 4: The Grid Test

# ============================

def build_db_url(config: dict):
    user = config["user"]
    pw = config["password"]
    host = config["host"]
    db = config["db"]
    return f"postgresql://{user}:{pw}@{host}:5432/{db}"
  
@pytest.fixture
def mock_db_config():
  return {
    "user": "jay",
    "password": "123",
    "host": "local",
    "db": "test"
  }
  
@pytest.mark.db_config
def test_build_db_url(mock_db_config):
  db_url = build_db_url(mock_db_config)
  
  assert db_url == "postgresql://jay:123@local:5432/test"
  
  
# ============================

#. Test 6: The Cleanup Test (yield)

# ============================

class DatabaseConnection:
    def __init__(self, db_name: str):
        self.db_name = db_name
        self.is_active = False

    def connect(self):
        self.is_active = True

    def close(self):
        self.is_active = False

@pytest.fixture(scope="function")
def active_db_session():
  db_connection = DatabaseConnection("test_db")
  
  db_connection.connect()
  
  yield db_connection
  
  db_connection.close()
  
@pytest.mark.test_yield
def test_db_is_active(active_db_session):
  assert active_db_session.is_active == True