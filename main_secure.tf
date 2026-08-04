# Add description to every ingress/egress rule
ingress {
  from_port   = 22
  to_port     = 22
  protocol    = "tcp"
  cidr_blocks = ["10.0.0.0/8"]
  description = "SSH from internal network only"  # ← add this
}