from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from models import NotificationType, NotificationStatus


class NotificationResponse(BaseModel):
    id: UUID
    user_id: UUID
    type: NotificationType
    subject: Optional[str]
    body: str
    status: NotificationStatus
    event_type: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
