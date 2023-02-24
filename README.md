# Shepherd

Provides access to computation resources on a single machine.

## IsletNet specification
[IsletNet](https://github.com/mild-blue/isletnet) uses some functionality of the 
Shepherd library for image processing, with the ability to customize it. 
In addition to the required dependencies described in [setup.py](setup.py), 
more dependencies are installed for IsletNet computations 
([requirements here](https://github.com/mild-blue/isletnet/blob/master/backend/shepherd/requirements.txt) + TensorFlow).
Special [config file](https://github.com/mild-blue/isletnet/blob/master/backend/shepherd/config.yaml) 
with storage, sheep and logging is also a part of the IsletNet repository.

## Development Guide

### Prerequisites

1. Install dependencies with `pip install .`
On every change, do this step. Otherwise, when launching the application, 
the old unmodified version will be run. Shepherd works as a library
2. Make sure you have Docker installed and that your user has permissions to use 
   it
3. If you intend to run computations on a GPU, install also `nvidia-docker2`

### Launching the Shepherd

First, you need to have a Docker registry and a Minio server running. The 
easiest way to achieve this is to use the Docker Compose example:

```
docker-compose -f examples/docker/docker-compose-sandbox.yml up -d
```

Second, you need a configuration file. Again, examples found in the `examples/configs/` 
folder are a great starting point. Feel free to pick one of those and edit it to 
your needs.

Finally, you need to run the following command to start the shepherd:

```
shepherd -c examples/configs/shepherd-docker-cpu.yml
```

Be sure to adjust the command line parameters according to your needs (`-h` is 
your host address, `-p` is the port number where the shepherd API server listens 
and `-c` is the path to the configuration file).

After launching the shepherd, there will be an HTTP API available on the 
configured port that can be used to control the shepherd.

### Processing a Request Directly
<i>(The relevance of this information has not been confirmed for a long time).</i></br>

To process a request for debugging purposes, you need to:

- choose a request id
- create a bucket on your Minio server with a name same as your request id
- put the payload (input for the model) in `<yourbucket>/inputs/input.json`
- invoke the `/start-job` API endpoint with your chosen request id
- after the job is processed, the result should be stored in Minio, in 
  `<yourbucket>/outputs.json`

### Running Tests

First, install the test requirements `pip install '.[tests]'`.
The test suite can be run with `python setup.py test`.

### Running Stress Tests
<i>(The relevance of this information has not been confirmed for a long time).</i></br>

First, install the test requirements `pip install '.[tests]'`.

To launch stress test, run:
```
docker-compose -f examples/docker/docker-compose-sandbox.yml up -d
shepherd -c tests/stress/shepherd-bare.yml
molotov tests/stress/loadtest.py -p 2 -w 10 -d 60 -xv
```
You can modify stress test arguments: `-p` (number of processes), `-w` (number of workers) and 
`-d` (number of seconds to run the test).

You can also run stress test with time measurements:
```
molotov --use-extension tests/stress/measure_time.py --max-runs 10 tests/stress/loadtest.py
```

### Logging
We log every request Shepherd receives from sheep and clients. 
The process logs, which refer to sheep, are saved in files specified 
for the corresponding sheep as `stderr_file` and `stdout_file` in the config. 
The logs for Shepherd itself are saved in a file whose directory is specified in 
the `logging_directory` parameter of the `logging` section in the config 
(if not specified, the default value `../logs` is used). 
Additionally, the logging level can be set in the same logging 
section by changing the `level` parameter (default is `debug`).
