from flask_restful import Api


from .index import Index
from .stargazers import StarGazers


def init(api: Api):
    api.add_resource(Index, "/v1/index")
    api.add_resource(StarGazers, *[f"/v1/{route}" for route in StarGazers.routes])

    """
    for resource in [Index, User, Repository]:
        api.add_resource(resource, *[f"/v1/{route}" for route in resource.routes])
    """
