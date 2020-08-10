# Dockerfile
FROM python:3.7
RUN pip3 install pipenv --upgrade
RUN mkdir /code
WORKDIR /code
COPY Pipfile* /code/
RUN pipenv install --system --deploy --ignore-pipfile
ADD ApiWatchTower /code/
