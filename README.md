# Communication Management (National Screening Platform)

This repository makes up the NSP component that handles communication with NHS Notify.

At present, this component is processing a file, and then using the appointment data in that file to create an event, and calling NHS Notify with the payload.
In future, the file processing will be removed, and the event subscription will remain.

Here's a diagram:

```mermaid
graph TD
    A[NBSS Crystal Report] -->|Sent as CSV to | M[NHSMail Mailbox]
    M -->|Uploaded to| N[Azure Blob Storage]
    N -->|Triggers| B[Appointment File Processor]
    B -->|Saves to DB| J[(Message Status)]
    B -->|Calls| D[Communications Management]
    D -->|Calls| E[NHS Notify]
    E -->|NHS App| F[NHS App User]
    E -->|SMS| H[Participant SMS]
    E -->|Letter| I[Participant Letter]
    E -->|Status Callback| K[Verify HMAC Key]
    K -->|Verified| D
    K -->|Invalid HMAC| L[Reject Request]

    D -->|Updates DB| J

    style A fill:#cce5ff,stroke:#0056b3,stroke-width:2px,color:#000;
    style M fill:#e2e3e5,stroke:#6c757d,stroke-width:2px,color:#000;
    style N fill:#d4edda,stroke:#155724,stroke-width:2px,color:#000;
    style B fill:#fff3cd,stroke:#856404,stroke-width:2px,color:#000;
    style D fill:#fff3cd,stroke:#856404,stroke-width:2px,color:#000;
    style E fill:#cce5ff,stroke:#0056b3,stroke-width:2px,color:#000;
    style F fill:#e2e3e5,stroke:#6c757d,stroke-width:2px,color:#000;
    style H fill:#e2e3e5,stroke:#6c757d,stroke-width:2px,color:#000;
    style I fill:#e2e3e5,stroke:#6c757d,stroke-width:2px,color:#000;
    style J fill:#f8d7da,stroke:#721c24,stroke-width:2px,color:#000;
    style K fill:#fefefe,stroke:#0056b3,stroke-width:2px,color:#000;
    style L fill:#f8d7da,stroke:#721c24,stroke-width:2px,color:#000;
```

## Contacts

For any info please contact the [Invite team on Slack](https://nhsdigitalcorporate.enterprise.slack.com/archives/C07QHFSV79U)

## Licence

> The [LICENCE.md](./LICENCE.md) file will need to be updated with the correct year and owner

Unless stated otherwise, the codebase is released under the MIT License. This covers both the codebase and any sample code in the documentation.

Any HTML or Markdown documentation is [© Crown Copyright](https://www.nationalarchives.gov.uk/information-management/re-using-public-sector-information/uk-government-licensing-framework/crown-copyright/) and available under the terms of the [Open Government Licence v3.0](https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/).
