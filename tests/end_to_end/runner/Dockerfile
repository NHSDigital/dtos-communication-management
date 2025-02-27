# To enable ssh & remote debugging on app service change the base image to the one below
# FROM mcr.microsoft.com/azure-functions/python:4-python3.11-appservice
FROM mcr.microsoft.com/azure-functions/python:4-python3.11


ENV AZURITE_CONNECTION_STRING=${AZURITE_CONNECTION_STRING} \
    CLIENT_API_KEY=${CLIENT_API_KEY} \
    CLIENT_APPLICATION_ID=${CLIENT_APPLICATION_ID} \
    DATABASE_HOST=db \
    DATABASE_USER=${DATABASE_USER} \
    DATABASE_PASSWORD=${DATABASE_PASSWORD} \
    DATABASE_SSLMODE=${DATABASE_SSLMODE} \
    DATABASE_NAME=${DATABASE_NAME} \
    ENV_FILE=.env.compose


COPY --from=root_dir Pipfile /
COPY --from=root_dir Pipfile.lock /
COPY --from=root_dir /src/notify/ /src/notify/
COPY --from=root_dir /tests/conftest.py /tests/end_to_end/conftest.py
COPY --from=root_dir /alembic/ /alembic/
COPY --from=root_dir /alembic.ini /alembic.ini
COPY --from=root_dir /.env.compose /.env.compose
COPY . /tests/end_to_end

RUN pip install pipenv
RUN pipenv install --dev --system

RUN rm -f /tests/end_to_end/log/functions/*/*.log
