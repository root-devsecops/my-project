terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "ap-south-1"
}

# ── INSECURE: S3 bucket for app assets ────────────
resource "aws_s3_bucket" "app_assets" {
  bucket = "flask-devsecops-assets"
}

# INSECURE: Public access not blocked
resource "aws_s3_bucket_public_access_block" "app_assets" {
  bucket = aws_s3_bucket.app_assets.id

  block_public_acls       = false
  block_public_policy     = false
  ignore_public_acls      = false
  restrict_public_buckets = false
}

# INSECURE: No encryption
resource "aws_s3_bucket_server_side_encryption_configuration" "app_assets" {
  bucket = aws_s3_bucket.app_assets.id
  # Missing encryption configuration
}

# ── INSECURE: EC2 instance ─────────────────────────
resource "aws_instance" "flask_server" {
  ami           = "ami-0f58b397bc5c1f2e8"
  instance_type = "t2.micro"

  # INSECURE: No key pair for SSH
  # INSECURE: Will get default security group (allows all traffic)

  tags = {
    Name = "flask-server"
  }
}

# ── INSECURE: Security group ───────────────────────
resource "aws_security_group" "flask_sg" {
  name        = "flask-security-group"
  description = "Security group for Flask app"

  # INSECURE: SSH open to the world
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # INSECURE: All ports open to the world
  ingress {
    from_port   = 0
    to_port     = 65535
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # All outbound allowed
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# ── INSECURE: RDS database ─────────────────────────
resource "aws_db_instance" "flask_db" {
  identifier        = "flask-db"
  engine            = "postgres"
  engine_version    = "15"
  instance_class    = "db.t3.micro"
  allocated_storage = 20

  db_name  = "flaskapp"
  username = "admin"
  password = "SuperSecret123!"  # INSECURE: Hardcoded password

  # INSECURE: Publicly accessible
  publicly_accessible = true

  # INSECURE: No encryption
  storage_encrypted = false

  # INSECURE: No backup
  backup_retention_period = 0

  skip_final_snapshot = true
}