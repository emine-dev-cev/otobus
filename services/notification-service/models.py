from sqlalchemy import Column, String, DateTime, Text, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
import uuid
import enum
from datetime import datetime, timezone
from database import Base


class NotificationType(str, enum.Enum):
    email = "email"
    sms = "sms"
    push = "push"


class NotificationStatus(str, enum.Enum):
    sent = "sent"
    failed = "failed"
    pending = "pending"


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    type = Column(SAEnum(NotificationType), nullable=False)
    subject = Column(String, nullable=True)
    body = Column(Text, nullable=False)
    status = Column(SAEnum(NotificationStatus), default=NotificationStatus.pending)
    event_type = Column(String, nullable=True)   # e.g. booking.created
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
