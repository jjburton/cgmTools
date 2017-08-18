from __future__ import print_function
import os
import sys
import argparse
import boto3
import magic
from botocore.exceptions import ClientError

def upload_to_s3(bucket, artefact):
    try:
        client = boto3.client('s3')
    except ClientError as err:
        print("Failed to create boto3 client.\n" + str(err))
        return False
    for root, dirs, files in os.walk(artefact, topdown=False):
        for file in files:
            try:
                if ".css" in file:
                    mimetype = "text/css"
                elif ".js" in file:
                    mimetype = "text/javascript"
                else:
                    mimetype = magic.from_file(os.path.join(root, file), mime=True)
                client.upload_file(os.path.join(root, file), bucket, os.path.join(root, file).replace(artefact+"/", ""), ExtraArgs={'ContentType': mimetype, 'ACL': "public-read"})
            except ClientError as err:
                print("Failed to upload artefact to S3.\n" + str(err))
                return False
            except IOError as err:
                print("Failed to access artefact in this directory.\n" + str(err))
                return False
    return True


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("bucket", help="Name of the existing S3 bucket")
    parser.add_argument("artefact", help="Name of the artefact to be uploaded to S3")
    args = parser.parse_args()

    if not upload_to_s3(args.bucket, args.artefact):
        sys.exit(1)

if __name__ == "__main__":
    main()