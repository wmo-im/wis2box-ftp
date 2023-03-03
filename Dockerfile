###############################################################################
#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
#
###############################################################################

FROM ubuntu:focal
ENV GID=1000 \
	UID=1000

ARG DEBIAN_FRONTEND=noninteractive
ARG USER_ID=1014
ARG GROUP_ID=1050

RUN apt-get update && apt-get -y install vsftpd openssh-server supervisor python3 python3-pip libpam-pwdfile apache2-utils
RUN pip3 install watchdog minio

RUN usermod -u ${USER_ID} ftp
RUN groupmod -g ${GROUP_ID} ftp

ENV FTP_USER **String**
ENV FTP_PASS **Random**
ENV PASV_ADDRESS **IPv4**
ENV PASV_ADDR_RESOLVE NO
ENV PASV_ENABLE YES
ENV PASV_MIN_PORT 21100
ENV PASV_MAX_PORT 21110
ENV XFERLOG_STD_FORMAT NO
ENV FILE_OPEN_MODE 0666
ENV LOCAL_UMASK 077
ENV REVERSE_LOOKUP_ENABLE YES
ENV PASV_PROMISCUOUS NO
ENV PORT_PROMISCUOUS NO

COPY vsftpd.conf /etc/vsftpd/
COPY vsftpd_virtual /etc/pam.d/
COPY run-vsftpd.sh /usr/sbin/

RUN chmod +x /usr/sbin/run-vsftpd.sh
RUN mkdir -p /home/vsftpd/
RUN chown -R ftp:ftp /home/vsftpd/

COPY sshd_config /etc/ssh/sshd_config
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf
COPY entrypoint.sh /entrypoint.sh
COPY minio-forwarder.py /usr/src/app/

RUN chmod +x /usr/src/app/docker-entrypoint.sh

VOLUME /home/vsftpd
VOLUME /var/log/vsftpd

CMD [ "/usr/bin/supervisord","-c","/etc/supervisor/conf.d/supervisord.conf" ]
ENTRYPOINT [ "/entrypoint.sh" ]
EXPOSE 20/tcp 21/tcp 22/tcp 40000-40009/tcp
HEALTHCHECK CMD netstat -lnt | grep :21 || exit 1
