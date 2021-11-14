FROM python:3.8

# setup python
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

RUN pip3 install --upgrade pip
# Install system deps
RUN pip install "poetry==1.1.4"


# Copy only requirements to cache them in docker layer
WORKDIR /code
COPY poetry.lock pyproject.toml /code/

RUN poetry config virtualenvs.create false \
  && poetry install --no-dev --no-interaction --no-ansi


COPY . /code

ENTRYPOINT [ "./docker-entrypoint.sh" ]