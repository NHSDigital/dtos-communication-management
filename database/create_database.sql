SELECT 'CREATE DATABASE communication_management'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'communication_management')\gexec

\c communication_management

CREATE TABLE IF NOT EXISTS message_statuses (
    batch_id UUID NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    idempotency_key UUID PRIMARY KEY,
    message_id TEXT DEFAULT 'UNKNOWN',
    message_reference UUID NOT NULL,
    nhs_number TEXT NOT NULL,
    payload JSONB,
    recipient_id TEXT NOT NULL,
    state TEXT DEFAULT 'NOT_SENT'
);
