import pulumi
import json
import os
import pulumi_aws as aws

# Create a bucket and expose a website index document
site_bucket = aws.s3.Bucket("siteBucket", website={
    "index_document": "index.html",
})
site_dir = "www"
# For each file in the directory, create an S3 object stored in `siteBucket`
files = []
for range in [{"key": k, "value": v} for [k, v] in enumerate(os.listdir(site_dir))]:
    files.append(aws.s3.BucketObject(f"files-{range['key']}",
        bucket=site_bucket.id,
        key=range["value"],
        source=pulumi.FileAsset(f"{site_dir}/{range['value']}"),
        content_type=range["value"],
        opts = pulumi.ResourceOptions(deleted_with=site_bucket)))
# set the MIME type of the file
# Set the access policy for the bucket so all objects are readable
bucket_policy = aws.s3.BucketPolicy("bucketPolicy",
    bucket=site_bucket.id,
    policy=pulumi.Output.json_dumps({
        "Version": "2012-10-17",
        "Statement": [{
            "Effect": "Allow",
            "Principal": "*",
            "Action": ["s3:GetObject"],
            "Resource": [site_bucket.id.apply(lambda id: f"arn:aws:s3:::{id}/*")],
        }],
    }))
pulumi.export("bucketName", site_bucket.bucket)
pulumi.export("websiteUrl", site_bucket.website_endpoint)
