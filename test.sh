#!/bin/bash 
echo erasing test file; 
aws --profile user s3 rm s3://pdfin/in/scan7.pdf 
echo pushing file;
aws --profile user s3 cp ../scan7.pdf s3://pdfin/in/scan7.pdf

