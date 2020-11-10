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
COPY requirements.txt ./requirements.txt
RUN pip3 install -r requirements.txt

# Install packages for building and executing dcm2niix
RUN apt-get update -qq \
    && apt-get install -y \
    git \
    curl \
    build-essential \
    cmake \
    pkg-config \
    libgdcm-tools \
    bsdtar \
    unzip \
    pigz

# Compile dcm2niix from source (version 2-November-2020 (v1.0.20201102))
ENV DCMCOMMIT=081c6300d0cf47088f0873cd586c9745498f637a
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
ADD dcm2niix ${FLYWHEEL}/dcm2niix
ADD pydeface ${FLYWHEEL}/pydeface
ADD utils ${FLYWHEEL}/utils
COPY run.py ${FLYWHEEL}/run.py
RUN chmod +x ${FLYWHEEL}/run.py
