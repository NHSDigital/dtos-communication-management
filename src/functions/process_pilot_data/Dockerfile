# To enable ssh & remote debugging on app service change the base image to the one below
# FROM mcr.microsoft.com/azure-functions/python:4-python3.11-appservice
FROM mcr.microsoft.com/azure-functions/python:4-python3.11

ENV AzureWebJobsScriptRoot=/home/site/wwwroot \
    AzureFunctionsJobHost__Logging__Console__IsEnabled=true \
    AzureWebJobsFeatureFlags=EnableWorkerIndexing \
    AzureWebJobsStorage=UseDevelopmentStorage=true \
    FUNCTIONS_WORKER_RUNTIME=python \
    BLOB_CONTAINER_NAME=blobs \
    NOTIFY_FUNCTION_URL=http://localhost:7072/api/notify/message/send

COPY requirements.txt /
RUN pip install -r /requirements.txt

COPY . /home/site/wwwroot
