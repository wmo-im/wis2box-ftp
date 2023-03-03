
from ftplib import FTP
import requests
import os
import time

ftp_user = os.environ.get('FTP_USER','wis2box')
ftp_password = os.environ.get('FTP_PASS','wis2box123')

filename = 'test/test-data/hello_world.txt'
# connect to local FTP and copy test-file
print(f"Copy file {filename} to local ftp")
session = FTP('localhost',ftp_user,ftp_password)
with open(filename,'rb') as f:
    session.storbinary(f'STOR hello_world.txt', f) 
session.quit()
print('wait 5 seconds')
time.sleep(5)
print('check file is in bucket')
res = requests.get('http://127.0.0.1:9000/wis2box-incoming/hello_world.txt')
print(res)
# raise exception in case of failure
res.raise_for_status()