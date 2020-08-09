# Dockerfile
FROM python:3.7
RUN pip3 install pipenv --upgrade
#COPY requirements.txt* /code/
#RUN pipenv install -r requirements.txt
RUN mkdir /code
WORKDIR /code
COPY Pipfile* /code/
RUN pipenv install --system --deploy --ignore-pipfile
#RUN pipenv install -e git+https://github.com/abozaralizadeh/django-azure-ad-auth.git#egg=azure-ad-auth
#COPY requirements.txt /code/
#RUN pip install -r requirements.txt
ADD ApiWatchTower /code/
