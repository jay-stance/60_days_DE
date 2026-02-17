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
  with TypeError:
    result = clean_webhook_payload({"USER_ID": 1, "Event_Type": 1})