# To enable ssh & remote debugging on app service change the base image to the one below
# FROM mcr.microsoft.com/azure-functions/python:4-python3.11-appservice
FROM mcr.microsoft.com/azure-functions/python:4-python3.11

ENV DATABASE_HOST=${DATABASE_HOST} \
    DATABASE_USER=${DATABASE_USER} \
    DATABASE_PASSWORD=${DATABASE_PASSWORD} \
    DATABASE_NAME=${DATABASE_NAME}


COPY --from=root_dir Pipfile /
COPY --from=root_dir Pipfile.lock /
RUN pip install pipenv
RUN pipenv install --system
RUN pipenv install --dev --system

COPY --from=shared_dir . /src/shared
COPY . /tests/integration
