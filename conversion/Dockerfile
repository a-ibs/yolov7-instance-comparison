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
        git \
        vim \
        wget \
    && yum clean all

WORKDIR /tmp

RUN git clone https://github.com/WongKinYiu/yolov7.git

WORKDIR /tmp/yolov7

# hadolint ignore=DL3013,DL3059
RUN pip3 install --no-cache-dir \
    pandas \
    requests \
    urllib3==1.26.15 \
    Pillow \
    opencv-python \
    tqdm \
    pyyaml \
    matplotlib \
    seaborn

# hadolint ignore=DL3033
RUN yum install -y \
    mesa-libGL.x86_64 \
    gcc \
    gcc-c++ \
    fontconfig \
    && yum clean all

# hadolint ignore=DL3013,SC2102
RUN pip3 install --no-cache-dir --upgrade pip \
    && pip3 config set global.extra-index-url https://pip.repos.neuron.amazonaws.com \
    && pip3 install --no-cache-dir torch-neuron==1.8.1.2.3.0.0 neuron-cc[tensorflow]==1.11.4.0 "protobuf<4" \
    && pip3 install --no-cache-dir torchvision==0.9.1 --no-deps

COPY ./convert_neuron.py /tmp/yolov7/

CMD ["python3", "convert_neuron.py"]
