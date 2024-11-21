SELECT 'CREATE DATABASE communication_management'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'communication_management')\gexec

\c communication_management

CREATE TYPE batch_message_status AS ENUM ('not_sent', 'sent', 'failed');
CREATE TYPE message_status AS ENUM ('created', 'pending_enrichment', 'enriched', 'sending', 'delivered', 'failed');

CREATE TABLE IF NOT EXISTS batch_messages (
    batch_id UUID NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    details JSONB,
    message_reference UUID NOT NULL,
    nhs_number TEXT NOT NULL,
    recipient_id TEXT NOT NULL,
    status batch_message_status DEFAULT 'not_sent',
    PRIMARY KEY (batch_id, message_reference)
);

CREATE TABLE IF NOT EXISTS message_statuses (
    created_at TIMESTAMP DEFAULT NOW(),
    details JSONB,
    idempotency_key UUID PRIMARY KEY,
    message_id TEXT DEFAULT 'UNKNOWN',
    message_reference UUID NOT NULL,
    status message_status DEFAULT 'created'
);
