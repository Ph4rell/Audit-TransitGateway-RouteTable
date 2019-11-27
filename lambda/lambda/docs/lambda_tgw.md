# lambda_tgw

Script to export all the transit route table from a account to a S3 bucket
and download all the file and extract the TGW attachment - VPC Id
Outputs : TGW Attchments and VPC ID
TODO
function to download - function to extract
add destination CIDR ?

## lambda_handler
```python
lambda_handler(event, context)
```

Func Lambda Handler
:param envent
:param context
:return

## download_files_from_s3
```python
download_files_from_s3(bucket_name)
```

Func to download content of the bucket to /tmp/
:return: no return

## delete_files
```python
delete_files(bucket_name)
```

Func to delete files from bucket and bucket himself
:param bucket_name: string
:return: no return

## bucket_exists
```python
bucket_exists(bucket_name)
```

Func to test if the bucket exist or not
:param bucket_name: string
:return: bool

## create_temp_bucket_s3
```python
create_temp_bucket_s3(bucket_name)
```

Func to create temporary s3 bucket to store data
:param bucket_name: string
:return: bucketname

## list_tgw_routetable
```python
list_tgw_routetable()
```

Func to list all the tgw route table ID
:return: Return tgw route table id

## export_data_to_s3
```python
export_data_to_s3(tgw_routetable_id, bucket)
```

Func to export the tgw route table to S3
:param tgw_routetable_id: list
:param bucket: string
:return: no return

