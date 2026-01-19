FROM public.ecr.aws/lambda/python:3.14

RUN yum install ca-certificates -y

COPY requirements.txt requirements-tests.txt setup.cfg /var/task/

RUN python -m venv venv && \
  source ./venv/bin/activate && \
  PIP_INDEX_URL=https://artefacts.tax.service.gov.uk/artifactory/api/pypi/pips/simple pip install --upgrade pip && \
  PIP_INDEX_URL=https://artefacts.tax.service.gov.uk/artifactory/api/pypi/pips/simple pip install --requirement requirements-tests.txt --target "/var/task"

COPY src tests /var/task/

CMD [ "handler.canary_handler" ]
