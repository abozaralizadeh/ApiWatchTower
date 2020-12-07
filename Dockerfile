# Dockerfile
FROM python:3.7
#RUN pip3 install pipenv --upgrade
RUN mkdir /code
WORKDIR /code
COPY . /code/
#RUN pipenv install --system --deploy --ignore-pipfile
RUN pip install -r requirements.txt