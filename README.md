Temporarily excluded S3 lifecycle configuration during LocalStack execution due to LocalStack API compatibility limitations, while preserving the intended Terraform configuration structure.


# Multi-Cloud Cost Hygiene Automation

A FinOps and cloud governance automation project built for the NimbusKart staging environment using Terraform, LocalStack, Python, boto3, and GitHub Actions.

This project provisions AWS-style infrastructure locally using LocalStack and Terraform, then scans the environment for cloud waste patterns such as orphaned EBS volumes, stopped EC2 instances, unused Elastic IPs, and missing governance tags.

The automation generates both machine-readable JSON reports and human-readable Markdown summaries while supporting safe dry-run and protected delete workflows.

---

## Project Objectives

- Provision reusable AWS infrastructure using Terraform modules
- Simulate cloud resources locally using LocalStack
- Detect common cloud cost hygiene issues
- Generate structured governance reports
- Enforce automation through GitHub Actions CI/CD
- Implement safe-by-default deletion workflows

---

## Architecture Overview

```text
GitHub Actions CI/CD
          ↓
     LocalStack
          ↓
Terraform Infrastructure
          ↓
AWS-style Resources
          ↓
Python Cost Janitor
          ↓
JSON + Markdown Reports

```

## Technology Stack

| Category | Tools |
|---|---|
| Infrastructure as Code | Terraform |
| Cloud Emulator | LocalStack |
| Cloud SDK | boto3 |
| Programming Language | Python 3.11 |
| CI/CD | GitHub Actions |
| Reporting | JSON + Markdown |
| Version Control | Git + GitHub |

---

## Project Structure

```text
multi-cloud-cost-hygiene/
│
├── terraform/
│   ├── modules/
│   │   └── network/
│   ├── main.tf
│   ├── variables.tf
│   └── outputs.tf
│
├── janitor/
│   ├── janitor.py
│   ├── constants.py
│   └── requirements.txt
│
├── samples/
│   ├── report.example.json
│   └── report.example.md
│
├── .github/
│   └── workflows/
│       └── ci.yml
│
└── README.md
```

## Local Development Setup

### Clone Repository

```bash
git clone https://github.com/MOHIT042005/multi-cloud-cost-hygiene.git
cd multi-cloud-cost-hygiene
docker run -d -p 4566:4566 --name localstack localstack/localstack:3.0
cd terraform
terraform init
terraform apply
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r janitor/requirements.txt
python janitor/janitor.py
```

## Cost Janitor Modes

### Dry Run Mode (Default)

Scans infrastructure without deleting resources.

```bash
python janitor/janitor.py
```

### Delete Mode

Deletes orphaned resources unless protected.

```bash
python janitor/janitor.py --delete
```

### Protected Resources

Resources tagged with:

```text
Protected=true
```
will never be deleted automatically.

---

## Sample Outputs

Generated reports:

- `report.json`
- `report.md`

Example reports are included inside:

```text
samples/
```

## GitHub Actions CI/CD Pipeline

The pipeline automatically:

1. Starts LocalStack
2. Initializes Terraform
3. Applies infrastructure
4. Runs Cost Janitor scans
5. Generates reports
6. Uploads artifacts

The workflow is located at:

```text
.github/workflows/ci.yml
```

## Engineering Decisions and Tradeoffs

### LocalStack Version Pinning

`localstack/localstack:3.0` was pinned instead of using `latest` to avoid compatibility and licensing issues introduced in newer releases.

### S3 Lifecycle Configuration

The S3 lifecycle resource was temporarily excluded during LocalStack execution due to LocalStack API compatibility limitations while preserving intended Terraform structure.

### Safe-by-Default Automation

The Cost Janitor defaults to dry-run mode to prevent unintended destructive actions.

### Protected Resource Handling

Resources tagged with `Protected=true` are skipped during delete operations to simulate production-grade governance safeguards.

---

## Future Improvements

- Multi-account scanning
- Slack/email notifications
- Cost Explorer integration
- Scheduled cleanup workflows
- Dashboard visualization
- Terraform drift detection
- Policy-as-code integration