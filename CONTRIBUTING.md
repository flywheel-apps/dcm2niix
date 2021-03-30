# Contributing

## Setup

Development environment is based on Docker. To build the docker dev environment
run the following:

```
docker build -t flywheel/dcm2niix:latest .
docker build -t flywheel/dcm2niix-test:latest -f tests/Dockerfile .
```

`flywheel/dcm2niix-test:latest` is the docker image you can use for development
and testing. 

