output "environment" {
  value = var.environment
}

output "project_name" {
  value = var.project_name
}

output "vpc_id" {
  value = module.network.vpc_id
}

output "public_subnet_1_id" {
  value = module.network.public_subnet_1_id
}

output "public_subnet_2_id" {
  value = module.network.public_subnet_2_id
}

output "bucket_name" {
  value = aws_s3_bucket.logs.bucket
}