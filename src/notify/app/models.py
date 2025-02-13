from sqlalchemy import Column, ForeignKey, func, Integer, String, Text, TIMESTAMP
from sqlalchemy.dialects import postgresql
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.ext.declarative import declarative_base
from dataclasses import dataclass
import enum

Base = declarative_base()


# Enums
class MessageBatchStatuses(enum.Enum):
    FAILED = "failed"
    NOT_SENT = "not_sent"
    SENT = "sent"


class ChannelStatuses(enum.Enum):
    DELIVERED = "delivered"
    NOTIFICATION_ATTEMPTED = "notification_attempted"
    NOTIFIED = "notified"
    PERMANENT_FAILURE = "permanent_failure"
    READ = "read"
    RECEIVED = "received"
    REJECTED = "rejected"
    TECHNICAL_FAILURE = "technical_failure"
    TEMPORARY_FAILURE = "temporary_failure"
    UNNOTIFIED = "unnotified"


class MessageStatuses(enum.Enum):
    CREATED = "created"
    DELIVERED = "delivered"
    ENRICHED = "enriched"
    FAILED = "failed"
    PENDING_ENRICHMENT = "pending_enrichment"
    SENDING = "sending"


# Tables
class MessageBatch(Base):
    __tablename__ = "message_batches"

    id = Column(Integer, primary_key=True)
    batch_id = Column(String, nullable=True)
    batch_reference = Column(UUID(as_uuid=True), nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())
    details = Column(JSONB, nullable=True)
    response = Column(JSONB, nullable=True)
    status = Column(
        postgresql.ENUM(MessageBatchStatuses, values_callable=lambda x: [e.value for e in x]),
        default=MessageBatchStatuses.NOT_SENT,
    )


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True)
    batch_id = Column(Integer, ForeignKey("message_batches.id"), nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())
    details = Column(JSONB, nullable=True)
    message_id = Column(String, nullable=False)
    message_reference = Column(UUID(as_uuid=True), nullable=False)
    nhs_number = Column(Text, nullable=False)
    recipient_id = Column(UUID(as_uuid=True), nullable=False)


@dataclass
class ChannelStatus(Base):
    __tablename__ = "channel_statuses"

    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())
    details = Column(JSONB, nullable=True)
    idempotency_key = Column(Text, primary_key=True)
    message_id = Column(String, nullable=True)
    message_reference = Column(UUID(as_uuid=True), nullable=False)
    status = Column(
        postgresql.ENUM(ChannelStatuses, values_callable=lambda x: [e.value for e in x]),
        nullable=True,
    )


class MessageStatus(Base):
    __tablename__ = "message_statuses"

    created_at = Column(TIMESTAMP, nullable=False, default="NOW()")
    details = Column(JSONB, nullable=True)
    idempotency_key = Column(Text, primary_key=True)
    message_id = Column(String, nullable=True)
    message_reference = Column(UUID(as_uuid=True), nullable=False)
    status = Column(
        postgresql.ENUM(MessageStatuses, values_callable=lambda x: [e.value for e in x]),
        default=MessageStatuses.CREATED,
    )
