FROM ubuntu:14.04
RUN localedef -i en_US -f UTF-8 en_US.UTF-8 \
    && apt-get update \
    && apt-get install -y python python-setuptools python-pip python3 python3-setuptools python3-pip python3-debian python-debian
WORKDIR /code