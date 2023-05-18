FROM nvidia/cuda:11.2.1-cudnn8-devel

ENV DEBIAN_FRONTEND noninteractive

ENV TZ=Asia/Tokyo

# hadolint ignore=DL3008
RUN apt-key adv --keyserver keyserver.ubuntu.com --recv-keys A4B469963BF863CC \
    && apt-get update \
    && apt-get install --no-install-recommends --no-install-suggests -y \
        libopencv-dev \
        git \
        python3.8 \
        python3-pip \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && update-alternatives --install /usr/bin/python python /usr/bin/python3.8 1

WORKDIR /work

RUN git clone https://github.com/WongKinYiu/yolov7.git

WORKDIR /work/yolov7

# hadolint ignore=DL3006,DL3013
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir --requirement requirements.txt \
    && pip install --no-cache-dir torch==1.8.1 "protobuf<4" \
    && pip install --no-cache-dir torchvision==0.9.1 --no-deps
