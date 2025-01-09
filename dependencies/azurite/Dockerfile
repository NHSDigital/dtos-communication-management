FROM python:3.12

COPY ./dependencies/azurite .

RUN pip install azure-storage-blob==12.22.0

CMD python3 -u ./azurite-setup.py
