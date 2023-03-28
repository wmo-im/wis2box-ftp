#!/bin/bash

# If no env var for FTP_USER has been specified, use 'admin':
if [ "$FTP_USER" = "**String**" ]; then
    export FTP_USER='admin'
fi

# If no env var has been specified, generate a random password for FTP_USER:
if [ "$FTP_PASS" = "**Random**" ]; then
    export FTP_PASS=`cat /dev/urandom | tr -dc A-Z-a-z-0-9 | head -c${1:-16}`
fi

# Create home dir and update vsftpd user db:
mkdir -p "/home/vsftpd/${FTP_USER}"
chown -R ftp:ftp /home/vsftpd/

# add user to password-file
mkdir -p /etc/vsftpd
htpasswd -c -p -b /etc/vsftpd/ftpd.passwd $FTP_USER $(openssl passwd -1 -noverify $FTP_PASS)

# add the pasv_address
echo "pasv_address=${PASV_ADDRESS}" >> /etc/vsftpd/vsftpd.conf

# Get log file path
export LOG_FILE=`grep xferlog_file /etc/vsftpd/vsftpd.conf|cut -d= -f2`

/usr/bin/ln -sf /dev/stdout $LOG_FILE

# Run vsftpd:
&>/dev/null /usr/sbin/vsftpd /etc/vsftpd/vsftpd.conf