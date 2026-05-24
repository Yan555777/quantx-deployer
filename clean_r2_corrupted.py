"""
Scans R2 options-data bucket for corrupted SPXW parquet files and deletes them.
A file is considered corrupted if:
  - Size is 0 bytes
  - Size is suspiciously small (< 50KB — real SPXW files are 30-60MB)

Run this locally, then re-run Modal precompute to re-download clean files.
"""
import boto3
import sys

ENDPOINT   = "https://7f835882a6c11ee760fe4e96eb8cbef2.r2.cloudflarestorage.com"
ACCESS_KEY = "50d381bdebfc205fceb2da9a449da664"
SECRET_KEY = "95317a57904438863431dc871dcb1a831bf685eeecfd90587887b02b3db7af17"
BUCKET     = "options-data"
PREFIX     = "SPXW/greeks_1min_daily/"
MIN_SIZE   = 50_000  # 50KB — anything smaller is corrupted

s3 = boto3.client(
    "s3",
    endpoint_url=ENDPOINT,
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY,
    region_name="auto",
)

print(f"Scanning s3://{BUCKET}/{PREFIX} for corrupted files...")
print(f"Min valid size: {MIN_SIZE/1e3:.0f} KB\n")

corrupted = []
total_scanned = 0

paginator = s3.get_paginator("list_objects_v2")
for page in paginator.paginate(Bucket=BUCKET, Prefix=PREFIX):
    for obj in page.get("Contents", []):
        total_scanned += 1
        size = obj["Size"]
        key  = obj["Key"]
        if size < MIN_SIZE:
            corrupted.append((key, size))
            print(f"  CORRUPTED: {key} ({size/1e3:.1f} KB)")

print(f"\nScanned: {total_scanned} files")
print(f"Corrupted: {len(corrupted)} files")

if not corrupted:
    print("✅ No corrupted files found!")
    sys.exit(0)

# Ask before deleting
print(f"\nDelete {len(corrupted)} corrupted files from R2? (yes/no): ", end="")
confirm = input().strip().lower()

if confirm != "yes":
    print("Aborted — no files deleted.")
    sys.exit(0)

# Delete in batches of 1000
deleted = 0
batch = []
for key, size in corrupted:
    batch.append({"Key": key})
    if len(batch) == 1000:
        s3.delete_objects(Bucket=BUCKET, Delete={"Objects": batch})
        deleted += len(batch)
        batch = []

if batch:
    s3.delete_objects(Bucket=BUCKET, Delete={"Objects": batch})
    deleted += len(batch)

print(f"✅ Deleted {deleted} corrupted files from R2.")
print("Now re-run Modal precompute to download fresh copies.")
