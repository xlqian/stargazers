import logging

from flask_restful import Resource, reqparse

import stargazers.model as model
from .response import Response, Repo


class StarGazers(Resource):

    routes = ["/stargazers/<user>/<repository>", ]

    # serialization
    def get(self, user, repository):
        parser = reqparse.RequestParser()
        # argument
        # TODO: pagination?
        parser.add_argument('start_page', type=int, location='values', required=False)
        parser.add_argument('count', type=int, location='values', required=False)
        request = parser.parse_args()

        response = Response()
        # better http error message handling
        try:
            result = model.get_shared_stargazsers_repositories(user, repository, request['start_page'], request['count'])
        except Exception as e:
            logging.exception('')
            response.error = str(e)
            return response.model_dump(), 404

        response.repos = [Repo(repo_name=repo, stargazers=users) for repo, users in result.items()]

        return response.model_dump(exclude_none=True)
