'''
Script to export all the transit route table from a account to a S3 bucket 
and download all the file and extract the TGW attachment - VPC Id
Outputs : TGW Attchments and VPC ID
TODO
function to download - function to extract
add destination CIDR ?
'''
#import json
import logging
#from random import randint
import os
import boto3
import botocore

def lambda_handler(event, context):
    """
    Func Lambda Handler
    :param envent
    :param context
    :return
    """

    temp_bucket = "d2si-temp-bucket-s3"


    if bucket_exists(temp_bucket):
        print(f"Bucket {temp_bucket} exist !")
        # Delete the old files in the bucket
        delete_files(temp_bucket)

        for rt in list_tgw_routetable():
            export_data_to_s3(rt, temp_bucket)
        download_files_from_s3(temp_bucket)
    else:
        print(f"Bucket {temp_bucket} don't exist !")
        # Create the bucket
        create_temp_bucket_s3(temp_bucket)

        for rt in list_tgw_routetable():
            export_data_to_s3(rt, temp_bucket)
        download_files_from_s3(temp_bucket)

def download_files_from_s3(bucket_name):
    """
    Func to download content of the bucket to /tmp/
    :return: no return
    """
    s3 = boto3.resource("s3")

    bucket = s3.Bucket(bucket_name)

    for s3_object in bucket.objects.all():
        try:
            path, filename = os.path.split(s3_object.key)
            bucket.download_file(s3_object.key, "/tmp/" + filename)
        except botocore.exceptions.ClientError as error:
            if error.response['Error']['Code'] == "404":
                print(f"The object {s3_object.key} does not exist")
            else:
                raise

def delete_files(bucket_name):
    """
    Func to delete files from bucket and bucket himself
    :param bucket_name: string
    :return: no return
    """
    s3 = boto3.resource("s3")

    bucket = s3.Bucket(bucket_name)
    for key in bucket.objects.all():
        key.delete()
    # Delete the bucket if we want to    
    #bucket.delete()

def bucket_exists(bucket_name):
    """
    Func to test if the bucket exist or not
    :param bucket_name: string
    :return: bool
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
    :param bucket_name: string
    :return: bucketname
    """
    s3 = boto3.resource("s3")

    bucket = s3.create_bucket(
        Bucket=bucket_name,
        ACL="private",
        CreateBucketConfiguration={
            "LocationConstraint": "eu-west-1"
        }
    )
    return bucket

def list_tgw_routetable():
    """
    Func to list all the tgw route table ID
    :return: Return tgw route table id
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
    :param tgw_routetable_id: list
    :param bucket: string
    :return: no return
    """
    client = boto3.client("ec2")
    try:
        client.export_transit_gateway_routes(
            TransitGatewayRouteTableId=tgw_routetable_id, \
            S3Bucket=bucket
        )
    except botocore.exceptions.ClientError as error:
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
