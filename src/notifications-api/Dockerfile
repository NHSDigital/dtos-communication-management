# To enable ssh & remote debugging on app service change the base image to the one below
# FROM mcr.microsoft.com/azure-functions/python:4-python3.11-appservice
FROM mcr.microsoft.com/azure-functions/python:4-python3.11

ENV AzureWebJobsScriptRoot=/home/site/wwwroot \
    AzureFunctionsJobHost__Logging__Console__IsEnabled=true \
    AzureWebJobsFeatureFlags=EnableWorkerIndexing \
    APPLICATION_ID=${APPLICATION_ID} \
    DATABASE_HOST=${DATABASE_HOST} \
    DATABASE_USER=${DATABASE_USER} \
    DATABASE_PASSWORD=${DATABASE_PASSWORD} \
    DATABASE_NAME=${DATABASE_NAME} \
    FUNCTIONS_WORKER_RUNTIME=python \
    NOTIFY_API_KEY=${NOTIFY_API_KEY} \
    NOTIFY_API_URL=${NOTIFY_API_URL}

COPY --from=root_dir Pipfile /
COPY --from=root_dir Pipfile.lock /
RUN pip install pipenv
RUN pipenv install --system

COPY . /home/site/wwwroot
COPY --from=root_dir ./database/schema.sql /home/site/wwwroot/database/schema.sql
