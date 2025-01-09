# Local development setup

This project uses Azure Functions to process data and send messages to the NHS Notify API Sandbox environment.
Docker containers can be used to run the Azure functions in a local development environment.
Docker compose is used to run the Azure functions and Azurite Azure Storage Emulator.
Alternatively, you can run the Azure functions locally using Azure Functions Core Tools.

## Prerequisites

- Python 3.11
- Docker
- Docker Compose (included with Docker Desktop)
- Azure Functions Core Tools (Optional, see below)

## Using Docker Compose to run Azure Functions and Azurite

This is the preferred method for running the Azure functions locally.

### Prepare environment variables

Copy `.env.example` to `.env.local` in the root of the project and populate with valid values. You may need to ask another developer for these values.

### Start Azurite and Azure functions

To start the Azure functions and Azurite, run the following command:

```bash
docker compose --env-file .env.local up
```

### Testing a file upload

There is a convenience script to upload a test file to the Azurite storage emulator. This script will upload a test file to the `pilot-data` container in the Azurite storage emulator.

```bash
pip install azure-storage-blob python-dotenv
python dependencies/azurite/send_file.py dependencies/azurite/example.csv
```

You should see the Azure functions being triggered in the console output and success messages from the functions.

## Manual setup using Azure Functions Core Tools to run functions outside of Docker

It's also possible to run one or more functions locally without using Docker. This can be useful for debugging or testing individual functions.

### Setup Python virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
```

### Install dependencies for a specific Azure function

Azure function code is located in `src/functions/<function_name>`. To install dependencies for a specific function, run the following command:

```bash
cd src/functions/<function_name>
pip install -r requirements.txt
```

### Start the Azure function locally

To start an Azure function locally, run the following command:

```bash
func start --verbose -p <port>
```

### Running end-to-end tests

To run an end-to-end test, you will need to run both functions locally. Functions default to port 7071, the local settings in this project use ports 7071 and 7072 respectively. You can change the port by using the `-p` flag.

1. Start Azurite
2. Start the **process-pilot-data** function with the default port (omit the -p flag)
3. Start the **notify** function on port 7072 (use the `-p 7072` flag)
4. Start Storage Explorer and connect to the Azurite Emulator
5. Create a container called `pilot-data` via the Storage Explorer
6. Create or update a blob in the `pilot-data` container.
The CSV file contents should look like (the NHS numbers are valid example data):

    ```csv
    9990548609,1971-09-07,2024-12-12,10:00,123 High St. London, Mammogram
    9435732992,1980-02-04,2024-12-13,11:00,321 South St. London, Mammogram
    9435792170,1969-01-29,2024-11-24,14:30,45 North St. London, Mammogram
    ```

7. Monitor function console output for logs, you should see the blob update trigger the **process-pilot-data** function and this should then trigger the **notify** function
