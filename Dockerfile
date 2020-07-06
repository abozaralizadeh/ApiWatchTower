# Dockerfile
FROM python:3.7
RUN pip install pipenv
#COPY requirements.txt* /code/
#RUN pipenv install -r requirements.txt
RUN mkdir /code
WORKDIR /code
COPY Pipfile* /code/
RUN pipenv install --system --deploy --ignore-pipfile
ADD ApiWatchTower /code/
