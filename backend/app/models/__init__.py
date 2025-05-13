from sqlalchemy.orm import relationship
from backend.app.models.user import User
from backend.app.models.message import Message

User.messages = relationship("Message", back_populates="user")
Message.user = relationship("User", back_populates="messages")