# wis2box-ftp

An additional service for the wis2box to enable forwarding data to MinIO via FTP.

Docker-container runs vsftp, openssh and a python-script using to watchdog to forward files from the sftp-directory to MinIO.

## without SSL

```bash
FTP_USER=wis2box
FTP_PASS=wis2box123
FTP_SSL_ENABLED=false
LOGGING_LEVEL=INFO
WIS2BOX_STORAGE_USER=minio
WIS2BOX_STORAGE_PASSWORD=minio123
```

## with SSL

Set FTP_ENABLED=true

Obtain SSL-certificates for your host, and map them to /etc/ssl/certs/vsftpd.crt and /etc/ssl/private/vsftpd.key in the container

To obtain self-signed certificates on Ubuntu use the openssh command as follows:

```bash
sudo openssl req -x509 -newkey rsa:4096 -keyout mykey.key -out mycert.crt -sha256 -days 365 -nodes
```

## on a remote host accessed using ssh

Please note that SFTP uses port 22 which is typically the same port used to provide remote SSH-access on a cloud-instance or any other non-local machine. If you want to enable SFTP on your host while maintaining SSH-access, you will have to reconfigure SSH on your host to use a non-default port.

For example, on an Ubuntu machine, edit the /etc/ssh/sshd_config file and add/change Port 22 to the port that you want (i.e: Port 222) to connect through ssh and then do service ssh restart. You must ensure that the new port chosen is open for external access (for example by updating the security groups for the EC2-instance when running on AWS) and remember to take into account any port-blocking rules on your local network.
