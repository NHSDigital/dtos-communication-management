# Communication Management API

## Overview

This service manages communication delivery via NHS Notify, handling message status updates and delivery tracking across multiple channels. It provides a robust API for recording and retrieving message statuses, with support for various delivery channels and status types.

## Getting Started

### Prerequisites

- Python 3.11 or higher
- PostgreSQL 14 or higher
- Docker (for containerized development)
- pipenv (for dependency management)

### Environment Setup

1. Clone the repository:

   ```bash
   git clone [repository-url]
   cd dtos-communication-management
   ```

2. Install dependencies:

   ```bash
   pip install pipenv
   pipenv install --dev
   pipenv shell
   ```

3. Set up environment variables:

   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

### Required Environment Variables

- `NOTIFY_API_KEY`: API key for the notification service
- `CLIENT_API_KEY`: API key for client authentication
- `DATABASE_URL`: PostgreSQL connection string
- `HMAC_SECRET`: Secret key for HMAC signature generation

## Development

### Running Locally

[Local development docs](docs/developer-guides/Local_development_setup.md)

### Database Migrations

To create a new migration:

```bash
alembic revision --autogenerate -m "description of changes"
```

To apply migrations:

```bash
alembic upgrade head
```

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/unit/notify/app/route_handlers/test_status_create_endpoint.py

# Run with coverage
pytest --cov=src
```

### Test Categories

- Unit Tests: `tests/unit/`
- Integration Tests: `tests/integration/`
- End-to-End Tests: `tests/end_to_end/`

## Architecture

### Components

- **API Layer**: FastAPI-based REST API for status management
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Message Processing**: Asynchronous message handling with status tracking
- **Authentication**: API key and HMAC signature-based security

### Data Flow

1. Status updates are received via the `/api/status/create` endpoint
2. Updates are validated and stored in the database
3. Status queries are handled via the `/api/statuses` endpoint
4. All operations are logged and monitored

## Deployment

### Infrastructure Requirements

- Azure Function App (Linux-based)
- Azure PostgreSQL Flexible Server
- Azure Key Vault for secrets management
- Azure Container Registry for Docker images
- Azure Storage Account for file uploads
- Azure Virtual Network with private endpoints

### Deployment Process

The application is deployed using Azure DevOps pipelines and Terraform infrastructure as code. The deployment process is automated and follows these stages:

1. **Infrastructure Deployment**

   - Core infrastructure is deployed using Terraform
   - Separate pipelines for core and audit infrastructure
   - Environments: Development (DEV), Integration (INT), Pre-production (PRE), and Production (PRD)
   - Pipeline files:
     - Core: `.azuredevops/pipelines/cd-infrastructure-{env}-core.yaml`
     - Audit: `.azuredevops/pipelines/cd-infrastructure-{env}-audit.yaml`

2. **Application Deployment**

   - Docker image is built and pushed to Azure Container Registry
   - Function App is deployed with environment-specific configuration
   - Production and Pre-production environments include a staging slot for zero-downtime deployments
   - Environment-specific variables are managed through Azure Key Vault

3. **Deployment Environments**

   - Development (DEV): `https://int.api.service.nhs.uk`
   - Integration (INT): `https://int.api.service.nhs.uk`
   - Pre-production (PRE): `https://api.service.nhs.uk`
   - Production (PRD): `https://api.service.nhs.uk`

4. **Infrastructure Configuration**
   - App Service Plan: Linux-based P2v3 with auto-scaling
   - PostgreSQL: Flexible Server with private endpoints
   - Storage: Private endpoints for blob and queue storage
   - Network: Virtual Network with private endpoints for all services

## Contributing

### Development Workflow

1. Create a branch from `main`
2. Make your changes
3. Add tests for new functionality
4. Update documentation
5. Submit a pull request

### Code Standards

- Follow PEP 8 style guide
- Write unit tests for new features
- Update documentation for API changes
- Use type hints for all new code
- Follow functional programming principles where possible

### Pull Request Process

1. Ensure all checks pass (tests + linting)
2. Update documentation if needed
3. Get code review approval
4. Merge to main branch

## API Endpoints

### POST /api/message/batch

This endpoint is used to send a batch of messages. It accepts a JSON payload containing message data and validates the request using a bearer token.

#### Request

- **Method:** POST
- **Headers:**
  - Authorization: `Bearer <CLIENT_TOKEN>`
  - Content-Type: application/json
  - X-Consumer-Key: `some-consumer`
- **Body (JSON):**

  ```json
  {
    "data": {
      "type": "MessageBatch",
      "attributes": {
        "routingPlanId": "<routing_plan_id>",
        "messageBatchReference": "<batch_reference>",
        "messages": [
          {
            "messageReference": "<message_reference>",
            "recipient": {
              "nhsNumber": "<nhs_number>",
              "contactDetails": {
                "email": "<email>",
                "sms": "<phone_number>",
                "address": {
                  "lines": [
                    "<address_line_1>",
                    "<address_line_2>",
                    "<address_line_3>",
                    "<city>",
                    "<county>"
                  ],
                  "postcode": "<postcode>"
                }
              }
            },
            "originator": {
              "odsCode": "<ods_code>"
            },
            "personalisation": {}
          }
        ]
      }
    }
  }
  ```

#### Response

- **Success (201):**

  ```json
  {
    "status": "success",
    "response": {
      "data": {
        "type": "MessageBatch",
        "id": "<batch_id>",
        "attributes": {
          "messageBatchReference": "<batch_reference>",
          "routingPlan": {
            "id": "<routing_plan_id>",
            "name": "<plan_name>",
            "version": "<plan_version>",
            "createdDate": "<timestamp>"
          },
          "messages": [
            {
              "messageReference": "<message_reference>",
              "id": "<message_id>"
            }
          ]
        }
      }
    }
  }
  ```

- **Error (401):** Missing or invalid Authorization header

  ```json
  {
    "status": "failed",
    "error": "Authorization header not present"
  }
  ```

- **Error (422):** Invalid request body

  ```json
  {
    "status": "failed",
    "error": "Invalid body: '<error_message>'"
  }
  ```

### POST /api/status/create

This endpoint is used to record status updates for messages. It accepts a JSON payload containing status data and validates the request using API keys and an HMAC signature.

#### Request

- **Method:** POST
- **Headers:**
  - Content-Type: application/json
  - x-api-key: `<NOTIFY_API_KEY>`
  - x-hmac-sha256-signature: `<signature>`
- **Body (JSON):**

  ```json
  {
    "data": [
      {
        "type": "MessageStatus",
        "attributes": {
          "messageId": "<message_id>",
          "messageReference": "<message_reference>",
          "messageStatus": "<status>",
          "channel": "<channel>",
          "channelStatus": "<channel_status>",
          "supplierStatus": "<supplier_status>"
        },
        "meta": {
          "idempotencyKey": "<idempotency_key>"
        }
      }
    ]
  }
  ```

#### Response

- **Success (200):**

  ```json
  {
    "status": "success"
  }
  ```

- **Error (401):** Invalid API key

  ```json
  {
    "status": "Invalid API key"
  }
  ```

- **Error (403):** Invalid signature

  ```json
  {
    "status": "Invalid signature"
  }
  ```

- **Error (422):** Invalid request body

  ```json
  {
    "status": "<error_message>"
  }
  ```

- **Error (500):** Server error

  ```json
  {
    "status": "error"
  }
  ```

### GET /api/statuses

This endpoint retrieves status records based on query parameters. It filters statuses by attributes such as channel, supplier status, batch reference, NHS number, and creation date.

#### Request

- **Method:** GET
- **Headers:**
  - x-api-key: `<CLIENT_API_KEY>`
  - x-consumer-key: 'some-key'
- **Query Parameters (optional):**
  - channel: Filter by channel (e.g., "nhsapp")
  - supplierStatus: Filter by supplier status (e.g., "read")
  - batchReference: Filter by batch reference
  - nhsNumber: Filter by NHS number
  - created_at: Filter by creation date

#### Response

- **Success (200):**

  ```json
  {
    "status": "success",
    "data": [
      {
        "created_at": "<timestamp>",
        "message_id": "<message_id>",
        "message_reference": "<message_reference>",
        "channel": "<channel>",
        "channelStatus": "<channel_status>",
        "supplierStatus": "<supplier_status>"
      }
    ]
  }
  ```

- **Error (401):** Invalid API key

  ```json
  {
    "status": "Invalid API key"
  }
  ```

- **Error (500):** Server error

  ```json
  {
    "status": "error"
  }
  ```

## Contacts

For any info please contact the [Invite team on Slack](https://nhsdigitalcorporate.enterprise.slack.com/archives/C07QHFSV79U)

## Licence

> The [LICENCE.md](./LICENCE.md) file will need to be updated with the correct year and owner

Unless stated otherwise, the codebase is released under the MIT License. This covers both the codebase and any sample code in the documentation.

Any HTML or Markdown documentation is [© Crown Copyright](https://www.nationalarchives.gov.uk/information-management/re-using-public-sector-information/uk-government-licensing-framework/crown-copyright/) and available under the terms of the [Open Government Licence v3.0](https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/).
