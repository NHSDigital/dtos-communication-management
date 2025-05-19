# Test Strategy: Comms Manager

## Overview

This document outlines the test strategy and coverage for the Comms Manager service, which forms part of the National Screening Platform (NSP). Comms Manager is responsible for sending participant notifications via NHS Notify and tracking delivery status.

## Test Structure

The test suite is organized into three main categories:

### Unit Tests (`tests/unit/`)

- Function App Tests
  - Health check endpoint validation
  - Blob trigger functionality
  - File upload processing
- Notify App Tests
  - Route handlers
  - File processor
  - Service layer components

### Integration Tests (`tests/integration/`)

- Notify service integration tests
- Message batch processing
- Status update handling

### End-to-End Tests (`tests/end_to_end/`)

- NHS Notify API stub for testing
- End-to-end test runner
- Complete message flow validation

## Test Coverage

### Function App Testing

- Azure Function HTTP triggers
- Blob storage triggers
- Health check endpoints
- File upload processing

### Notify Service Testing

- Message batch validation
- NHS Notify API integration
- Status update processing
- Error handling and retries

## Tools & Frameworks

- `pytest` for test execution
  - `unittest.mock` for mocking
- Azure Functions test utilities
- Custom test data fixtures

## Test Data

- CSV file upload test data
- Message batch test fixtures
- NHS Notify API response mocks

## Entry Criteria

- Code changes are complete
- Test data is available
- Environment is configured

## Exit Criteria

- All automated tests pass
- No critical test failures
- Test coverage meets requirements

## Risk Areas

- File upload processing
- Message batch validation
- NHS Notify API integration
- Status update handling

## Logging & Monitoring

- Test execution logs
- Error tracking
- Performance metrics

## Environments

- **Local:** Development environment
- **CI/CD:** Automated test execution
- **Staging:** Pre-production validation

---

This test strategy reflects the current implementation and structure of the test suite.
