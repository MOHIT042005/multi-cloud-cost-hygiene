import json
from datetime import datetime

import boto3
from rich import print

from constants import (
    EBS_GP3_PRICE_PER_GB,
    ACCOUNT_ID,
    AWS_REGION
)

# Create EC2 client connected to LocalStack
ec2 = boto3.client(
    "ec2",
    region_name=AWS_REGION,
    endpoint_url="http://localhost:4566",
    aws_access_key_id="test",
    aws_secret_access_key="test"
)

# Store orphan findings
findings = []

print("\n[bold blue]Scanning EBS Volumes...[/bold blue]\n")

# Retrieve all EBS volumes
volumes_response = ec2.describe_volumes()

# Loop through volumes
for volume in volumes_response["Volumes"]:

    volume_id = volume["VolumeId"]
    volume_state = volume["State"]
    volume_size = volume["Size"]

    print(f"[green]Volume ID:[/green] {volume_id}")
    print(f"[yellow]State:[/yellow] {volume_state}")
    print(f"[cyan]Size:[/cyan] {volume_size} GB")

    # Detect orphaned volume
    if volume_state == "available":

        estimated_cost = round(
            volume_size * EBS_GP3_PRICE_PER_GB,
            2
        )

        finding = {
            "resource_id": volume_id,
            "resource_type": "ebs_volume",
            "reason": "unattached",
            "age_days": 0,
            "estimated_monthly_cost_usd": estimated_cost,
            "tags": {},
            "suggested_action": "delete",
            "safe_to_auto_delete": False
        }

        findings.append(finding)

        print("[bold red]ORPHAN DETECTED[/bold red]")

    print("-" * 50)

# Build final report structure
report = {
    "scan_timestamp": datetime.utcnow().isoformat() + "Z",
    "account_id": ACCOUNT_ID,
    "region": AWS_REGION,
    "summary": {
        "total_orphans": len(findings),
        "estimated_monthly_waste_usd": round(
            sum(
                finding["estimated_monthly_cost_usd"]
                for finding in findings
            ),
            2
        )
    },
    "findings": findings
}

# Write JSON report
with open("report.json", "w") as report_file:
    json.dump(report, report_file, indent=4)

print("\n[bold green]Report generated successfully[/bold green]")