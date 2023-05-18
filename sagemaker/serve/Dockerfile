FROM nvidia/cuda:11.2.1-cudnn8-devel

ENV DEBIAN_FRONTEND noninteractive

ENV TZ=Asia/Tokyo

# hadolint ignore=DL3008
RUN apt-key adv --keyserver keyserver.ubuntu.com --recv-keys A4B469963BF863CC \
    && apt-get update \
    && apt-get install --no-install-recommends --no-install-suggests -y \
        git \
        libopencv-dev \
        python3.8 \
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
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir --requirement requirements.txt

COPY ./app/* /work/prg/

RUN chmod +x /work/prg/serve

ENV PATH="/work/prg:${PATH}"
