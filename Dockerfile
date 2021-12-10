# Dockerfile for dcm2niix gear

FROM neurodebian:bionic

MAINTAINER Flywheel <support@flywheel.io>

# Install FSL for PyDeface
RUN echo deb http://neurodeb.pirsquared.org data main contrib non-free >> /etc/apt/sources.list.d/neurodebian.sources.list
RUN echo deb http://neurodeb.pirsquared.org bionic main contrib non-free >> /etc/apt/sources.list.d/neurodebian.sources.list
RUN apt-get update \
    && apt-get install -y fsl-core \
    && rm -rf /var/cache/apt/
RUN echo ". /etc/fsl/5.0/fsl.sh" >> /root/.bashrc

# Python setup - version 3.6 in base image
RUN apt-get update \
    && apt-get install -y python3-pip

# Install packages for building and executing dcm2niix
RUN apt-get update -qq &&\
    apt-get install -y \
        git \
        curl \
        build-essential \
        cmake \
        pkg-config \
        libgdcm-tools \
        bsdtar \
        unzip \
        pigz

# Install additional libraries for added calls below
RUN apt-get update -qq && \
    apt-get install -y \
        make \
        build-essential \
        libssl-dev \
        zlib1g-dev \
        libbz2-dev \
        libreadline-dev \
        libsqlite3-dev wget \
        llvm \
        libncurses5-dev \
        libncursesw5-dev \
        xz-utils \
        tk-dev \
        libffi-dev \
        liblzma-dev \
        python-openssl

# Install pyenv and then more recent version of Python for toolkit dependencies
RUN curl -L https://github.com/pyenv/pyenv-installer/raw/master/bin/pyenv-installer | bash
ENV PYENV_ROOT /root/.pyenv
ENV PATH $PYENV_ROOT/shims:$PYENV_ROOT/bin:$PATH
RUN eval "$(pyenv init -)"
RUN eval "$(pyenv virtualenv-init -)"
RUN pyenv install 3.9.0
RUN pyenv local 3.9.0

# Bring in toml file, install and run poetry package management
COPY pyproject.toml ./pyproject.toml
RUN pip3 install poetry
RUN poetry update
RUN poetry install
RUN export PATH=$PATH:$HOME/.poetry/bin

# Compile dcm2niix from source (version 6-October-2021 (v1.0.20211006))
ENV DCMCOMMIT=003f0d19f1e57b0129c9dcf3e653f51ca3559028
RUN curl -#L  https://github.com/rordenlab/dcm2niix/archive/$DCMCOMMIT.zip | bsdtar -xf- -C /usr/local
WORKDIR /usr/local/dcm2niix-${DCMCOMMIT}/build
RUN cmake -DUSE_OPENJPEG=ON -MY_DEBUG_GE=ON ../ && \
    make && \
    make install

# Flywheel spec (v0)
ENV FLYWHEEL /flywheel/v0
RUN mkdir -p ${FLYWHEEL}
WORKDIR ${FLYWHEEL}

# Copy in fix_dcm_vols.py from source
ENV FIXDCMCOMMIT=918ee3327174c3c736e7b3839a556e0a709730c8
RUN curl -#L https://raw.githubusercontent.com/VisionandCognition/NHP-Process-MRI/$FIXDCMCOMMIT/bin/fix_dcm_vols > ${FLYWHEEL}/fix_dcm_vols.py
RUN chmod +x ${FLYWHEEL}/fix_dcm_vols.py

# Copy in gear scripts
COPY manifest.json ${FLYWHEEL}/manifest.json
ADD fw_gear_dcm2niix ${FLYWHEEL}/fw_gear_dcm2niix
COPY run.py ${FLYWHEEL}/run.py

# Installing the current project main dependencies (most likely to change, above layer(s) can be cached)

# Dev install. git for pip editable install.
# RUN \
#    apt-get update && \
#    apt-get install -y git && \
#    pip install "poetry==1.1.2"

# Note: poetry requires a README.md to install the current project
COPY \
    README.md \
    pyproject.toml \
    poetry.lock \
    $FLYWHEEL/
RUN poetry install --no-dev

# Configure entrypoint
RUN chmod +x ${FLYWHEEL}/run.py
ENTRYPOINT ["poetry","run","python","/flywheel/v0/run.py"]
