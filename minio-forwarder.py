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


from datetime import datetime

import logging
import os
from pathlib import Path
import sys
import time

from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler

from minio import Minio

logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))
LOGGER = logging.getLogger('MinioForwarder')

WATCHPATH = '/home/vsftpd/'
POLLING_INTERVAL = 5
FILE_PATTERNS = '*.*'

import sys

from minio import Minio

class MinioForwarder:
    """
    Class combining watchdog with forward to MinIO
    """

    def __init__(self, minio_client: Minio, minio_bucket: str, watchpath: str):
        """
        initializer

        :param minio_client: Minio class instance defining minio end-point
        :param minio_bucket: 'str' defining bucket to upload to
        :param watchpath: 'str' path defining local directory to be watched

        :returns: `None`
        """
        self.minio_client = minio_client
        self.minio_bucket = minio_bucket
        self.watchpath = watchpath
        self.observer = Observer()
        file_patterns = FILE_PATTERNS.split(',')
        LOGGER.info(f'Init event-handler on patterns: {file_patterns}')

        self.event_handler = PatternMatchingEventHandler(
            patterns=file_patterns,
            ignore_patterns=[],
            ignore_directories=True)

        self.event_handler.on_any_event = self.on_any_event
        self.event_handler.on_closed = self.on_create_update
        self.event_handler.on_moved = self.on_create_update

    def run(self, polling_interval: int):
        """
        Run watch
        :param path: `pathlib.Path` of directory path
        :param polling_interval: `int` of polling interval
        :returns: `None`
        """

        LOGGER.info(f'Starting watchdog-observer on path={self.watchpath}')
        self.observer.schedule(self.event_handler, self.watchpath, recursive=True)
        self.observer.start()
        try:
            while True:
                now = datetime.now().isoformat()
                LOGGER.debug(f'Heartbeat {now}')
                time.sleep(polling_interval)
        except Exception as err:
            LOGGER.error(f'Observing error: {err}')
            self.observer.stop()
        self.observer.join()

    def upload_to_minio(self,filepath: Path):
        """
        Upload to MinIO
        :param filepath: file to be uploaded
        :returns: `None`
        """

        # remove the watchpath
        identifier = filepath.replace(self.watchpath,'')
        LOGGER.info(f"Put into {self.minio_bucket} : {filepath} as {identifier}")
        self.minio_client.fput_object(self.minio_bucket, identifier, filepath)

    def on_any_event(self, event: object) -> None:
        LOGGER.debug(event)

    def on_create_update(self, event: object) -> None:
        """
        action to take when new file is created
        :param event: watchdog-event
        :returns: `None`
        """
        LOGGER.debug(f'event-type={event.event_type}')
        path = event.src_path if event.event_type != 'moved' else event.dest_path
        LOGGER.debug(f'path={path}')

        if path[-3:] == 'tmp':
            LOGGER.info('skip tmp file')
            return

        LOGGER.info(f'Received file: {path}')
        LOGGER.info('Upload file to MinIO')

        try:
            self.upload_to_minio(path)
        except Exception as err:
            LOGGER.error(f'Failed to forward to MinIO: {err}')
            return
        # TODO on sucess remove file


def main():
    """
    Watch a directory for new files and forward the file to MinIO
    """

    LOGGING_LOGLEVEL = os.environ.get('LOGGING_LEVEL','INFO')
    print(f"Log level = {LOGGING_LOGLEVEL}")
    LOGGER.setLevel(LOGGING_LOGLEVEL)

    minio_endpoint = os.environ.get('MINIO_ENDPOINT')
    minio_user = os.environ.get('MINIO_ROOT_USER')
    minio_password = os.environ.get('MINIO_ROOT_PASSWORD')
    minio_bucket = 'wis2box-incoming'
    is_secure = False
    
    LOGGER.info(f"Prepare Minio-client to be used by MinioForwarder")
    LOGGER.info(f"minio_endpoint={minio_endpoint}")
    LOGGER.info(f"minio_user={minio_user}")
    LOGGER.info(f"minio_bucket={minio_bucket}")
    if minio_endpoint.startswith('https://'):
        is_secure = True
        minio_endpoint = minio_endpoint.replace('https://', '')
    else:
        minio_endpoint = minio_endpoint.replace('http://', '')
    
    ftp_user = os.environ.get('FTP_USER')
    watchpath = f'/home/vsftpd/{ftp_user}'

    minio_client = Minio(
        endpoint=minio_endpoint,
        access_key=minio_user,
        secret_key=minio_password,
        secure=is_secure)
    # hardcode watch-path to match vsftpd-home
    w = MinioForwarder(minio_client=minio_client,minio_bucket=minio_bucket,watchpath=watchpath)
    LOGGER.info(f"Listening to {watchpath} every {POLLING_INTERVAL} second")  # noqa
    w.run(polling_interval=int(POLLING_INTERVAL))
    w.disconnect()


if __name__ == '__main__':
    main()