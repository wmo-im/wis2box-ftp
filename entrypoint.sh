#!/bin/sh

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

# needed by ssh
mkdir -p /run/sshd

# needed by vsftpd
mkdir -p /var/run/vsftpd/empty

touch /var/log/vsftpd.log
tail -f /var/log/vsftpd.log | tee /dev/stdout &
touch /var/log/vsftpd/vsftpd.log
tail -f /var/log/vsftpd/vsftpd.log | tee /dev/stdout &
touch /var/log/supervisord.log
tail -f /var/log/supervisord.log | tee /dev/stdout &

exec "$@"