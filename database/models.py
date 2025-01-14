from sqlalchemy import (
    Column,
    String,
    Text,
    TIMESTAMP,
    JSON,
    Enum,
    UUID,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
import enum

Base = declarative_base()


# Enums
class BatchMessageStatus(enum.Enum):
    NOT_SENT = "not_sent"
    SENT = "sent"
    FAILED = "failed"


class MessageStatus(enum.Enum):
    CREATED = "created"
    PENDING_ENRICHMENT = "pending_enrichment"
    ENRICHED = "enriched"
    SENDING = "sending"
    DELIVERED = "delivered"
    FAILED = "failed"


class ChannelStatus(enum.Enum):
    DELIVERED = "delivered"
    READ = "read"
    NOTIFICATION_ATTEMPTED = "notification_attempted"
    UNNOTIFIED = "unnotified"
    REJECTED = "rejected"
    NOTIFIED = "notified"
    RECEIVED = "received"
    PERMANENT_FAILURE = "permanent_failure"
    TEMPORARY_FAILURE = "temporary_failure"
    TECHNICAL_FAILURE = "technical_failure"


# Tables
class BatchMessage(Base):
    __tablename__ = "batch_messages"

    batch_id = Column(UUID(as_uuid=True), nullable=False, primary_key=True)
    created_at = Column(TIMESTAMP, nullable=False, default="NOW()")
    details = Column(JSON, nullable=True)
    message_reference = Column(UUID(as_uuid=True), nullable=False, primary_key=True)
    nhs_number = Column(Text, nullable=False)
    recipient_id = Column(UUID(as_uuid=True), nullable=False)
    status = Column(Enum(BatchMessageStatus), default=BatchMessageStatus.NOT_SENT, primary_key=True)


class MessageStatusTable(Base):
    __tablename__ = "message_statuses"

    created_at = Column(TIMESTAMP, nullable=False, default="NOW()")
    details = Column(JSON, nullable=True)
    idempotency_key = Column(Text, primary_key=True)
    message_id = Column(String, default="UNKNOWN")
    message_reference = Column(UUID(as_uuid=True), nullable=False)
    status = Column(Enum(MessageStatus), default=MessageStatus.CREATED)


class ChannelStatusTable(Base):
    __tablename__ = "channel_statuses"

    created_at = Column(TIMESTAMP, nullable=False, default="NOW()")
    details = Column(JSON, nullable=True)
    idempotency_key = Column(Text, primary_key=True)
    message_id = Column(String, default="UNKNOWN")
    message_reference = Column(UUID(as_uuid=True), nullable=False)
    status = Column(Enum(ChannelStatus), nullable=True)
