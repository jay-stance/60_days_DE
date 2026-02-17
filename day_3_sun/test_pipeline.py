import pandas as pd

# The test only requests the final link in the chain
# def test_email_cleaning_pipeline(populated_db):
    
#     # 1. RUN PIPELINE: Read from the raw table, clean it, write to a clean table
#     # (Imagine this is the function you are actually testing)
#     clean_emails(source_conn=populated_db) 
    
#     # 2. ASSERTION: Read the final table to prove your pipeline worked
#     result_df = pd.read_sql("SELECT * FROM clean_customers", populated_db)
    
#     assert result_df["email"].iloc[0] == "alice@test.com" # Lowercased and stripped!
#     assert pd.isna(result_df["email"].iloc[2]) # Nulls handled correctly