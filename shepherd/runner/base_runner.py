import logging
import os
import os.path as path
import re
import traceback
from abc import abstractmethod

import zmq
import zmq.asyncio

from shepherd.comm import *
from shepherd.constants import INPUT_DIR, OUTPUT_DIR


def n_available_gpus() -> int:
    """
    Return the number of NVIDIA GPU devices available to this process.

    .. note::
        This method attempts to parse (in-order) ``CUDA_VISIBLE_DEVICES`` env variable (bare sheep) and
        ``NVIDIA_VISIBLE_DEVICES`` env variable (docker sheep).
        If none of these variables is available, it lists GPU devices in ``/dev``.

    :return: the number of available GPU devices
    """
    if 'CUDA_VISIBLE_DEVICES' in os.environ:
        devices = os.environ['CUDA_VISIBLE_DEVICES']
    elif 'NVIDIA_VISIBLE_DEVICES' in os.environ and not os.environ['NVIDIA_VISIBLE_DEVICES'].strip() == 'all':
        devices = os.environ['NVIDIA_VISIBLE_DEVICES']
    else:
        devices = ','.join(filter(lambda d: re.search(r'nvidia[0-9]+', d) is not None, os.listdir('/dev')))

    return len(devices.split(',')) if len(devices) > 0 else 0


class BaseRunner:
    """
    Base **emloop** runner class suitable for inheritance when implementing a runner with custom behavior.
    :py:class:`BaseRunner` manages the socket, messages and many more. See :py:meth:`_process_job` for more info.
    """

    def __init__(self, config_path: str, port: int, stream_name: str):
        """Create new :py:class:`Runner`."""
        logging.info('Creating runner from `%s` listening on port %s', config_path, port)

        # bind to the socket
        self._port = port
        self._socket = None

        self._config_path: str = config_path
        self._stream_name: str = stream_name

    @abstractmethod
    def _process_job(self, input_path: str, output_path: str) -> None:
        """
        Process a job with having inputs in the ``input_path`` and save the outputs to the ``output_path``.

        :param input_path: input directory path
        :param output_path: output directory path
        """

    async def process_all(self) -> None:
        """Listen on the ``self._socket`` and process the incoming jobs in an endless loop."""
        logging.info('Starting the loop')
        try:
            logging.debug('Creating socket')
            self._socket: zmq.Socket = zmq.asyncio.Context.instance().socket(zmq.ROUTER)
            self._socket.setsockopt(zmq.IDENTITY, b"runner")
            self._socket.bind("tcp://0.0.0.0:{}".format(self._port))
            while True:
                logging.info('Waiting for a job')
                input_message: InputMessage = await Messenger.recv(self._socket, [InputMessage])
                job_id = input_message.job_id
                io_data_root = input_message.io_data_root
                logging.info('Received job `%s` with io data root `%s`', job_id, io_data_root)
                try:
                    input_path = path.join(io_data_root, job_id, INPUT_DIR)
                    output_path = path.join(io_data_root, job_id, OUTPUT_DIR)
                    self._process_job(input_path, output_path)
                    logging.info('Job `%s` done, sending DoneMessage', job_id)
                    await Messenger.send(self._socket, DoneMessage(dict(job_id=job_id)), input_message)

                except BaseException as ex:
                    logging.exception(ex)

                    logging.error('Sending ErrorMessage for job `%s`', job_id)
                    short_erorr = "{}: {}".format(type(ex).__name__, str(ex))
                    long_error = str(traceback.format_tb(ex.__traceback__))
                    error_message = ErrorMessage(dict(job_id=job_id, message=short_erorr,
                                                      exception_traceback=long_error, exception_type=str(type(ex))))
                    await Messenger.send(self._socket, error_message, input_message)
        finally:
            if self._socket is not None:
                self._socket.close(0)
