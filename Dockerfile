FROM python:3.8

RUN pip3 install -U pipenv

COPY . /repo
RUN (cd /repo && make env)

WORKDIR /repo
ENTRYPOINT pipenv run webcheckctl

ENV export WEBCHECK_CONFIG=/config.yaml
ENV LANG=en_US.UTF-8
