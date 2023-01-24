# minio-ftp-forwarder
sftp forwarding files to MinIO endpoint. Docker-stack consisting of 2 containers: sftp-container (vsftp,openssh,supervisor on alpine) and a python-container running watchdog on the sftp-directory and forwarder files to MinIO.

## how to use

Obtain SSL-certificates for your host and reference them in the contents of your env_file. 

To obtain self-signed certificates on Ubuntu use the openssh command as follows:

Generate private key:

Generate certificate-request and provide information as requested:

Use the certificate-request to create a self-signed certificate valid for 365 days:
```bash
openssl.exe x509 -req -days 365 -in /etc/ssl/certs/mycsr.csr -signkey /etc/ssl/certs/mykey.key -out /etc/ssl/certs/mycert.crt
```

```
Update the contents of env_file to set ftp-user/password and specify target MinIO endpoint and path:

```bash
FTP_PASS=password
LOGGING_LEVEL=INFO
MINIO_ENDPOINT=http://localhost:9000
MINIO_BUCKET=wis2box-incoming
MINIO_USER=minio
MINIO_PASSWORD=minio123
MINIO_PATH=/foo/bar
SFTP_ENABLED=true
SFTP_PRIVATE_KEY_FILE=mykey.key
SFTP_CERT_FILE=mycert.crt
```

Then start with

```bash
docker-compose -f docker-compose-sftp-to-minio.yml --env-file env_file up -d --build
```

## on a remote host accessed using ssh

Please note that SFTP uses port 22 which is typically the same port used to provide remote SSH-access on a cloud-instance or any other non-local machine. If you want to enable SFTP on your host while maintaining SSH-access, you will have to reconfigure SSH on your host to use a non-default port.

For example, on an Ubuntu machine, edit the /etc/ssh/sshd_config file and add/change Port 22 to the port that you want (i.e: Port 222) to connect through ssh and then do service ssh restart. You must ensure that the new port chosen is open for external access (for example by updating the security groups for the EC2-instance when running on AWS) and remember to take into account any port-blocking rules on your local network.
