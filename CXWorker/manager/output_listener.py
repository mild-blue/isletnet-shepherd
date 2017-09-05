from io import BytesIO

import logging
import requests
from minio import Minio

from .registry import ContainerRegistry


class OutputListener:
    """
    Waits for output from containers and stores it
    """

    def __init__(self, registry: ContainerRegistry, minio: Minio):
        self.registry = registry
        self.minio = minio

    def listen(self):
        while True:
            container_ids = self.registry.wait_for_output()

            for id in container_ids:
                output = self.registry.read_output(id)
                request = self.registry.get_current_request(id)
                self.minio.put_object(request.id, request.result_url, BytesIO(output), len(output))

                if request.status_url is not None:
                    requests.post(request.status_url, json={
                        "success": True,
                        "status": "Done"
                    })

                self.registry.request_finished(id)
