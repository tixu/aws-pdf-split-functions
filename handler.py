from __future__ import print_function
import json
import io
import boto3
from  PyPDF2 import PdfFileReader, PdfFileWriter
import time
import re
import urllib


s3 = boto3.resource('s3')

def pdf_splitter(path, key):
    m = re.search('in/(.*).pdf', key)
    small_key = m.group(1)
    pdf = PdfFileReader(path)
    for page in range(pdf.getNumPages()):
        pdf_writer = PdfFileWriter()
        pdf_writer.addPage(pdf.getPage(page))
        r = page+1
      
        output_filename = '{}_page_{}.pdf'.format(
            "/tmp/temp", r)
            
        split_key = 'scan/{}/page{}.pdf'.format(small_key,r)
        with open(output_filename, 'wb') as out:
            pdf_writer.write(out)
        print('Created: {}'.format(output_filename))
        try: 
            
          s3.Object('telos-1', split_key).put(Body=open(output_filename, 'rb'))
          print('Created: {}'.format(split_key))
        except Exception as e:
            print(e)
            
def get_info(path):
    with open(path, 'rb') as f:
        pdf = PdfFileReader(f)
        info = pdf.getDocumentInfo()
        number_of_pages = pdf.getNumPages()
    print(info)
    print("page number %d " % (number_of_pages))


def F(event, context):
    bucket = event['Records'][0]['s3']['bucket']['name']
    for record in event['Records']:
        key = urllib.parse.unquote_plus(record['s3']['object']['key'])
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
        response = obj.get()
        body = response['Body']
        try:
          with io.FileIO('/tmp/temp.pdf', 'w') as file:
             while file.write(body.read(amt=512)):
                pass
        except Exception as e:
            print(e)
            print('Error writing file')
            raise e
        get_info('/tmp/temp.pdf')
        pdf_splitter('/tmp/temp.pdf',key)
