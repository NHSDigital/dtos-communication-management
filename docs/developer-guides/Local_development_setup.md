# Local development setup

The following instructions will help you set up your local development environment to run the Azure functions locally along with the Azurite Azure Storage Emulator.
This allows you to create and update blob data in emulated storage and trigger the **process-pilot-data** azure function.
This in turn will make a request to the **notify** function which will send a message to the NHS Notify API Sandbox environment.

## Prerequisites

- Python 3.11
- [Azure Functions Core Tools](https://learn.microsoft.com/en-us/azure/azure-functions/create-first-function-cli-python?pivots=python-mode-decorators&tabs=linux%2Cbash%2Cazure-cli%2Cbrowser#install-the-azure-functions-core-tools)
- [Azurite (Azure Storage Emulator)](https://github.com/Azure/Azurite?tab=readme-ov-file#getting-started)
- [Azure Storage Explorer (optional)](https://azure.microsoft.com/en-us/features/storage-explorer/) - to view and manage Azure Storage resources

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
5. Create a container called `blobs` via the Storage Explorer
6. Create or update a blob in the `blobs` container.
The CSV file contents should look like (the NHS numbers are valid example data):

    ```csv
    9990548609,1971-09-07,2024-12-12,10:00,123 High St. London, Mammogram
    9435732992,1980-02-04,2024-12-13,11:00,321 South St. London, Mammogram
    9435792170,1969-01-29,2024-11-24,14:30,45 North St. London, Mammogram
    ```

7. Monitor function console output for logs, you should see the blob update trigger the **process-pilot-data** function and this should then trigger the **notify** function
