FROM amazonlinux:2

# hadolint ignore=DL3033
RUN yum update -y \
    && yum install -y \
        python3 \
        pciutils \
        mesa-libGL.x86_64 \
        gcc \
        gcc-c++ \
        fontconfig \
        git \
    && rm -rf /var/cache/yum/* \
    && yum clean all

# hadolint ignore=DL3013
RUN pip3 install --no-cache-dir \
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

WORKDIR /work

COPY ./requirements.txt /work/

# hadolint ignore=DL3006,DL3013
RUN pip3 install --no-cache-dir --upgrade pip \
    && pip3 install --no-cache-dir --requirement requirements.txt

RUN git clone https://github.com/WongKinYiu/yolov7.git prg

WORKDIR /work/prg

# hadolint ignore=DL3006,DL3013
RUN pip3 install --no-cache-dir --upgrade pip \
    && pip3 install --no-cache-dir torch==1.8.1 torchvision==0.9.1

COPY ./app/* /work/prg/

RUN chmod +x /work/prg/serve

ENV PATH="/work/prg:${PATH}"
