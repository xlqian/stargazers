from typing import List, Optional
from pydantic import BaseModel


class Repo(BaseModel):
    repo_name: str
    stargazers: List[str]


class Response(BaseModel):
    repos: List[Repo] = list()
    error: Optional[str] = None
