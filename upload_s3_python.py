#!/usr/bin/env python
# -*- coding: utf8 -*-"

import boto3
from botocore.client import ClientError
import requests
#import subprocess
import os

# Collecting information about EC2 instance from AWS service

user_data = 'http://169.254.169.254/latest/user-data'
meta_data = 'http://169.254.169.254/latest/meta-data'

ec2InsDatafile = 'ec2InsDatafile'
ec2_params = {
    'Instance ID': 'instance-id',
    'Reservation ID': 'reservation-id',
    'Public IP': 'public-ipv4',
    'Public Hostname': 'public-hostname',
    'Private IP':'local-ipv4',
    'Security Groups':'security-groups',
    'AMI ID': 'ami-id'
}

with open(ec2InsDatafile, 'w') as fh:
    for param, value in ec2_params.items():
        try: 
            response = requests.get(meta_data +'/' + value)
            print(response.text)
            ec2_params[param]=response.text

        except requests.RequestException as e:
            print(f"Error while making request {param}: {e}")
        if isinstance(response.text,list):
            print(response.text +': is list')
            data = ' '.join(response.text)
        else:
            data = param +":"+response.text
        try:
            fh.write(data+'\r\n')
        except:
            print('Error during writing to file')
            print(data)

    #Getting  OS related if from system files
    os_vers = "grep '^VERSION=' /etc/os-release |cut -d'=' -f2"
    os_name = "grep '^NAME' /etc/os-release |cut -d'=' -f2"
    os_name_val ="OS NAME: "+ os.popen(os_name).read().rstrip()
    os_vers_val ="OS VERSION: "+ os.popen(os_vers).read().rstrip()
    os_usrs = "grep -E 'bash|sh' /etc/passwd |awk -F : '{print $1}'|xargs echo  "
    os_usrs_val = "Login able users: " + os.popen(os_usrs).read().rstrip()
    try:
        fh.write(os_name_val+'\r\n')
        fh.write(os_vers_val+'\r\n')
        fh.write(os_usrs_val+'\r\n')
    except:
        print("Error during write to file")


#print(ec2_params)

print("uploading to bucket")
# Upload file to s3 storage
#s3_bucket_name = 'new-bucket-e05ab0e0'
s3_bucket_name = 'applicant-task'
s3_upload_path = 'r5d4/'
s3_conn = boto3.client('s3')

try:
    # no permissions
    #bckt_head = s3_conn.head_bucket(Bucket=s3_bucket_name)
    #print("bckt_head = " + bckt_head)

    with open(ec2InsDatafile, 'r') as fh2:
        #https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3/client/put_object.html
        response = s3_conn.put_object(
            Bucket = s3_bucket_name,
            Key = s3_upload_path + "system_info" + ec2_params['Instance ID'] + ".txt",
            Body = fh2.read()
        )
        print(response)
    print("File has been uploaded into " + s3_bucket_name + "/" + s3_upload_path + " S3 bucket with instance_id key.")
except ClientError as e:
    print(e.response['Error']['Message'])
    print("Are you sure the destination bucket exist? Check it.")
