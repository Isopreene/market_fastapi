FROM python:3.12
WORKDIR app/

RUN apt-get update \
    && apt-get install -y gcc python3-dev musl-dev libmagic1 libffi-dev netcat-traditional \
    build-essential libpq-dev

COPY pyproject.toml poetry.lock /
RUN pip3 install poetry
RUN poetry config virtualenvs.create false \
  && poetry install --no-interaction --no-ansi


COPY script.sh /script.sh
RUN chmod +x /script.sh

WORKDIR /app
COPY . /app

ENTRYPOINT ["bash", "/app/script.sh"]