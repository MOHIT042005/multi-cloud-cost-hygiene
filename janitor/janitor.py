import boto3
from rich import print

# Create EC2 client connected to LocalStack
ec2 = boto3.client(
    "ec2",
    region_name="us-east-1",
    endpoint_url="http://localhost:4566",
    aws_access_key_id="test",
    aws_secret_access_key="test"
)

# Call AWS API to retrieve all EBS volumes
volumes_response = ec2.describe_volumes()

print("\n[bold blue]Scanning EBS Volumes...[/bold blue]\n")

# Loop through all returned volumes
for volume in volumes_response["Volumes"]:

    volume_id = volume["VolumeId"]
    volume_state = volume["State"]
    volume_size = volume["Size"]

    print(f"[green]Volume ID:[/green] {volume_id}")
    print(f"[yellow]State:[/yellow] {volume_state}")
    print(f"[cyan]Size:[/cyan] {volume_size} GB")

    # Detect unattached/orphaned volumes
    if volume_state == "available":
        print("[bold red]ORPHAN DETECTED: Unattached EBS Volume[/bold red]")

    print("-" * 50)