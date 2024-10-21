# Nice to have:
# - uwsgi
# - apache

FROM python:3.10.14-slim-bullseye

RUN apt update && apt-get --yes install libpq-dev python-dev gcc

COPY stargazers /server/stargazers

WORKDIR /server
RUN pip3 install -r stargazers/requirements.txt


ENTRYPOINT ["flask", "--app", "stargazers", "run", "--host", "0.0.0.0", "--port", "5000" ]
