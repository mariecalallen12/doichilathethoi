"""
API Endpoints for Chat
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app import dependencies
from app.services.chat_service import chat_service
from app.schemas.chat import Conversation, ConversationCreate
from app.models.user import User

router = APIRouter()

@router.get("/admin/conversations", response_model=List[Conversation], tags=["Chat (Admin)"])
def get_all_conversations(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(dependencies.get_db),
    current_user: User = Depends(dependencies.require_role(["admin", "owner"])),
):
    """
    Retrieve all conversations (Admin only)
    """
    conversations = chat_service.get_all_conversations(db, skip=skip, limit=limit)
    return conversations

@router.post("/conversations", response_model=Conversation, tags=["Chat (User)"])
def create_new_conversation(
    *,
    db: Session = Depends(dependencies.get_db),
    conversation_in: ConversationCreate,
    current_user: User = Depends(dependencies.get_current_active_user),
):
    """
    Create a new conversation. A user can only create a conversation for themselves.
    """
    conversation = chat_service.create_conversation(db=db, user=current_user, initial_data=conversation_in)
    return conversation

@router.get("/conversations", response_model=List[Conversation], tags=["Chat (User)"])
def get_my_conversations(
    db: Session = Depends(dependencies.get_db),
    current_user: User = Depends(dependencies.get_current_active_user),
):
    """
    Get all conversations for the current user.
    """
    return chat_service.get_conversations_for_user(db=db, user_id=current_user.id)

@router.get("/conversations/{conversation_id}", response_model=Conversation, tags=["Chat (User)", "Chat (Admin)"])
def get_conversation_details(
    conversation_id: int,
    db: Session = Depends(dependencies.get_db),
    current_user: User = Depends(dependencies.get_current_user),
):
    """
    Get details of a specific conversation.
    A user can only access conversations they are part of. Admins can access any.
    """
    user_id_to_check = current_user.id
    # If the user is an admin, they can see any conversation, so we don't filter by user.
    # However, the service layer function `get_conversation_by_id` expects a user_id.
    # For this check, we can pass the admin's own ID, and the logic inside the service will handle it.
    
    conversation = chat_service.get_conversation_by_id(db=db, user_id=user_id_to_check, conversation_id=conversation_id)

    if not conversation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
        
    # Final check to ensure non-admins don't see other people's chats
    if "admin" not in current_user.role.name and "owner" not in current_user.role.name:
        if conversation.user_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access this conversation")

    return conversation
