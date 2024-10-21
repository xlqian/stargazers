import logging
import os
import collections

from sqlalchemy import Column, Integer, String, ForeignKey, Table, Index, select
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine


def make_engine():
    db_connection_string = os.environ.get('DB_CONNECTION_STRING') or "postgresql://stargazers:password@db/stargazers"
    return create_engine(db_connection_string)


engine = make_engine()

def make_session(engine):
    Session = sessionmaker(bind=engine)
    return Session()


session = make_session(engine)


Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    user_name = Column(String(50), unique=True, nullable=False)

    # Relationship: User owns many repositories
    owned_repositories = relationship("Repository", back_populates="owner")

    # Relationship: User can star many repositories
    starred_repositories = relationship("Repository", secondary="user_starred_repositories", back_populates="starred_by")

    @classmethod
    def get_model_user(cls, user_name):
        return session.query(User).filter(User.user_name == user_name).first()

    @classmethod
    def get_or_commit_model_user(cls, user_name):
        user = session.query(User).filter(User.user_name == user_name).first()
        if user:
            return user
        user = User(user_name=user_name)
        session.add(user)
        session.commit()
        return user

class Repository(Base):
    __tablename__ = 'repositories'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)

    # Relationship: Repository is owned by one user
    owner_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    owner = relationship("User", back_populates="owned_repositories")

    # Relationship: Repository can be starred by many users
    starred_by = relationship("User", secondary="user_starred_repositories", back_populates="starred_repositories")

    @classmethod
    def get_model_repository(cls, repo_name):
        return session.query(Repository).filter(Repository.name == repo_name).first()

    @classmethod
    def get_or_commit_model_repository(cls, repo_name):
        repo = session.query(Repository).filter(Repository.name == repo_name).first()
        if repo:
            return repo
        repo = Repository(name=repo_name)
        session.add(repo)
        session.commit()
        return repo

# Association table for the many-to-many relationship between User and Repository (for starring)
user_stared_repositories = Table('user_starred_repositories', Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('repository_id', Integer, ForeignKey('repositories.id'))
)

def create_db():
    Base.metadata.create_all(engine)

    # TODO : add index
    Index('repo_name_idx', Repository.name)
    # ...

    session.commit()


def create_sample_db():
    user1 = User(user_name='user1')
    user2 = User(user_name='user2')
    user3 = User(user_name='user3')
    user4 = User(user_name='user4')

    repo1 = Repository(name='repo1', owner=user1)
    repo2 = Repository(name='repo2', owner=user2)
    repo3 = Repository(name='repo3', owner=user3)
    repo4 = Repository(name='repo4', owner=user1)

    Base.metadata.create_all(engine)

    # TODO : add index
    Index('repo_name_idx', Repository.name)
    # ...

    repo1.starred_by.extend([user1, user2])
    repo2.starred_by.extend([user2, user3])

    session.add_all([user1, user2, user3, user4, repo1, repo2, repo3, repo4])
    session.commit()


def get_shared_stargazsers_repositories(user: str, repository: str, start_page: int, count: int) -> dict:
    repo = session.query(Repository).join(User, Repository.owner_id == User.id).filter(
        User.user_name == f'{user}',
        Repository.name == f'{repository}'
    ).first()

    if repo is None:
        raise Exception(f"No such repo is found for user: {user}, repo: {repository}")

    stargazers_ids = set((user.id for user in repo.starred_by))

    logging.getLogger(__name__).debug("stargazers_ids: ", stargazers_ids)

    # TODO: make the subquery function
    # starred_users = session.query(user_stared_repositories.c.user_id)\
    #    .filter(user_stared_repositories.c.repository_id == repo.id)\
    #    .subquery()

    # Find all other repositories starred by these users
    shared_repos = session.query(
        Repository.id,
        Repository.name,
        User.user_name
    ).join(user_stared_repositories, Repository.id == user_stared_repositories.c.repository_id)\
     .join(User, User.id == user_stared_repositories.c.user_id)\
     .filter(Repository.id != repo.id)\
     .filter(user_stared_repositories.c.user_id.in_(stargazers_ids))\
     .all()

    result = collections.defaultdict(list)
    for repo_id, repo_name, user_name in shared_repos:
        logging.error(str(repo_id) + str(repo_name) + str(user_name))
        # TODO: use user_id instead of user_name to save network, then use a redis cache to retrieve user name
        result[repo_name].append(user_name)
    logging.error(result)
    return result
