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
  

# ============================

#. Test 7: The I/O Test (tmp_path)

# ============================

import json
from pathlib import Path

def save_json(data: dict, file_path: Path):
    with open(file_path, "w") as f:
        json.dump(data, f)
        
@pytest.mark.tmp_path
def test_file_saves(tmp_path):     # tmp_path is an inbuilt fixture, so you still need to pass it to the function
  data = {"name": "jay", "level": "intermediate"}
  file_path = tmp_path / "test.json"
  
  save_json(data, file_path)
  
  assert file_path.exists() == True
  assert len(file_path.read_text()) > 1
  
  
# ============================

#. Test 8: The Hijack Test (monkeypatch)

# ============================

import pytest
import requests
from unittest.mock import MagicMock
import responses

def get_crypto_price(coin: str):
    # The real logic
    response = requests.get(f"https://api.coindesk.com/v1/bpi/currentprice/{coin}.json")
    return response.json()["rate"]

@pytest.fixture
def mock_requests_get(monkeypatch):
    """
    Fixture to intercept requests.get and return a controlled mock object.
    """
    mock_resp = MagicMock()
    # Mock the .json() method to return our fake data
    mock_resp.json.return_value = {"rate": "50,000.00"}
    
    # 2. Mock the 'get' function (the action itself)
    mock_get_func = MagicMock(return_value=mock_resp)
    
    # Patch the 'get' method in the 'requests' module
    monkeypatch.setattr(requests, "get", mock_get_func)
    
    return mock_get_func  # Return the mock so we can inspect it in the test

@pytest.mark.test_monkeypatch
def test_get_crypto_price(mock_requests_get):
    # Act
    coin_price = get_crypto_price("BTC")
    
    # Assert 1: Check the return value
    assert coin_price == "50,000.00"
    mock_requests_get.assert_called_once()
    
    args, _ = mock_requests_get.call_args
    assert "BTC.json" in args[0]
    
    # Assert 2: Verify the URL was constructed correctly (The "Pro" step)
    # Since we returned mock_resp, we can't easily check 'requests.get' 
    # unless we store the lambda or use a different patching style.
    
# METHOD 2

@responses.activate # This "turns on" the interceptor for this test
def test_get_crypto_price_with_responses():
    # Define the URL and what it should return
    target_url = "https://api.coindesk.com/v1/bpi/currentprice/BTC.json"
    
    responses.add(
        responses.GET, 
        target_url,
        json={"rate": "50,000.00"}, # The fake body
        status=200                  # The fake status code
    )

    # Act
    price = get_crypto_price("BTC")

    # Assert
    assert price == "50,000.00"
    
    
# ============================

#. Test 9: The Assembly Line (parametrize)

# ============================

def classify_risk(amount: int):
    if amount > 10000:
        return "HIGH"
    elif amount > 1000:
        return "MEDIUM"
    return "LOW"
  
@pytest.mark.risk_level
@pytest.mark.parametrize(
  'input_value, expected_output',
  [
    (12000, "HIGH"),
    (4000, "MEDIUM"),
    (500, "LOW")
  ],
  ids=[
    "passed 12,000 - expecting high",
    "passed 4,000 - especting medium",
    "passed 500 - especting low"
  ]
  )
def test_classify_risk(input_value, expected_output):
  risk_level = classify_risk(input_value)
  
  assert risk_level == expected_output
  
  
# ============================

# Test 10: The Conditional Skip

# ============================

import os

def connect_to_snowflake():
    # This crashes if the key is missing
    key = os.environ["SNOWFLAKE_KEY"] 
    return "Connected"

@pytest.mark.skipif(not os.environ.get("SNOWFLAKE_KEY"), reason="Snowflakes credentials must be present")
@pytest.mark.test_skip_condition
def test_snowflake_connection():
  connection_status = connect_to_snowflake()
  
  assert connection_status == "Connected"