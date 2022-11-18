# minio-ftp-forwarder
ftp forwarding files to MinIO endpoint. Docker-stack consisting of 2 containers: alpine-container running vsftp plus python-container running watchdog on ftp-directory and forwarder files to MinIO.

## how to use

Check if the vsftp.conf settings  work for you. You might have to set the pasv_address for you server:

```bash
pasv_address=192.168.100.104
pasv_addr_resolve=NO
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
```

Then start with

```bash
docker-compose -f docker-compose-minio-ftp.yml --env-file env_file up -d --build
```
