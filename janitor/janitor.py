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

# Generate Markdown summary
markdown_lines = []

markdown_lines.append("# Cost Janitor Report\n")

markdown_lines.append(
    f"**Scan Timestamp:** {report['scan_timestamp']}\n"
)

markdown_lines.append(
    f"**Total Orphans Found:** {report['summary']['total_orphans']}\n"
)

markdown_lines.append(
    f"**Estimated Monthly Waste:** "
    f"${report['summary']['estimated_monthly_waste_usd']}\n"
)

markdown_lines.append("## Findings\n")

# Add findings into Markdown
for finding in findings:

    markdown_lines.append(
        f"### {finding['resource_id']}\n"
    )

    markdown_lines.append(
        f"- Resource Type: {finding['resource_type']}"
    )

    markdown_lines.append(
        f"- Reason: {finding['reason']}"
    )

    markdown_lines.append(
        f"- Estimated Monthly Cost: "
        f"${finding['estimated_monthly_cost_usd']}"
    )

    markdown_lines.append(
        f"- Suggested Action: "
        f"{finding['suggested_action']}\n"
    )

# Write Markdown report
with open("report.md", "w") as markdown_file:

    markdown_file.write("\n".join(markdown_lines))

print("[bold green]Markdown summary generated successfully[/bold green]")