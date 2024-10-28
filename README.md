# stargazers

to run the service: 

```bash
docker compose -f docker-compose.yml  down -v  
STARGAZERS_GITHUB_TOKEN=${token} STARGAZERS_OWNER=${owner} STARGAZERS_REPO={repo} docker compose -f docker-compose.yml  up --build --force-recreate
```

then in the browser:

http://localhost:5000/v1/stargazers/owner/repo

todo use graph db? (dijkastra)
