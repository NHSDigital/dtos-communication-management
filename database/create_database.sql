SELECT 'CREATE DATABASE communication_management'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'communication_management')\gexec

\c communication_management

CREATE TYPE message_state AS ENUM ('not_sent', 'created', 'pending_enrichment', 'enriched', 'sending', 'delivered', 'failed');

CREATE TABLE IF NOT EXISTS message_statuses (
    batch_id UUID NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    idempotency_key UUID PRIMARY KEY,
    message_id TEXT DEFAULT 'UNKNOWN',
    message_reference UUID NOT NULL,
    nhs_number TEXT NOT NULL,
    payload JSONB,
    recipient_id TEXT NOT NULL,
    state message_state DEFAULT 'not_sent'
);
