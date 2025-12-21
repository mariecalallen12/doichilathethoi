"""
WebSocket Endpoints for Chat
"""
import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session

from app.websocket.connection_manager import manager
from app.dependencies import get_db
from app.core.security import verify_access_token
from app.services.user_service import UserService
from app.services.chat_service import chat_service
from app.schemas.chat import ChatMessage

router = APIRouter()

async def get_user_from_token(token: str, db: Session):
    """Helper to get user from a token string."""
    if not token:
        return None
    payload = verify_access_token(token)
    if not payload:
        return None
    user_id = payload.get("sub")
    if not user_id:
        return None
    user = UserService(db, None).get_by_id(int(user_id))
    return user

@router.websocket("/ws/chat/{conversation_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    conversation_id: int,
    db: Session = Depends(get_db)
):
    """
    The main WebSocket endpoint for a chat conversation.
    1. Client connects.
    2. Client sends an auth message: `{"type": "auth", "token": "..."}`
    3. Server verifies token and authorizes user for the conversation.
    4. Client and server can then exchange chat messages.
    """
    user = None
    await manager.connect(websocket, conversation_id)
    try:
        # First message must be authentication
        auth_data = await websocket.receive_json()
        token = auth_data.get("token")
        
        user = await get_user_from_token(token, db)
        if not user:
            await websocket.close(code=1008, reason="Invalid token")
            manager.disconnect(websocket, conversation_id)
            return

        # Check if user is part of the conversation
        conversation = chat_service.get_conversation_by_id(db, user_id=user.id, conversation_id=conversation_id)
        if not conversation:
            # Also check if user is an admin trying to join
            if "admin" not in user.role.name and "owner" not in user.role.name:
                 await websocket.close(code=1008, reason="Not authorized")
                 manager.disconnect(websocket, conversation_id)
                 return
            # If admin, assign them to the conversation if it's unassigned
            unassigned_convo = db.query(Conversation).filter(Conversation.id == conversation_id).first()
            if unassigned_convo and not unassigned_convo.admin_id:
                unassigned_convo.admin_id = user.id
                db.commit()


        # Announce user has joined
        join_msg = {"type": "system", "message": f"User {user.id} has joined the chat."}
        await manager.broadcast_to_room_except(json.dumps(join_msg), conversation_id, websocket)

        # Main message loop
        while True:
            data = await websocket.receive_json()
            content = data.get("content")
            if not content:
                continue

            # Determine sender type
            sender_type = "admin" if "admin" in user.role.name or "owner" in user.role.name else "user"

            # Add message to DB
            db_message = chat_service.add_message(
                db=db,
                conversation=conversation,
                sender=user,
                sender_type=sender_type,
                content=content
            )

            # Create a Pydantic model for response serialization
            message_response = ChatMessage.from_orm(db_message)

            # Broadcast the new message to the room
            await manager.broadcast_to_room(message_response.json(), conversation_id)

    except WebSocketDisconnect:
        manager.disconnect(websocket, conversation_id)
        if user:
            # Announce user has left
            left_msg = {"type": "system", "message": f"User {user.id} has left the chat."}
            await manager.broadcast_to_room(json.dumps(left_msg), conversation_id)
    except Exception as e:
        print(f"WebSocket Error: {e}")
        manager.disconnect(websocket, conversation_id)
        await websocket.close(code=1011, reason="Server error")

