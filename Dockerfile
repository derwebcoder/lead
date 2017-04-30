FROM python:3.5.3-alpine
MAINTAINER Marvin Becker <marvinbecker[at]derwebcoder[dot]de>

ADD ./lead.py /root/lead.py

RUN set -x && \
    pip install docker && \
    chmod +x /root/lead.py && \
    mkdir /source

WORKDIR /source

ENTRYPOINT ["python3", "/root/lead.py"]