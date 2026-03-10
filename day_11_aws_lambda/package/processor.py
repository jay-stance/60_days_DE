import json
import boto3
import urllib.parse
import uuid
import os

# ==========================================
# 1. GLOBAL SCOPE (The "Warm Start" Zone)
# ==========================================
# This runs during the 10-second INIT phase. 
# We initialize boto3 here so it stays warm for the next user.
s3_client = boto3.client('s3')

def lambda_handler(event, context):
    """
    The main INVOKE phase. AWS passes the S3 trigger data into the 'event' argument.
    """
    # 1. Parse the exact Bucket and File Name from the AWS S3 Event JSON
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')

    # 2. Prevent Data Leaks: Generate a random UUID for the /tmp file
    # This ensures User 2 never accidentally reads User 1's ticket data
    secure_tmp_path = f"/tmp/{uuid.uuid4()}-{key}"

    try:
        print(f"Starting Tachpae extraction for: {key}")
        
        # 3. Download the file to the ghost server's local /tmp drive
        s3_client.download_file(bucket, key, secure_tmp_path)
        
        # 4. Core Logic: Read and process the ticket data
        with open(secure_tmp_path, 'r') as file:
            raw_tickets = file.read()
            # In a real pipeline, you would parse the CSV and insert it into a database here
            print(f"Successfully processed {len(raw_tickets)} characters of ticket data.")

        return {
            'statusCode': 200,
            'body': json.dumps(f"Success: Processed {key}")
        }

    except Exception as e:
        print(f"FATAL ERROR: {str(e)}")
        raise e

    finally:
        # ==========================================
        # 5. THE SHUTDOWN CLEANUP
        # ==========================================
        # This 'finally' block runs no matter what, even if the code crashes above.
        # It aggressively deletes the file so it doesn't survive a Warm Start.
        if os.path.exists(secure_tmp_path):
            os.remove(secure_tmp_path)
            print(f"Cleaned up {secure_tmp_path} from memory.")