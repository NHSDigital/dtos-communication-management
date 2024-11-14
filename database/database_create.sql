CREATE TABLE IF NOT EXISTS message_status (
    batch_id UUID NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    current_state TEXT NOT NULL DEFAULT 'NOT_SENT',
    full_payload_details JSONB,
    idempotency_key UUID NOT NULL,
    message_id TEXT NOT NULL DEFAULT 'UNKNOWN',
    message_reference UUID NOT NULL,
    nhs_number TEXT NOT NULL,
    recipient_id TEXT NOT NULL,
    PRIMARY KEY (batch_id, recipient_id),
    CONSTRAINT unique_idempotency_key UNIQUE (idempotency_key)
);
