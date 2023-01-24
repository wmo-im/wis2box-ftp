#!/bin/sh



if [ $FTP_SSL_ENABLED == true ]
then
  echo "using SSL enabled config"
  cp -rf /etc/vsftpd-ssl.conf /etc/vsftpd.conf
else
  echo "using non-SSL enabled config"
  cp -rf /etc/vsftpd-nossl.conf /etc/vsftpd.conf
fi  

# Generate unique ssh keys for this container, if needed
if [ ! -f /etc/ssh/ssh_host_ed25519_key ]; then
    echo "generating new unique ssh-key with -t ed255519"
    ssh-keygen -t ed25519 -f /etc/ssh/ssh_host_ed25519_key -N ''
    chmod 600 /etc/ssh/ssh_host_ed25519_key || true
fi
if [ ! -f /etc/ssh/ssh_host_rsa_key ]; then
    echo "generating new unique ssh-key with -t rsa -b 4096"
    ssh-keygen -t rsa -b 4096 -f /etc/ssh/ssh_host_rsa_key -N ''
    chmod 600 /etc/ssh/ssh_host_rsa_key || true
fi



mkdir -p /data/incoming
mkdir -p /data/ftp-users

# Create a group for the ftp user
addgroup -g $GID -S ftpaccess

# create user
adduser -D -G ftpaccess -h /data/incoming -s /bin/false -u $UID $FTP_USER
mkdir -p /data/incoming
chown root:ftpaccess /data/incoming
chmod 750 /data/incoming

mkdir -p /data/incoming/data
chown $FTP_USER:ftpaccess /data/incoming/data
chmod 750 $FTP_USER:ftpaccess /data/incoming/data

# set/update password
echo "$FTP_USER:$FTP_PASS" | /usr/sbin/chpasswd

touch /var/log/vsftpd.log
tail -f /var/log/vsftpd.log | tee /dev/stdout &
touch /var/log/xferlog
tail -f /var/log/xferlog | tee /dev/stdout &
touch /var/log/supervisord.log
tail -f /var/log/supervisord.log | tee /dev/stdout &

exec "$@"