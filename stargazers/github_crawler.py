import logging

import requests
import typing
import re
import itertools

from stargazers.model import User, Repository, session


def get_stargazers(owner: str, repo: str, access_token:str) -> typing.List[str]:
    url = f"https://api.github.com/repos/{owner}/{repo}/stargazers"
    headers = {"Authorization": f"Bearer {access_token}",
               "X-GitHub-Api-Version": "2022-11-28"}

    page = 1
    res = []
    while True and page <= 5:
        response = requests.get(url, headers=headers, params={"page": page})
        response.raise_for_status()

        stargazers = response.json()
        for stargazer in stargazers:
            res.append(stargazer['login'])

        link_header = response.headers.get("Link")
        if not link_header:
            break

        next_page_url = re.search(r'<(.*?)>; rel="next"', link_header)
        if next_page_url is None:
            break
        url = next_page_url.group(1)
        page += 1
    return res

def get_starred_repos(username, access_token):
    url = f"https://api.github.com/users/{username}/starred"
    headers = {"Authorization": f"Bearer {access_token}"}

    page = 1

    res = []
    while True and page < 5:
        response = requests.get(url, headers=headers, params={"page": page})
        response.raise_for_status()

        starred_repos = response.json()
        for repo in starred_repos:
            res.append((repo['full_name'], repo['owner']['login']))

        link_header = response.headers.get("Link")
        if not link_header:
            break

        next_page_url = re.search(r'<(.*?)>; rel="next"', link_header)
        if next_page_url is None:
            break
        url = next_page_url.group(1)
        page += 1

    return res


# totally draft
def fill_db(owner, repo, access_token):
    star_gazers = get_stargazers(owner, repo, access_token)

    user_map = dict()
    repo_map = dict()

    def _get_user_model(user_name):
        model_user = user_map.get(user_name)
        if model_user is None:
            user_map[user_name] = model_user = User(user_name=user_name)
        return model_user

    def _get_repo_model(repo_name):
        model_repo = repo_map.get(repo_name)
        if model_repo is None:
            user_map[repo_name] = model_repo = Repository(name=repo_name)
        return model_repo

    model_current_owner = User.get_or_commit_model_user(owner)
    model_current_repo = Repository(name=repo, owner=model_current_owner)
    user_map[owner] = model_current_owner
    repo_map[repo] = model_current_repo

    # my token has limits :)
    for gazer in star_gazers[:5]:
        model_gazer = _get_user_model(gazer)
        model_current_repo.starred_by.append(model_gazer)

        starred_repos = get_starred_repos(gazer, access_token)
        for _repo, _owner in starred_repos[:10]:

            model_owner = _get_user_model(_owner)
            model_repo = _get_repo_model(_repo)
            model_repo.owner = model_owner

            model_repo.starred_by.append(model_gazer)

    logging.getLogger(__name__).info(f"adding {len(user_map)} users")
    logging.getLogger(__name__).info(f"adding {len(repo_map)} repo")

    session.add_all(itertools.chain((v for _, v in user_map.items()),
                                    (v for _, v in repo_map.items())))
    session.commit()


if __name__ == '__main__':

    owner = "xlqian"
    repo = "navitia"
    access_token = ""

    print(get_stargazers(owner, repo, access_token))
    print(get_starred_repos(owner, access_token))
