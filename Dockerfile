FROM public.ecr.aws/lambda/python:3.9

RUN yum install ca-certificates -y

COPY requirements.txt requirements-tests.txt setup.cfg /var/task/

RUN python -m venv venv && \
  source ./venv/bin/activate && \
  pip install --upgrade pip && \
  pip install --requirement requirements-tests.txt --target "/var/task"

COPY src tests /var/task/

CMD [ "handler.canary_handler" ]
