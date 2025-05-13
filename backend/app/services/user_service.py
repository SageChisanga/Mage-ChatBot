from sqlalchemy.orm import Session
from typing import Optional
from backend.app.models.user import User

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """
    Retrieve a user by their email address.
    
    Args:
        db (Session): Database session
        email (str): User's email address
        
    Returns:
        Optional[User]: User object if found, None otherwise
    """
    return db.query(User).filter(User.email == email).first() 