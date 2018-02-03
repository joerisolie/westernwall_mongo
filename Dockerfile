FROM ubuntu:16.04

LABEL "owner"="jso"

RUN apt-get update && apt-get install -y \
	python3 \
	python3-venv\
	libpq-dev\
	python3-dev\
	iproute2\
	gcc
COPY ./source /source
WORKDIR /source

#Next line only for "dirty" source
RUN rm -rf venv

RUN python3 -m venv venv
RUN venv/bin/pip install --upgrade pip && venv/bin/pip install -r reqs.txt

CMD ["venv/bin/python3", "run.py"]

