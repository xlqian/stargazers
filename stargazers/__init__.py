from flask import Flask
from flask_restful import Api
import logging

from .interfaces import v1

app = Flask(__name__)

app.logger.setLevel(logging.INFO)

api = Api(app)

v1.init(api)

# create the db
from stargazers.model import create_sample_db, create_db

from time import sleep
# TODO: a proper way to wait for the db to be ready (pg_*)
sleep(5)
# create_sample_db()
# TODO: should be done properly in an another docker with schema migration...
create_db()
# TODO: move it into a proper worker/docker, Asynchronous worker to fill/update the db?
from .github_crawler import fill_db
import os
owner = os.environ.get('STARGAZERS_OWNER') or "xlqian"
repo = os.environ.get('STARGAZERS_REPO') or "navitia"
token = os.environ.get('STARGAZERS_GITHUB_TOKEN') or "token"
fill_db(owner, repo, token)
