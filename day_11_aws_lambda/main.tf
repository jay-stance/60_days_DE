# ==========================================
# PART 1: SETUP
# ==========================================
provider "aws" {
  region = "us-east-1"
}

variable "environment" { default = "dev" }
locals { bucket_name = "tachpae-core-${var.environment}-logs" }

# ==========================================
# PART 2: THE STORAGE (The Trigger Source)
# ==========================================
resource "aws_s3_bucket" "tachpe_logs_bucket" {
  bucket = local.bucket_name
}

# ==========================================
# PART 3: THE HARD HAT (Permissions)
# ==========================================
# 3A. Create the role for the ghost server
resource "aws_iam_role" "lambda_exec_role" {
  name = "tachpae_lambda_execution_role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{ Action = "sts:AssumeRole", Effect = "Allow", Principal = { Service = "lambda.amazonaws.com" } }]
  })
}

# 3B. Allow the server to print logs to CloudWatch
resource "aws_iam_role_policy_attachment" "lambda_logs" {
  role       = aws_iam_role.lambda_exec_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# 3C. Allow the Python script (boto3) to download the CSV from S3
resource "aws_iam_policy" "s3_read_policy" {
  name = "tachpae-s3-reading"
  policy = jsonencode({
    Version: "2012-10-17",
    Statement: [{
      Effect: "Allow",
      Action: ["s3:GetObject"], # Only needs GetObject to download
      Resource: ["${aws_s3_bucket.tachpe_logs_bucket.arn}/*"]
    }]
  })
}

# 3D. WIRE THE POLICY TO THE ROLE (The fix!)
resource "aws_iam_role_policy_attachment" "lambda_s3_read" {
  role       = aws_iam_role.lambda_exec_role.name
  policy_arn = aws_iam_policy.s3_read_policy.arn
}

# ==========================================
# PART 4: THE COMPUTE (The Ghost Server)
# ==========================================
resource "aws_lambda_function" "ticket_processor" {
  function_name    = "tachpae-ticket-processor"
  role             = aws_iam_role.lambda_exec_role.arn # Wearing the Hard Hat from Part 3
  
  filename         = "lambda_payload.zip"
  source_code_hash = filebase64sha256("lambda_payload.zip")
  handler          = "processor.lambda_handler"
  runtime          = "python3.12"
  architectures    = ["x86_64"] 
  
  memory_size      = 512 
  timeout          = 30 

  # The Environment Variable "Sticky Note"
  environment {
    variables = {
      # We tell Terraform to grab the actual name of the table it just built
      DYNAMODB_TABLE = aws_dynamodb_table.ticket_counts.name
    }
  }

  # THE SHIELD: AWS will NEVER spin up more than 50 of these at the same time.
  # If 5,000 requests hit, AWS queues the rest up and processes them safely in batches of 50.
  reserved_concurrent_executions = 50
}

# ==========================================
# PART 5: THE WIRING (Connecting S3 to Lambda)
# ==========================================
# 5A. The Security Lock: Allow S3 to push the Lambda trigger button
resource "aws_lambda_permission" "allow_s3_to_trigger" {
  statement_id  = "AllowExecutionFromS3Bucket"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.ticket_processor.arn
  principal     = "s3.amazonaws.com"
  source_arn    = aws_s3_bucket.tachpe_logs_bucket.arn
}

# 5B. The Tripwire: Tell S3 to fire the event when a CSV lands
resource "aws_s3_bucket_notification" "tachpae_bucket_trigger" {
  bucket = aws_s3_bucket.tachpe_logs_bucket.id

  lambda_function {
    lambda_function_arn = aws_lambda_function.ticket_processor.arn
    events              = ["s3:ObjectCreated:*"]
    filter_suffix       = ".csv" 
  }

  depends_on = [aws_lambda_permission.allow_s3_to_trigger]
}


# ==========================================
# PART 2B: THE DATABASE (DynamoDB)
# ==========================================
resource "aws_dynamodb_table" "ticket_counts" {
  name         = "tachpae-ticket-counts"
  billing_mode = "PAY_PER_REQUEST" # Senior Best Practice: Don't pay for idle databases!
  hash_key     = "file_name"       # This is our Primary Key

  attribute {
    name = "file_name"
    type = "S"                     # 'S' stands for String
  }
}

# 3E. Allow the Python script to write to the new DynamoDB table
resource "aws_iam_policy" "dynamodb_write_policy" {
  name = "tachpae-dynamodb-writing"
  policy = jsonencode({
    Version: "2012-10-17",
    Statement: [{
      Effect: "Allow",
      Action: ["dynamodb:PutItem"], # We only need PutItem to insert data
      Resource: [aws_dynamodb_table.ticket_counts.arn]
    }]
  })
}

# 3F. Attach the new DynamoDB policy to the Lambda's Hard Hat
resource "aws_iam_role_policy_attachment" "lambda_dynamo_write" {
  role       = aws_iam_role.lambda_exec_role.name
  policy_arn = aws_iam_policy.dynamodb_write_policy.arn
}