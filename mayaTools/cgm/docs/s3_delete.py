from __future__ import print_function
import os
import sys
import argparse
import boto3
#import zipfile
from botocore.exceptions import ClientError

def empty_bucket(bucket):
    try:
        resource = boto3.resource('s3')
    except ClientError as err:
        print("Failed to create boto3 resource.\n" + str(err))
        return False
    print("Removing all objects from bucket: " + bucket)
    resource.Bucket(bucket).objects.delete()
    return True


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("bucket", help="Name of the existing S3 bucket to empty")
    args = parser.parse_args()

    if not empty_bucket(args.bucket):
        sys.exit(1)

if __name__ == "__main__":
    main()