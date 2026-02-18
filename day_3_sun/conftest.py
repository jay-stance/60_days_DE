import pytest
import sqlite3
import pandas as pd

# --- FIXTURE 1: The Foundation ---
@pytest.fixture(scope="function")
def db_connection():
    """Spins up an empty, temporary database in RAM."""
    # SETUP: Create an in-memory SQLite database (lightning fast, requires no servers)
    conn = sqlite3.connect(":memory:")
    
    yield conn  # Hand the blank connection down the chain
    
    # TEARDOWN: Destroy the database completely after the test
    conn.close()

# --- FIXTURE 2: The Data Loader ---
@pytest.fixture(scope="function")
def populated_db(db_connection): # <-- MAGIC: It requests the first fixture!
    """Uses the connection fixture to load messy test data."""
    
    # 1. Create a messy dataframe
    messy_data = pd.DataFrame({
        "customer_id": [1, 2, 3],
        "email": [" ALICE@test.com ", "bob@TEST.com", None] # Needs cleaning
    })
    
    # 2. Write the messy data into the database connection we received
    messy_data.to_sql("raw_customers", db_connection, index=False)
    
    # 3. Yield the now-populated connection to the actual test
    yield db_connection
    
@pytest.fixture(autouse=True)
def set_testmod_env(monkeypatch):
  monkeypatch.setenv("APP_MODE", "TEST")