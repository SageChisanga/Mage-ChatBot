from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import json
import logging
import openai
import os
from datetime import datetime

from backend.app.database import get_db
from backend.app.models.message import Message
from backend.app.utils.security import get_current_user
from backend.app.models.user import User
from backend.app.schemas.auth import TokenData
from jose import jwt
from backend.app.utils.security import SECRET_KEY, ALGORITHM

# Configure logging
logger = logging.getLogger(__name__)

chat_router = APIRouter(tags=["CHAT"], prefix="/chat")

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        try:
            await websocket.accept()
            self.active_connections.append(websocket)
            logger.info(f"New WebSocket connection established. Total connections: {len(self.active_connections)}")
        except Exception as e:
            logger.error(f"Error accepting WebSocket connection: {str(e)}")
            raise

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(f"WebSocket connection closed. Remaining connections: {len(self.active_connections)}")

    async def send_message(self, message: str, websocket: WebSocket):
        try:
            await websocket.send_text(message)
        except Exception as e:
            logger.error(f"Error sending message: {str(e)}")
            raise

manager = ConnectionManager()

def get_ai_response(message: str) -> str:
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant. Provide clear, concise, and accurate responses."},
                {"role": "user", "content": message}
            ],
            temperature=0.7,
            max_tokens=150
        )
        return response.choices[0].message.content
    except openai.error.AuthenticationError:
        logger.error("OpenAI API authentication failed. Please check your API key.")
        return "I'm having trouble authenticating with my AI service. Please check the server configuration."
    except openai.error.RateLimitError:
        logger.error("OpenAI API rate limit exceeded")
        return "I'm receiving too many requests right now. Please try again in a moment."
    except openai.error.APIError as e:
        logger.error(f"OpenAI API error: {str(e)}")
        return "I'm having trouble connecting to my AI service. Please try again later."
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return "I encountered an unexpected error. Please try again later."

async def get_current_user_from_token(token: str, db: Session) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except jwt.JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.email == token_data.email).first()
    if user is None:
        raise credentials_exception
    return user

@chat_router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, db: Session = Depends(get_db)):
    logger.info("New WebSocket connection request received")
    
    # Get token from query parameters
    token = websocket.query_params.get("token")
    if not token:
        logger.error("No token provided in WebSocket connection")
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    try:
        # Authenticate user
        user = await get_current_user_from_token(token, db)
        logger.info(f"Authenticated user: {user.email}")
        
        await manager.connect(websocket)
        logger.info("WebSocket connection established successfully")
        
        while True:
            try:
                data = await websocket.receive_text()
                logger.info(f"Received message from user {user.email}: {data}")
                message_data = json.loads(data)
                
                # Save user message with user_id
                user_message = Message(
                    content=message_data["message"],
                    is_bot=0,
                    user_id=user.id
                )
                db.add(user_message)
                db.commit()
                logger.info("User message saved to database")

                # Get AI response
                bot_response = get_ai_response(message_data["message"])
                logger.info(f"AI response generated: {bot_response}")

                # Save bot response with user_id
                bot_message = Message(
                    content=bot_response,
                    is_bot=1,
                    user_id=user.id
                )
                db.add(bot_message)
                db.commit()
                logger.info("Bot response saved to database")

                # Send response back to client
                await manager.send_message(
                    json.dumps({"message": bot_response, "is_bot": True}),
                    websocket
                )
                logger.info("Response sent to client")

            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON received: {str(e)}")
                await manager.send_message(
                    json.dumps({"message": "Invalid message format", "is_bot": True}),
                    websocket
                )
            except Exception as e:
                logger.error(f"Error processing message: {str(e)}")
                await manager.send_message(
                    json.dumps({"message": "Error processing your message", "is_bot": True}),
                    websocket
                )

    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        try:
            await manager.send_message(
                json.dumps({"message": "An error occurred in the chat server. Please try again later.", "is_bot": True}),
                websocket
            )
        except:
            pass
        manager.disconnect(websocket)

@chat_router.get("/messages", response_model=List[dict])
async def get_messages(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all messages for the current user.
    Requires authentication via Bearer token.
    """
    try:
        # Only get messages for the current user
        messages = db.query(Message).filter(
            Message.user_id == current_user.id
        ).order_by(Message.timestamp).all()
        
        return [
            {
                "id": msg.id,
                "content": msg.content,
                "is_bot": bool(msg.is_bot),
                "timestamp": msg.timestamp.isoformat()
            }
            for msg in messages
        ]
    except Exception as e:
        logger.error(f"Error fetching messages: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching messages from database"
        ) 