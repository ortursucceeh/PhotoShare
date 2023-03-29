# PhotoShare_Project

#Test test test

Credentials-------------------------------------------------------------------
You have to store your ".env" file on your local machine! Just use your credentials regarding to this pattern.

...\PhotoShare_Project\.env
----------------------
POSTGRES_DB=rest_app
POSTGRES_USER=postgres
POSTGRES_PASSWORD=567234
POSTGRES_PORT=5432

SQLALCHEMY_DATABASE_URL=postgresql+psycopg2://${POSTGRES_USER}:${POSTGRES_PASSWORD}@localhost:${POSTGRES_PORT}/${POSTGRES_DB}

SECRET_KEY=secret_key
ALGORITHM=HS256

MAIL_USERNAME=example@meta.ua
MAIL_PASSWORD=secretPassword
MAIL_FROM=example@meta.ua
MAIL_PORT=465
MAIL_SERVER=smtp.meta.ua

REDIS_HOST=localhost
REDIS=6379
-------------------------------------------------------------------