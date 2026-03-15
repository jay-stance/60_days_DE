provider "aws" {
  region = "us-east-1"
}

# ==========================================
# PHASE 1: THE ENTERPRISE NETWORK
# ==========================================
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "5.5.0" # Always lock your module versions in production!

  name = "financial-data-vpc"
  
  # 1. The CIDR Block (Claiming the 10.x.x.x private IP space)
  cidr = "10.0.0.0/16"

  # 2. The Availability Zones (Using two data centers for disaster recovery)
  azs             = ["us-east-1a", "us-east-1b"]
  
  # 3. The Subnets (The Lobby and The Vault)
  public_subnets  = ["10.0.1.0/24", "10.0.2.0/24"]
  private_subnets = ["10.0.101.0/24", "10.0.102.0/24"]

  # 4. The Magic Courier (The NAT Gateway)
  enable_nat_gateway = true
  single_nat_gateway = true # We use one NAT to save money while learning (they cost ~$30/month)

  # 5. Security Best Practice: Don't automatically give out public IPs inside the VPC
  map_public_ip_on_launch = false

  tags = {
    Environment = "Production"
    Team        = "Data-Engineering"
  }
}

# ==========================================
# PHASE 2: THE ECR VAULT
# ==========================================
resource "aws_ecr_repository" "financial_etl_repo" {
  name                 = "fintech-exchange-etl"
  image_tag_mutability = "MUTABLE"
  force_delete = true

  # Force AWS to scan our Python environment for hacker vulnerabilities
  image_scanning_configuration {
    scan_on_push = true
  }
}

# ==========================================
# PHASE 3: THE ECS FARGATE ENGINE
# ==========================================

# 1. The Cluster (The Warehouse)
resource "aws_ecs_cluster" "financial_cluster" {
  name = "fintech-etl-cluster"
}

# 2. The Logs (So you can see your Python print statements)
resource "aws_cloudwatch_log_group" "ecs_logs" {
  name              = "/ecs/fintech-exchange-etl"
  retention_in_days = 7
}

# 3. The IAM Role (Giving Fargate permission to pull from ECR)
resource "aws_iam_role" "ecs_task_execution_role" {
  name = "fintech_ecs_execution_role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{ Action = "sts:AssumeRole", Effect = "Allow", Principal = { Service = "ecs-tasks.amazonaws.com" } }]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_execution_policy" {
  role       = aws_iam_role.ecs_task_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

# 4. The Security Group (The Vault Door)
resource "aws_security_group" "fargate_sg" {
  name        = "fintech-fargate-sg"
  description = "Allow outbound traffic only for financial ETL"
  vpc_id      = module.vpc.vpc_id # This connects directly to the Phase 1 VPC!

  # Inbound: DENY ALL (Hackers cannot enter)
  
  # Outbound: ALLOW ALL (Container can reach the NAT Gateway to download exchange rates)
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# 5. The Task Definition (The Master Blueprint)
resource "aws_ecs_task_definition" "financial_etl_task" {
  family                   = "fintech-exchange-etl-job"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "256" # 0.25 vCPU
  memory                   = "512" # 512 MB RAM
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn

  # Here is where we tell ECS exactly which Docker image to run
  container_definitions = jsonencode([{
    name      = "financial-etl-container"
    image     = "${aws_ecr_repository.financial_etl_repo.repository_url}:latest"
    essential = true
    
    logConfiguration = {
      logDriver = "awslogs"
      options = {
        "awslogs-group"         = aws_cloudwatch_log_group.ecs_logs.name
        "awslogs-region"        = "us-east-1"
        "awslogs-stream-prefix" = "ecs"
      }
    }
  }])
}

# ==========================================
# PHASE 6: TERMINAL OUTPUTS
# ==========================================

# Print the Security Group ID
output "fargate_security_group_id" {
  description = "The ID of the Fargate Security Group"
  value       = aws_security_group.fargate_sg.id
}

# Print the FIRST Private Subnet ID
output "fargate_private_subnet_id" {
  description = "The ID of the first Private Subnet to launch the Task into"
  # Because the VPC module creates multiple subnets, it returns a list. 
  # We use [0] to grab the very first one in the list.
  value       = module.vpc.private_subnets[0]
}



# ==========================================
# PHASE 7: EVENTBRIDGE AUTOMATION (The Alarm Clock)
# ==========================================

# 1. The Messenger's Hard Hat (IAM Role)
resource "aws_iam_role" "eventbridge_ecs_role" {
  name = "fintech_eventbridge_trigger_role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = { Service = "events.amazonaws.com" } # Only EventBridge can wear this
    }]
  })
}

# Give EventBridge permission to pull the trigger AND hand off the Execution Hat
resource "aws_iam_role_policy" "eventbridge_ecs_policy" {
  name = "fintech_eventbridge_ecs_policy"
  role = aws_iam_role.eventbridge_ecs_role.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = "ecs:RunTask"
        Resource = "*" # Allows it to run the Task Definition
      },
      {
        Effect   = "Allow"
        Action   = "iam:PassRole" # The critical Senior DE permission!
        Resource = aws_iam_role.ecs_task_execution_role.arn
      }
    ]
  })
}

# 2. The Rule (The Schedule)
resource "aws_cloudwatch_event_rule" "daily_etl_schedule" {
  name                = "fintech-daily-etl-trigger"
  description         = "Fires every night at midnight UTC"
  schedule_expression = "cron(0 0 * * ? *)" 
}

# 3. The Target (Wiring the Clock to the Engine)
resource "aws_cloudwatch_event_target" "ecs_fargate_target" {
  rule      = aws_cloudwatch_event_rule.daily_etl_schedule.name
  target_id = "RunFinancialETL"
  arn       = aws_ecs_cluster.financial_cluster.arn
  role_arn  = aws_iam_role.eventbridge_ecs_role.arn

  ecs_target {
    task_count              = 1
    task_definition_arn   = aws_ecs_task_definition.financial_etl_task.arn
    launch_type             = "FARGATE"
    
    # Notice how EventBridge dynamically injects the network rules we used in the CLI!
    network_configuration {
      subnets          = module.vpc.private_subnets
      security_groups  = [aws_security_group.fargate_sg.id]
      assign_public_ip = false
    }
  }
}