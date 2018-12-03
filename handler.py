from __future__ import print_function
import json
import io
import os
import boto3
from  PyPDF2 import PdfFileReader, PdfFileWriter
import time
import re
import urllib
import Queue as queue
from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.core import patch_all

patch_all()

s3 = boto3.resource('s3')
dynamodb = boto3.resource('dynamodb')
bucket = os.getenv('output','smals-work-1')


@xray_recorder.capture('splitting')
def pdf_splitter(path, key):
    m = re.search('in/(.*).pdf', key)
    small_key = m.group(1)
    pdf = PdfFileReader(path)
    for page in range(pdf.getNumPages()):
        pdf_writer = PdfFileWriter()
        pdf_writer.addPage(pdf.getPage(page))
        r = page+1
      
        output_filename = '{}_page_{:0>5d}.pdf'.format(
            "/tmp/temp", r)
            
        split_key = '{}/page{:0>5d}.pdf'.format(small_key,r)
        with open(output_filename, 'wb') as out:
            pdf_writer.write(out)
        print('Created: {}'.format(output_filename))
        try:
          print('putting objet {} into bucket {}'.format(split_key,bucket))
            
          s3.Object(bucket, split_key).put(Body=open(output_filename, 'rb'))
          print('Created: {}'.format(split_key))
        except Exception as e:
            print(e)
@xray_recorder.capture('storing info')
def store_info(path,key):
    with open(path, 'rb') as f:
        pdf = PdfFileReader(f)
        info = pdf.getDocumentInfo()
        number_of_pages = pdf.getNumPages()
    print(info)
    print("page number %d " % (number_of_pages))
    base = key[3:-4]
    try:
      table = dynamodb.Table('FAN')
      table.put_item(Item={'ID':base,'instance': number_of_pages})
    except Exception  as e: 
      print ("got an exception while inserting in db {}".format(e))
def F(event, context):
    bucket = event['Records'][0]['s3']['bucket']['name']
    for record in event['Records']:
        key = urllib.unquote_plus(record['s3']['object']['key'])
        try:
          print("Bucket: "+ bucket)
          print("Key: "+ key)
          obj = s3.Object(bucket_name=bucket, key=record['s3']['object']['key'])
        except Exception as e:
          print(e)
          print('Error getting object {} from bucket {}. Make sure they exist '
                'and your bucket is in the same region as this '
                'function.'.format(key, bucket))
          raise e
        try:
          response = obj.get()
          body = response['Body']
          with io.FileIO('/tmp/temp.pdf', 'w') as file:
               while file.write(body.read(amt=512)):
                   pass
        except Exception as e:
            print(e)
            print('Error writing file')
            raise e
        store_info('/tmp/temp.pdf',key)
        pdf_splitter('/tmp/temp.pdf',key)
