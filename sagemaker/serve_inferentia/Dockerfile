FROM amazonlinux:2

# hadolint ignore=SC3003
RUN echo $'[neuron] \n\
name=Neuron YUM Repository \n\
baseurl=https://yum.repos.neuron.amazonaws.com \n\
enabled=1' > /etc/yum.repos.d/neuron.repo \
    && rpm --import https://yum.repos.neuron.amazonaws.com/GPG-PUB-KEY-AMAZON-AWS-NEURON.PUB

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
    seaborn

WORKDIR /work

COPY ./requirements.txt /work/

# hadolint ignore=DL3006,DL3013
RUN pip3 install --no-cache-dir --upgrade pip \
    && pip3 install --no-cache-dir --requirement requirements.txt

RUN git clone https://github.com/WongKinYiu/yolov7.git prg

WORKDIR /work/prg

# hadolint ignore=DL3013,SC2102
RUN pip3 install --no-cache-dir --upgrade pip \
    && pip3 config set global.extra-index-url https://pip.repos.neuron.amazonaws.com \
    && pip3 install --no-cache-dir torch-neuron==1.8.1.2.3.0.0 "protobuf<4" \
    && pip3 install --no-cache-dir torchvision==0.9.1 --no-deps

COPY ./app/* /work/prg/

RUN chmod +x /work/prg/serve

ENV PATH="/work/prg:${PATH}"
