# To enable ssh & remote debugging on app service change the base image to the one below
# FROM mcr.microsoft.com/azure-functions/python:4-python3.11-appservice
FROM mcr.microsoft.com/azure-functions/python:4-python3.11

ENV AzureWebJobsScriptRoot=/home/site/wwwroot \
    AzureFunctionsJobHost__Logging__Console__IsEnabled=true \
    AzureWebJobsFeatureFlags=EnableWorkerIndexing \
    AzureWebJobsStorage=UseDevelopmentStorage=true \
    FUNCTIONS_WORKER_RUNTIME=python \
    BLOB_CONTAINER_NAME=${BLOB_CONTAINER_NAME} \
    NOTIFY_FUNCTION_URL=${NOTIFY_FUNCTION_URL}

COPY --from=root_dir Pipfile /
COPY --from=root_dir Pipfile.lock /
RUN pip install pipenv
RUN pipenv install --system

COPY . /home/site/wwwroot
