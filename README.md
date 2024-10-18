# Communication Management (National Screening Platform)

This repository makes up the NSP component that handles communication with NHS Notify.

At present, this component is processing a file, and then using the appointment data in that file to create an event, and calling NHS Notify with the payload.
In future, the file processing will be removed, and the event subscription will remain.

Here's a diagram:

```mermaid
graph TD
    A[NBSS Crystal Report] -->|Manual Extraction| B[Appointment File Processor]
    B -->|Raises Event| C[Appointment Allocated Event]
    C --> D[Communications Management]
    D -->|Calls| E[NHS Notify]

    E -->|NHS App| F[NHS App User]
    E -->|Email| G[Participant Email]
    E -->|SMS| H[Participant SMS]
    E -->|Letter| I[Participant Letter]

    style A fill:#f9f,stroke:#333,stroke-width:2px;
    style B fill:#bbf,stroke:#333,stroke-width:2px;
    style C fill:#f99,stroke:#333,stroke-width:2px;
    style D fill:#ff9,stroke:#333,stroke-width:2px;
    style E fill:#9f9,stroke:#333,stroke-width:2px;
    style F fill:#ff0,stroke:#333,stroke-width:2px;
    style G fill:#ff0,stroke:#333,stroke-width:2px;
    style H fill:#ff0,stroke:#333,stroke-width:2px;
    style I fill:#ff0,stroke:#333,stroke-width:2px;
```

## Contacts

For any info please contact the [Invite team on Slack](https://nhsdigitalcorporate.enterprise.slack.com/archives/C07QHFSV79U)

## Licence

> The [LICENCE.md](./LICENCE.md) file will need to be updated with the correct year and owner

Unless stated otherwise, the codebase is released under the MIT License. This covers both the codebase and any sample code in the documentation.

Any HTML or Markdown documentation is [© Crown Copyright](https://www.nationalarchives.gov.uk/information-management/re-using-public-sector-information/uk-government-licensing-framework/crown-copyright/) and available under the terms of the [Open Government Licence v3.0](https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/).
