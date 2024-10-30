# To enable ssh & remote debugging on app service change the base image to the one below
# FROM mcr.microsoft.com/azure-functions/python:4-python3.11-appservice
FROM mcr.microsoft.com/azure-functions/python:4-python3.11

ENV AzureWebJobsScriptRoot=/home/site/wwwroot \
    AzureFunctionsJobHost__Logging__Console__IsEnabled=true \
    AzureWebJobsFeatureFlags=EnableWorkerIndexing \
    AzureWebJobsStorage=UseDevelopmentStorage=true \
    FUNCTIONS_WORKER_RUNTIME=python \
    NOTIFY_API_URL=https://sandbox.api.service.nhs.uk \
    WEBSITES_PORT=8080


COPY requirements.txt /
RUN pip install -r /requirements.txt

COPY . /home/site/wwwroot
