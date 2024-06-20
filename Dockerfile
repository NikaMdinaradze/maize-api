FROM python:3.11.5-slim-bullseye

ENV PIP_DISABLE_PIP_VERSION_CHECK true
ENV PYTHONDONTWRITEBYTECODE true
ENV PYTHONUNBUFFERED true

WORKDIR /code

COPY ./requirements.txt .
RUN pip install -r requirements.txt

COPY . /code

RUN useradd -ms /bin/bash maize-user
RUN chown -R maize-user:maize-user /code

ADD scripts/docker-entrypoint-dev.sh /home/maize-user/docker-entrypoint-dev.sh
ADD scripts/check_service.py /home/maize-user/check_service.py

RUN chmod +x /home/maize-user/docker-entrypoint-dev.sh
USER maize-user

ENTRYPOINT ["/home/maize-user/docker-entrypoint-dev.sh"]
