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


LOGGER = logging.getLogger('MinioForwarder')
logging.basicConfig(stream=sys.stdout)

WATCHPATH = '/data/incoming'
POLLING_INTERVAL = 5
FILE_PATTERNS = '*.*'

import sys

from minio import Minio

class MinioForwarder:
    """
    Class combining watchdog with forward to MinIO
    """

    def __init__(self, minio_client: Minio, bucket_name: str):
        self.minio_client = minio_client
        self.minio_bucket = bucket_name
        self.observer = Observer()
        file_patterns = FILE_PATTERNS.split(',')
        LOGGER.info(f'Init event-handler on patterns: {file_patterns}')

        self.event_handler = PatternMatchingEventHandler(
            patterns=file_patterns,
            ignore_patterns=[],
            ignore_directories=True)

        self.event_handler.on_created = self.on_created

    def run(self, path: Path, polling_interval: int):
        """
        Run watch
        :param path: `pathlib.Path` of directory path
        :param polling_interval: `int` of polling interval
        :returns: `None`
        """

        LOGGER.info(f'Starting watchdog-observer on path={path}')
        self.observer.schedule(self.event_handler, path, recursive=True)
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

    def upload_to_minio(self,filepath):
        # remove the watchpath
        identifier = filepath.replace(WATCHPATH,'')
        LOGGER.debug(f"Put into {self.minio_bucket} : {filepath} as {identifier}")
        self.minio_client.fput_object(self.minio_bucket, identifier, filepath)

    def on_created(self, event):
        LOGGER.debug(f'Incoming event path: {event.src_path}')

        LOGGER.info(f'Received file: {event.src_path}')
        LOGGER.info('Upload file to MinIO')

        try:
            self.upload_to_minio(event.src_path)
        except Exception as err:
            LOGGER.error(f'Failed to forward to MinIO: {err}')
            return
        # TODO on sucess remove file


def main():
    """
    Watch a directory for new files and forward the file to MinIO
    """

    LOGGING_LOGLEVEL = os.environ.get('LOGGING_LEVEL','INFO')
    print(LOGGING_LOGLEVEL)
    LOGGER.setLevel(LOGGING_LOGLEVEL)

    minio_endpoint = os.environ.get('MINIO_ENDPOINT')
    minio_user = os.environ.get('MINIO_USER')
    minio_password = os.environ.get('MINIO_PASSWORD')
    minio_bucket = os.environ.get('MINIO_BUCKET')
    is_secure = False
    
    LOGGER.info(f"Prepare Minio-client to be used by MinioForwarder")
    LOGGER.info(f"minio_endpoint={minio_endpoint}")
    LOGGER.info(f"minio_user={minio_user}")
    LOGGER.info(f"minio_bucket={minio_user}")
    if minio_endpoint.startswith('https://'):
        is_secure = True
        minio_endpoint = minio_endpoint.replace('https://', '')
    else:
        minio_endpoint = minio_endpoint.replace('http://', '')
    
    minio_client = Minio(
        endpoint=minio_endpoint,
        access_key=minio_user,
        secret_key=minio_password,
        secure=is_secure)

    w = MinioForwarder(minio_client=minio_client,bucket_name=minio_bucket)
    LOGGER.info(f"Listening to {WATCHPATH} every {POLLING_INTERVAL} second")  # noqa
    w.run(path=WATCHPATH, polling_interval=int(POLLING_INTERVAL))
    w.disconnect()


if __name__ == '__main__':
    main()