# Local development setup

## Prerequisites

- Python 3.11 preferred
- `pipenv` dependency management for Python see [`pipenv` docs](https://pypi.org/project/pipenv/)
- [asdf tool version manager](https://asdf-vm.com/guide/getting-started.html) and [asdf postgres plugin for PostgreSQL](https://github.com/smashedtoatoms/asdf-postgres) OR install PostgreSQL manually on your machine.
- [Azure Functions Core Tools](https://learn.microsoft.com/en-us/azure/azure-functions/functions-run-local?tabs=macos%2Cisolated-process%2Cnode-v4%2Cpython-v2%2Chttp-trigger%2Ccontainer-apps&pivots=programming-language-python)

## Setup

1. Clone the repository
2. Install dependencies and initialize the virtual environment

    ```bash
    pipenv install --dev
    pipenv shell
    ```

3. Create a `.env.local` file in the root of the project using `.env.example` as a template (ask a team member for the values)
4. Create a PostgreSQL database (ensure that your user has superuser privileges) and set the connection values in the `.env.local` file
5. Run the development start up script to create the database tables and seed the database

    ```bash
    ./dev.sh
    ```

   You should see the Azure function app start in the console.

6. Try the URL `http://localhost:7071/api/healthcheck` in your browser to confirm the function app is running.

## Running the tests

To run the tests locally:

1. Install dependencies and initialize the virtual environment

    ```bash
    pipenv install --dev
    pipenv shell
    ```

2. Run the test script

   ```bash
   ./test.sh
   ```
