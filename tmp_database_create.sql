CREATE TABLE message_status (
    batch_id UUID NOT NULL,
    recipient_id TEXT NOT NULL,
    current_state TEXT NOT NULL DEFAULT 'NOT_SENT',
    idempotency_key UUID NOT NULL,
    historical_state_data JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (batch_id, recipient_id),
    CONSTRAINT unique_idempotency_key UNIQUE (idempotency_key)
);
