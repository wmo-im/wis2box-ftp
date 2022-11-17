# minio-ftp-forwarder
ftp forwarding files to MinIO endpoint

## how to use

Update the contents of env_file and then start with

```bash
docker-compose -f docker-compose-minio-ftp.yml --env-file env_file up -d --build
```
