# Script to export all the transit route table from a account to a S3 bucket 
# and download all the file and extract the TGW attachment - VPC Id
# Outputs : TGW Attchments and VPC ID
# TODO 
# function to download - function to extract
# add destination CIDR ?

import json
import boto3
import botocore
import logging
from random import randint
import os

def lambda_handler(event, context):

    temp_bucket = "d2si-temp-bucket-s3"


    if bucket_exists(temp_bucket):
        print(f"Bucket {temp_bucket} exist !")
        delete_bucket(temp_bucket)
        lambda_handler(event, context)
        
    
    else:
        print(f"Bucket {temp_bucket} don't exist !")
        create_temp_bucket_s3(temp_bucket)

        for i in list_tgw_routetable():
            export_data_to_s3(i, temp_bucket)
        
def delete_bucket(bucket_name):
    """
    Func to delete files from bucket and bucket himself
    """
    s3 = boto3.resource("s3")
    bucket = s3.Bucket(bucket_name)
    for key in bucket.objects.all():
        key.delete()
    bucket.delete()


def bucket_exists(bucket_name):
    """
    Func to test if the bucket exist or not
    """

    s3 = boto3.client('s3')
    try:
        response = s3.head_bucket(Bucket=bucket_name)
    except botocore.exceptions.ClientError as e:
        logging.debug(e)
        return False
    return True
        
def create_temp_bucket_s3(bucket_name):
    """
    Func to create temporary s3 bucket to store data
    """
    s3 = boto3.resource("s3")

    bucket = s3.create_bucket(
        Bucket = bucket_name,
        ACL = "private",
        CreateBucketConfiguration = {
            "LocationConstraint": "eu-west-1"
        }
    )  
    return bucket


def list_tgw_routetable():
    """
    Func to list all the tgw route table ID
    Return tgw route table id
    """
    client = boto3.client("ec2")
    tgw_table = list()
    try:
        tables = client.describe_transit_gateway_route_tables()
        for table in tables["TransitGatewayRouteTables"]:
            #tgw_table_name = (table["Tags"][2].get("Value"))
            tgw_table.append(table["TransitGatewayRouteTableId"])

    except botocore.exceptionsClientError as error:
        print(error)

    return tgw_table


def export_data_to_s3(tgw_routetable_id, bucket):
    """
    Func to export the tgw route table to S3
    """
    client = boto3.client("ec2")
    try:
        client.export_transit_gateway_routes(
            TransitGatewayRouteTableId=tgw_routetable_id, \
            S3Bucket=bucket
        )
    
    except ClientError as error:
        print(error)



# try:
#     files = list()
#     bucket = s3.Bucket(bucket)

#     for s3_object in bucket.objects.all():
#         path, filename = os.path.split(s3_object.key)
#         bucket.download_file(s3_object.key, filename)

#         files.append(filename)
    
#     for file in files:
#         print('')
#         print(
#             f"Name Route Table: {tgw_table_name}" \
#             f"Route Table ID: {tgw_table}" \
#             f"File: {file}"
#         )
        
#         with open(file, 'r') as json_file:
#             data = json.load(json_file)
            
#             for assoc in data["routes"]:
#                 destCIDR = assoc.get("destinationCidrBlock")
#                 attachId = assoc["transitGatewayAttachments"][0].get('transitGatewayAttachmentId')
#                 vpc = assoc["transitGatewayAttachments"][0].get("resourceId")

#                 print(f'CIDR Dest: {destCIDR} Attachment: {attachId} VPC: {vpc}')

# except ClientError as error:
#     for e in error.response["Error"]["Code"]:
#         print(e)


if __name__ == "__main__":
    event = 1
    context = 1
    lambda_handler(event, context)
