from dataclasses import dataclass
from sqlalchemy import Engine, text
from functools import lru_cache
from typing import List, Optional
import logging

# TODO: Use sqlalchemy to describe the model
@dataclass
class User:
    id: int = 0
    name: str = ""

@dataclass
class Repository:
    id: int = 0
    name: str = ""


@lru_cache
def get_user(engine: Engine, user_id: int):
    with engine.connect() as con:
        with con.begin():
            con.execute("REQUEST SQL")


def create_repo(engine: Engine, repo_name: str, users: List[str]):
    with engine.connect() as con:
        req = f"""
        -- Step 1: Find the repo ID
        INSERT INTO repositories (repository_name)
        VALUES ('f{repo_name}')
        WHERE NOT EXISTS (SELECT 1 FROM users WHERE user_name = 'f{repo_name}');
        RETURNING repository_id;

        -- Step 2: Delete existing relationships
        DELETE FROM Stargazers_Relationships
        WHERE repository_id = (SELECT repository_id FROM companies WHERE repository_name = '{repo_name}');
        """

        for user in users:
            req += (
                f"""
                -- If user doesn't exist, create it and insert relationship
                INSERT INTO users (user_name)
                VALUES ('f{user}')
                WHERE NOT EXISTS (SELECT 1 FROM users WHERE user_name = 'f{user}')
                RETURNING user_id;

                INSERT INTO Stargazers_Relationships (repositories_id, users_id)
                VALUES ((repository_id, user_id));
                """)

        with con.begin():
            # TODO: user PREPARE to avoid sql injection
            con.execute(text(req))

# @cache_redis
# @lru_cache
# async ?
def get_repo(engine: Engine, owner_name: str, repo_name: str) -> Optional[Repository, List[User]]:
    with engine.connect() as con:
        with con.begin():
            res = con.execute(text(f"""SELECT repo.repository_name, u.user_name FROM repositories repo
                JOIN Stargazers_Relationships cc ON repo.repository_id = cc.repository_id
                JOIN users u ON cc.user_id = u.user_id
                WHERE repo.owner_name = '{owner_name}' AND repo.repository_name = '{repo_name}';"""))

            repo = Repository(name=repo_name)
            users = set((User(name=row[2]) for row in res))
            return repo, users