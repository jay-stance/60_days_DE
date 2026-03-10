import json
import boto3
import urllib.parse
import uuid
import os
import csv

# ==========================================
# 1. GLOBAL SCOPE (The Warm Start Zone)
# ==========================================
# We now initialize BOTH clients here so they stay warm!
s3_client = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')

# Connect to the exact table we built in Terraform
table = dynamodb.Table('tachpae-ticket-counts')

def lambda_handler(event, context):
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    raw_file_key = event['Records'][0]['s3']['object']['key']
    clean_file_key = urllib.parse.unquote_plus(raw_file_key, encoding='utf-8')
    
    secure_tmp_path = f"/tmp/{uuid.uuid4()}-{clean_file_key}"

    try:
        # 1. EXTRACT: Download the file from S3
        print(f"Downloading {clean_file_key}...")
        s3_client.download_file(bucket_name, clean_file_key, secure_tmp_path)
        
        # 2. TRANSFORM: Read the CSV and count the rows
        row_count = 0
        with open(secure_tmp_path, 'r', encoding='utf-8') as csv_file:
            csv_reader = csv.reader(csv_file)
            # Skip the header row if your CSV has one (optional)
            next(csv_reader, None) 
            
            for row in csv_reader:
                row_count += 1
                
        print(f"Counted {row_count} rows in {clean_file_key}")

        # 3. LOAD: Push the metadata to DynamoDB
        table.put_item(
            Item={
                'file_name': clean_file_key,
                'row_count': row_count
            }
        )
        print("Successfully wrote row count to DynamoDB.")

        return {
            'statusCode': 200,
            'body': json.dumps(f"Processed {clean_file_key}: {row_count} rows.")
        }

    except Exception as e:
        print(f"FATAL ERROR: {str(e)}")
        raise e

    finally:
        # 4. CLEANUP: Prevent Warm Start data leaks
        if os.path.exists(secure_tmp_path):
            os.remove(secure_tmp_path)