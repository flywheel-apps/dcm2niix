ARG BASE

FROM ${BASE}

ENV FLYWHEEL="/flywheel/v0"

COPY tests ${FLYWHEEL}/tests
COPY .pre-commit-config.yaml .env ${FLYWHEEL}/
# .git to make repo git available to pre-commit hooks
COPY .git ${FLYWHEEL}/.git

# Installing pre-commit
RUN pip install pre-commit

# Need to install poetry with dev dependencies
RUN poetry install

RUN bash -c "source /etc/fsl/5.0/fsl.sh && PATH=/home/flywheel/.local/bin:\$PATH"

ENTRYPOINT [""]