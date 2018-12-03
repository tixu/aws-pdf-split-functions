#!/bin/bash
echo 'deleting zip file';
rm handler.zip ; 
echo 'zipping archive'
cd .vendor
zip -r9 ../handler-split.zip *;
cd ..
zip -g handler-split.zip handler.py 
echo 'uploading function'
aws --profile user s3 cp handler-split.zip s3://smals-ocr-deploy;
echo 'deploying function'
#aws lambda update-function-code --s3-bucket lambdazip2 --s3-key handler-split.zip --function-name print-python  --region eu-central-1 --profile user

