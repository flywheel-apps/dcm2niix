# Dockerfile for dcm2niix gear

FROM neurodebian:bionic

MAINTAINER Flywheel <support@flywheel.io>

# install fsl for pydeface
RUN echo deb http://neurodeb.pirsquared.org data main contrib non-free >> /etc/apt/sources.list.d/neurodebian.sources.list
RUN echo deb http://neurodeb.pirsquared.org bionic main contrib non-free >> /etc/apt/sources.list.d/neurodebian.sources.list
RUN apt-get update \
    && apt-get install -y fsl-core
RUN echo ". /etc/fsl/5.0/fsl.sh" >> /root/.bashrc

# python setup
RUN apt-get update \
    && apt-get install -y python3-pip
COPY requirements.txt ./requirements.txt
RUN pip3 install -r requirements.txt

# install packages for building and executing dcm2niix
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

# compile dcm2niix from source (version 31-March-2020 (v1.0.20200331))
ENV DCMCOMMIT=485c387c93bbca3b29b93403dfde211c4bc39af6
RUN curl -#L  https://github.com/rordenlab/dcm2niix/archive/$DCMCOMMIT.zip | bsdtar -xf- -C /usr/local
WORKDIR /usr/local/dcm2niix-${DCMCOMMIT}/build
RUN cmake -DUSE_OPENJPEG=ON -MY_DEBUG_GE=ON ../ && \
    make && \
    make install

# flywheel spec (v0)
ENV FLYWHEEL /flywheel/v0
RUN mkdir -p ${FLYWHEEL}
WORKDIR ${FLYWHEEL}

# copy in fix_dcm_vols.py from source
ENV FIXDCMCOMMIT=918ee3327174c3c736e7b3839a556e0a709730c8
RUN curl -#L https://raw.githubusercontent.com/VisionandCognition/NHP-Process-MRI/$FIXDCMCOMMIT/bin/fix_dcm_vols > ${FLYWHEEL}/fix_dcm_vols.py
RUN chmod +x ${FLYWHEEL}/fix_dcm_vols.py

# copy in scripts
COPY manifest.json ${FLYWHEEL}/manifest.json
COPY arrange.py \
     dcm2niix.py \
     metadata.py \
     pydeface.py \
     resolve.py \
     run.py \
     utils.py ${FLYWHEEL}/
RUN chmod +x ${FLYWHEEL}/run.py

# FIX: replicate Flywheel for testing
COPY config.json ${FLYWHEEL}/config.json
RUN mkdir -p ${FLYWHEEL}/input
RUN mkdir -p ${FLYWHEEL}/output
COPY assets/aliza_siemens_trio.zip ${FLYWHEEL}/input/aliza_siemens_trio.zip

# set the entrypoint
# ENTRYPOINT ["python3 run.py"]
