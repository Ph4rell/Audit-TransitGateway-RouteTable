# Script to export all the transit route table from a account to a S3 bucket 
# and download all the file and extract the TGW attachment - VPC Id
# Outputs : TGW Attchments and VPC ID
# TODO 
# function to export - function to download - function to extract
# add destination CIDR ?

import json
import boto3
from botocore.exceptions import ClientError
import os

client = boto3.client('ec2')
s3 = boto3.resource('s3')

bucket = "engieexportroutetabletransitgw"

try:
    tables = client.describe_transit_gateway_route_tables()

    for table in tables["TransitGatewayRouteTables"]:

        tgw_table_name = (table["Tags"][2].get("Value"))
        tgw_table = (table["TransitGatewayRouteTableId"])
        #client.export_transit_gateway_routes(TransitGatewayRouteTableId=tgw_table, S3Bucket=bucket)

except ClientError as error:
    print("bucket")
    raise IOError(f"Error with {error.message}")


try:
    files = list()
    bucket = s3.Bucket(bucket)

    for s3_object in bucket.objects.all():
        path, filename = os.path.split(s3_object.key)
        bucket.download_file(s3_object.key, filename)

        files.append(filename)
    
    for file in files:
        print('')
        print(
            f"Name Route Table: {tgw_table_name}" \
            f"Route Table ID: {tgw_table}" \
            f"File: {file}"
        )
        
        with open(file, 'r') as json_file:
            data = json.load(json_file)
            
            for assoc in data["routes"]:
                destCIDR = assoc.get("destinationCidrBlock")
                attachId = assoc["transitGatewayAttachments"][0].get('transitGatewayAttachmentId')
                vpc = assoc["transitGatewayAttachments"][0].get("resourceId")

                print(f'CIDR Dest: {destCIDR} Attachment: {attachId} VPC: {vpc}')

except ClientError as error:
    for e in error.response["Error"]["Code"]:
        print(e)
    