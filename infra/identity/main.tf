# Permanent and free: lets GitHub Actions on main log in to AWS (no stored keys).
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.95"
    }
  }
}

provider "aws" {
  region = var.region
}

variable "region" {
  type    = string
  default = "us-east-1"
}

variable "github_repo" {
  description = "owner/name, exactly as GitHub spells it"
  type        = string
  default     = "AmirAbuELHija/devops-project"
}

resource "aws_iam_openid_connect_provider" "github" {
  url            = "https://token.actions.githubusercontent.com"
  client_id_list = ["sts.amazonaws.com"]
}

data "aws_iam_policy_document" "trust" {
  statement {
    actions = ["sts:AssumeRoleWithWebIdentity"]

    principals {
      type        = "Federated"
      identifiers = [aws_iam_openid_connect_provider.github.arn]
    }

    condition {
      test     = "StringEquals"
      variable = "token.actions.githubusercontent.com:aud"
      values   = ["sts.amazonaws.com"]
    }

    condition {
      test     = "StringEquals"
      variable = "token.actions.githubusercontent.com:sub"
      values   = ["repo:${var.github_repo}:ref:refs/heads/main"]
    }
  }
}

resource "aws_iam_role" "pipeline" {
  name                 = "pipeline-identities"
  assume_role_policy   = data.aws_iam_policy_document.trust.json
  max_session_duration = 3600
}

output "AWS_ROLE_ARN" {
  value = aws_iam_role.pipeline.arn
}

output "AWS_REGION" {
  value = var.region
}