"""
Chat Service
- Handles business logic for conversations and messages
"""
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional

from app.models.support import Conversation, ChatMessage
from app.models.user import User
from app.schemas.chat import ConversationCreate

class ChatService:
    def get_conversation_by_id(self, db: Session, user_id: int, conversation_id: int) -> Optional[Conversation]:
        """
        Logic to fetch a conversation by its ID.
        Ensures the user is a participant in the conversation.
        """
        return db.query(Conversation).options(joinedload(Conversation.messages)).filter(
            Conversation.id == conversation_id,
            (Conversation.user_id == user_id) | (Conversation.admin_id == user_id)
        ).first()

    def get_conversations_for_user(self, db: Session, user_id: int) -> List[Conversation]:
        """
        Logic to fetch all conversations for a specific user.
        Loads the last message for preview purposes.
        """
        return db.query(Conversation).filter(Conversation.user_id == user_id).order_by(Conversation.updated_at.desc()).all()

    def get_all_conversations(self, db: Session, skip: int = 0, limit: int = 100) -> List[Conversation]:
        """
        Logic for admins to fetch all conversations.
        """
        return db.query(Conversation).order_by(Conversation.updated_at.desc()).offset(skip).limit(limit).all()

    def create_conversation(self, db: Session, user: User, initial_data: ConversationCreate) -> Conversation:
        """
        Logic to create a new conversation and add the first message.
        """
        # Create the conversation
        db_conversation = Conversation(
            user_id=user.id,
            status="open"
        )
        db.add(db_conversation)
        db.flush() # Flush to get the conversation ID

        # Create the first message
        first_message = ChatMessage(
            conversation_id=db_conversation.id,
            sender_id=user.id,
            sender_type='user',
            content=initial_data.first_message
        )
        db.add(first_message)
        db.commit()
        db.refresh(db_conversation)
        
        return db_conversation

    def add_message(self, db: Session, conversation: Conversation, sender: User, sender_type: str, content: str) -> ChatMessage:
        """
        Logic to add a new message to an existing conversation.
        This will be primarily used by the WebSocket handler.
        """
        db_message = ChatMessage(
            conversation_id=conversation.id,
            sender_id=sender.id,
            sender_type=sender_type,
            content=content
        )
        db.add(db_message)
        # Update the conversation's updated_at timestamp
        conversation.updated_at = db_message.created_at
        db.add(conversation)
        db.commit()
        db.refresh(db_message)
        return db_message

chat_service = ChatService()
