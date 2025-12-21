"""
Pydantic Schemas for Chat Feature
"""
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class ChatMessageBase(BaseModel):
    content: str

class ChatMessageCreate(ChatMessageBase):
    pass

class ChatMessage(ChatMessageBase):
    id: int
    conversation_id: int
    sender_id: int
    sender_type: str
    created_at: datetime

    class Config:
        from_attributes = True

class ConversationBase(BaseModel):
    user_id: int
    admin_id: Optional[int] = None
    status: str = "open"

class ConversationCreate(BaseModel):
    # When a user starts a chat, they send the first message
    first_message: str

class Conversation(ConversationBase):
    id: int
    created_at: datetime
    updated_at: datetime
    messages: List[ChatMessage] = []

    class Config:
        from_attributes = True
