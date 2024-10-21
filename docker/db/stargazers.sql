-- First version ...

CREATE TABLE Users (
    user_id SERIAL PRIMARY KEY,
    user_name VARCHAR(100) NOT NULL UNIQUE -- CHECK (user_name REGEXP '^[A-Za-z0-9]+$')
);

CREATE TABLE Repositories (
    repository_id SERIAL PRIMARY KEY,
    repository_name TEXT NOT NULL, -- (user_name REGEXP '^[A-Za-z0-9]+$'),
    owner_id SERIAL,
    FOREIGN KEY (owner_id) REFERENCES Users(user_id),
    UNIQUE (owner_id, repository_name)
);


CREATE TABLE Stargazers_Relationships (
    repository_id SERIAL,
    user_id SERIAL,
    FOREIGN KEY (repository_id) REFERENCES Repositories(repository_id),
    FOREIGN KEY (user_id) REFERENCES Users(user_id)
);

-- speed up the search
CREATE INDEX idx_repository_name ON Repositories (repository_name);
CREATE INDEX idx_user_name ON Users (user_name);
CREATE INDEX idx_repository_user ON Stargazers_Relationships (repository_id, user_id);


INSERT INTO Users (user_name) VALUES
    ('User_A'),
    ('User_B'),
    ('User_C');

INSERT INTO Repositories (repository_name) VALUES
    ('Repo_A'),
    ('Repo_B'),
    ('Repo_C');


INSERT INTO Stargazers_Relationships (repository_id, user_id) VALUES
    (1, 1),
    (1, 2),
    (2, 2),
    (2, 3),
    (3, 3);
