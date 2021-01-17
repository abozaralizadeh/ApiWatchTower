![AWT](https://bitbucket.org/m4x4m/apiwatchtower/raw/54061db3311cdc43d7754b24e24cd41a67560601/static/logo.png)

# Api Watch Tower (AWT)

AWT is an open-source Django application for deep real-time API monitoring by periodical calls and evaluating the results, not only as a health checker but also for controlling the integrity and getting alerts in case of any unexpected changes to the result payload itself. Aimed to use along with other tools like Grafana to visualise the data and setting alert systems.

To see the demo without applying any configuration, you can use the single container here: [abo0zar/single_awt](https://hub.docker.com/repository/docker/abo0zar/single_awt)


## Installation

The easiest way to setup is using the docker container ([abo0zar/api_watch_tower:latest](https://hub.docker.com/repository/docker/abo0zar/api_watch_tower)) using the following Yaml file:



```yml
# docker-compose.yml

version: '3'

services:
  postgres:
    image: postgres
    restart: always
    environment:
      - POSTGRES_DB=AWT
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
    volumes:
      - postgresData:/var/lib/postgresql/data
    expose:
      - "5432"

  redis:
    image: redis
    restart: always
    command: redis-server
    expose:
      - "6379"

  awt_admin:
    image: abo0zar/api_watch_tower:latest
    restart: always
    container_name: "abozar_app_django"
    command: bash -c 'python manage.py migrate auth && python manage.py migrate && python manage.py runserver 0.0.0.0:8000'
    ports:
      - "8000:8000"
    depends_on:
      - postgres
    environment:
      - AAD_TENANT_ID=xxxOptionalxxx
      - AAD_CLIENT_ID=xxxOptionalxxx
      - HTTPS=off

  awt_worker:
    image: abo0zar/api_watch_tower:latest
    command: celery -A ApiWatchTower worker -B --concurrency=10
    depends_on:
      - redis
      - postgres
      - awt_admin

  awt_scheduler:
    image: abo0zar/api_watch_tower:latest
    restart: always
    command: celery -A ApiWatchTower beat -l info -S django --pidfile=
    depends_on:
      - redis
      - postgres
      - awt_admin
      - awt_worker

  grafana:
    image: grafana/grafana:latest
    restart: always
    container_name: "awt_grafana"
    volumes:
      - grafanaStorage:/var/lib/grafana
    depends_on:
      - postgres
    ports:
      - "3000:3000"

volumes:
    postgresData:
    grafanaStorage:

```

## Requirements

AWT works with Postgres as the database and to monitor the results you can use grafana. 
Also Redis is used as a broker for AWT celery workers. use nginx to serve both AWT and Grafana on the same port if needed, in that case yu need to run grafana behind a reverse proxy,
visit grafana documentation to achieve to that goal here: [run grafana behind a proxy](https://grafana.com/tutorials/run-grafana-behind-a-proxy/#2)

## Configurations

The following environment variables can be passed to all the containers that use AWT docker image:

#### HTTPS
**default:** off
Can have the values 'on' and 'off'

#### AWT_REDIS_HOST
**default:** redis

#### AWT_REDIS_PORT
**default:** 6379

#### AWT_LANGUAGE_CODE
**default:** it

#### AWT_TIME_ZONE
**default:** Europe/Rome

#### AWT_PG_DBNAME
**default:** AWT

#### AWT_PG_USERNAME
**default:** postgres

#### AWT_PG_PASSWORD
**default:** postgres

#### AWT_PG_HOST
**default:** postgres

#### AWT_PG_PORT
**default:** 5432

There are also some settings related to the configuration of Azure Active Directory login that can be find here: [django-azure-ad-auth](https://github.com/abozaralizadeh/django-azure-ad-auth)

Also to configure Grafana you can visit the official documentations but some usefull configurations are suggested here:

#### GF_SECURITY_ADMIN_USER
#### GF_SECURITY_ADMIN_PASSWORD
#### GF_SERVER_ROOT_URL
#### GF_INSTALL_PLUGINS

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
[MIT License](https://bitbucket.org/m4x4m/apiwatchtower/src/master/LICENSE) 

Copyright (c) 2021 Abozar Alizadeh

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

![AWT](https://bitbucket.org/m4x4m/apiwatchtower/raw/54061db3311cdc43d7754b24e24cd41a67560601/static/logo.png)