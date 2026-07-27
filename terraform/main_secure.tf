terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  # SECURE: Remote state backend with encryption
  backend "s3" {
    bucket         = "flask-devsecops-tfstate"
    key            = "prod/terraform.tfstate"
    region         = "ap-south-1"
    encrypt        = true
    dynamodb_table = "terraform-state-lock"
  }
}

provider "aws" {
  region = "ap-south-1"

  default_tags {
    tags = {
      Project     = "flask-devsecops"
      Environment = "production"
      ManagedBy   = "terraform"
    }
  }
}

# ── SECURE: S3 bucket ─────────────────────────────
resource "aws_s3_bucket" "app_assets" {
  bucket = "flask-devsecops-assets"
}

# SECURE: Block all public access
resource "aws_s3_bucket_public_access_block" "app_assets" {
  bucket = aws_s3_bucket.app_assets.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# SECURE: Enable encryption
resource "aws_s3_bucket_server_side_encryption_configuration" "app_assets" {
  bucket = aws_s3_bucket.app_assets.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "aws:kms"
    }
  }
}

# SECURE: Enable versioning
resource "aws_s3_bucket_versioning" "app_assets" {
  bucket = aws_s3_bucket.app_assets.id

  versioning_configuration {
    status = "Enabled"
  }
}

# SECURE: Enable access logging
resource "aws_s3_bucket_logging" "app_assets" {
  bucket        = aws_s3_bucket.app_assets.id
  target_bucket = aws_s3_bucket.app_assets.id
  target_prefix = "access-logs/"
}

# ── SECURE: EC2 instance ───────────────────────────
resource "aws_instance" "flask_server" {
  ami                    = "ami-0f58b397bc5c1f2e8"
  instance_type          = "t3.micro"
  key_name               = aws_key_pair.flask_key.key_name
  vpc_security_group_ids = [aws_security_group.flask_sg.id]
  subnet_id              = "subnet-xxxxxxxxxx"

  # SECURE: Enable detailed monitoring
  monitoring = true

  # SECURE: Encrypted root volume
  root_block_device {
    encrypted   = true
    volume_type = "gp3"
    volume_size = 20
  }

  # SECURE: IMDSv2 required
  metadata_options {
    http_tokens                 = "required"
    http_put_response_hop_limit = 1
  }

  tags = {
    Name = "flask-server"
  }
}

# SECURE: Key pair for SSH
resource "aws_key_pair" "flask_key" {
  key_name   = "flask-devsecops-key"
  public_key = file("~/.ssh/id_ed25519.pub")
}

# ── SECURE: Security group ─────────────────────────
resource "aws_security_group" "flask_sg" {
  name        = "flask-security-group"
  description = "Security group for Flask app"
  vpc_id      = "vpc-xxxxxxxxxx"

  # SECURE: SSH only from specific IP
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["10.0.0.0/8"]
    description = "SSH from internal network only"
  }

  # SECURE: Only app port exposed
  ingress {
    from_port   = 5000
    to_port     = 5000
    protocol    = "tcp"
    cidr_blocks = ["10.0.0.0/8"]
    description = "Flask app from internal network"
  }

  egress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "HTTPS outbound only"
  }
}

# ── SECURE: RDS database ───────────────────────────
resource "aws_db_instance" "flask_db" {
  identifier        = "flask-db"
  engine            = "postgres"
  engine_version    = "15"
  instance_class    = "db.t3.micro"
  allocated_storage = 20

  db_name  = "flaskapp"
  username = "admin"

  # SECURE: Password from AWS Secrets Manager
  password = data.aws_secretsmanager_secret_version.db_password.secret_string

  # SECURE: Not publicly accessible
  publicly_accessible = false

  # SECURE: Encryption enabled
  storage_encrypted = true

  # SECURE: Automated backups
  backup_retention_period = 7
  backup_window           = "03:00-04:00"

  # SECURE: Multi-AZ for high availability
  multi_az = true

  # SECURE: Enhanced monitoring
  monitoring_interval = 60

  # SECURE: Auto minor version upgrades
  auto_minor_version_upgrade = true

  # SECURE: Deletion protection
  deletion_protection = true

  skip_final_snapshot = false
  final_snapshot_identifier = "flask-db-final-snapshot"
}

# SECURE: Fetch password from Secrets Manager
data "aws_secretsmanager_secret_version" "db_password" {
  secret_id = "flask-db-password"
}