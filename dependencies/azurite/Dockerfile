FROM python:3.12

ENV AZURITE_CONNECTION_STRING=${AZURITE_CONNECTION_STRING} \
    BLOB_CONTAINER_NAME=${BLOB_CONTAINER_NAME}

COPY ./dependencies/azurite .

RUN pip install azure-storage-blob==12.22.0

CMD python3 -u ./azurite-setup.py
