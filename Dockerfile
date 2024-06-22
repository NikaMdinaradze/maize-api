FROM python:3.11.5-slim-bullseye

ENV PIP_DISABLE_PIP_VERSION_CHECK true
ENV PYTHONDONTWRITEBYTECODE true
ENV PYTHONUNBUFFERED true

WORKDIR /code

COPY ./requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . /code

ADD scripts/docker-entrypoint-dev.sh /root/docker-entrypoint-dev.sh
ADD scripts/check_service.py /root/check_service.py

RUN chmod +x /root/docker-entrypoint-dev.sh

ENTRYPOINT ["/root/docker-entrypoint-dev.sh"]
