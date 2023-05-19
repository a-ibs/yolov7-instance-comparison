FROM nvidia/cuda:11.2.1-cudnn8-devel

ENV DEBIAN_FRONTEND noninteractive

# hadolint ignore=DL3008
RUN apt-key adv --keyserver keyserver.ubuntu.com --recv-keys A4B469963BF863CC \
    && apt-get update \
    && apt-get install --no-install-recommends --no-install-suggests -y \
        gnupg2 \
        ca-certificates \
        libgl1-mesa-dev \
        libopencv-dev \
        git \
        jq \
        wget \
        python3.8 \
        python3-pip \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && update-alternatives --install /usr/bin/python python /usr/bin/python3.8 1

ENV PATH="${HOME}/.local/bin:${PATH}"

RUN git clone https://github.com/WongKinYiu/yolov7.git /work

WORKDIR /work

RUN wget --quiet --continue \
    --timestamping https://github.com/WongKinYiu/yolov7/releases/download/v0.1/yolov7x_training.pt \
    --output-document ./yolov7x_training.pt

# hadolint ignore=DL3013,DL3059
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir \
        torch==1.8.1 \
        torchvision==0.9.1 \
        numpy==1.23.5 \
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

RUN sed -ie "s/                'paste_in': (1, 0.0, 1.0)}.*/                'paste_in': (1, 0.0, 1.0),'loss_ota': (0, 0.0, 1.0)}/g" train.py

COPY ./app/cfg /work/cfg
COPY ./app/data /work/data
COPY ./app/train /work/train

RUN chmod +x /work/train

ENV PATH="/work:${PATH}"
