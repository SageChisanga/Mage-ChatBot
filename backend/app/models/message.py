from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from backend.app.database import Base

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text)
    is_bot = Column(Integer)  # 0 for user, 1 for bot
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    user_id = Column(Integer, ForeignKey("users.id"))
    # Relationship with User model will be defined after both classes

# ... existing code ...
# At the end of the file, after both User and Message are defined:
# from app.models.user import User
# Message.user = relationship("User", back_populates="messages")
 