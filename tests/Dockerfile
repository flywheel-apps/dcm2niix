ARG BASE

FROM ${BASE}

COPY . /flywheel/v0/`

RUN bash -c "source /etc/fsl/5.0/fsl.sh && pip3 install --user -r tests/requirements.txt && PATH=/home/flywheel/.local/bin:\$PATH"
