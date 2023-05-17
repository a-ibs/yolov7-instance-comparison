FROM arm64v8/ubuntu:20.04

ENV DEBIAN_FRONTEND noninteractive

ENV TZ=Asia/Tokyo

# hadolint ignore=DL3008
RUN apt-get update \
        && apt-get install --no-install-recommends --no-install-suggests -y \
                gnupg2 \
        && apt-get clean \
        && rm -rf /var/lib/apt/lists/*

# hadolint ignore=DL3008
RUN apt-key adv --keyserver keyserver.ubuntu.com --recv-keys A4B469963BF863CC \
        && apt-get update \
        && apt-get install --no-install-recommends --no-install-suggests -y \
                gcc-aarch64-linux-gnu \
                g++-aarch64-linux-gnu \
                git \
                libopencv-dev \
                python3.8-dev \
                python3-pip \
        && apt-get clean \
        && rm -rf /var/lib/apt/lists/* \
        && update-alternatives --install /usr/bin/python python /usr/bin/python3.8 1

WORKDIR /work

COPY ./requirements.txt /work/

# hadolint ignore=DL3006,DL3013
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir --requirement requirements.txt

WORKDIR /work

RUN git clone https://github.com/WongKinYiu/yolov7.git prg

WORKDIR /work/prg

# hadolint ignore=DL3006,DL3013
RUN pip3 install --no-cache-dir --upgrade pip \
    && pip3 install --no-cache-dir \
        torch==2.0.1 \
        torchvision==0.15.2 \
        pandas \
        requests \
        Pillow \
        opencv-python \
        tqdm \
        pyyaml \
        matplotlib \
        seaborn \
        scipy \
        tensorboard

COPY ./app/* /work/prg/

RUN chmod +x /work/prg/serve

ENV PATH="/work/prg:${PATH}"
