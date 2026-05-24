import json
from datetime import datetime

import boto3
from rich import print

from constants import (
    EBS_GP3_PRICE_PER_GB,
    ACCOUNT_ID,
    AWS_REGION,
    STOPPED_INSTANCE_THRESHOLD_DAYS,
    REQUIRED_TAGS
)

def check_missing_tags(resource_tags):

    missing_tags = []

    # Convert AWS tag structure into simple dictionary
    tags_dict = {}

    if resource_tags:

        for tag in resource_tags:
            tags_dict[tag["Key"]] = tag["Value"]

    # Check required tags
    for required_tag in REQUIRED_TAGS:

        if required_tag not in tags_dict:
            missing_tags.append(required_tag)

    return missing_tags

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
    volume_tags = volume.get("Tags", [])
    missing_tags = check_missing_tags(volume_tags)

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

    # Detect missing required tags
if missing_tags:

    finding = {
        "resource_id": volume_id,
        "resource_type": "ebs_volume",
        "reason": "missing_required_tags",
        "age_days": 0,
        "estimated_monthly_cost_usd": 0,
        "tags": {
            "missing": missing_tags
        },
        "suggested_action": "add_required_tags",
        "safe_to_auto_delete": False
    }

    findings.append(finding)

    print(
        f"[bold red]MISSING TAGS DETECTED:[/bold red] "
        f"{missing_tags}"
    )

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

print("\n[bold blue]Scanning EC2 Instances...[/bold blue]\n")

instances_response = ec2.describe_instances()

for reservation in instances_response["Reservations"]:

    for instance in reservation["Instances"]:

        instance_id = instance["InstanceId"]
        instance_state = instance["State"]["Name"]

        print(f"[green]Instance ID:[/green] {instance_id}")
        print(f"[yellow]State:[/yellow] {instance_state}")

        # Detect stopped instances
        if instance_state == "stopped":

            finding = {
                "resource_id": instance_id,
                "resource_type": "ec2_instance",
                "reason": "stopped_instance",
                "age_days": STOPPED_INSTANCE_THRESHOLD_DAYS,
                "estimated_monthly_cost_usd": 5.00,
                "tags": {},
                "suggested_action": "investigate",
                "safe_to_auto_delete": False
            }

            findings.append(finding)

            print("[bold red]STOPPED INSTANCE DETECTED[/bold red]")

        print("-" * 50)

        print("\n[bold blue]Scanning Elastic IPs...[/bold blue]\n")


addresses_response = ec2.describe_addresses()

for address in addresses_response["Addresses"]:

    allocation_id = address.get("AllocationId", "unknown")
    association_id = address.get("AssociationId")

    print(f"[green]Elastic IP Allocation ID:[/green] {allocation_id}")

    # Detect unassociated Elastic IPs
    if association_id is None:

        finding = {
            "resource_id": allocation_id,
            "resource_type": "elastic_ip",
            "reason": "unassociated_elastic_ip",
            "age_days": 0,
            "estimated_monthly_cost_usd": 3.60,
            "tags": {},
            "suggested_action": "release",
            "safe_to_auto_delete": False
        }

        findings.append(finding)

        print("[bold red]UNUSED ELASTIC IP DETECTED[/bold red]")

    print("-" * 50)