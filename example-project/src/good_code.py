"""Example of good Python code with proper patterns."""

from typing import Optional, List
import logging

logger = logging.getLogger(__name__)


class UserService:
    """User service with proper error handling."""
    
    def __init__(self, db_connection):
        """Initialize with database connection.
        
        Args:
            db_connection: Database connection object
        """
        self.db = db_connection
    
    def get_user(self, user_id: int) -> Optional[dict]:
        """Get user by ID.
        
        Args:
            user_id: User identifier
            
        Returns:
            User dict or None if not found
        """
        if user_id <= 0:
            raise ValueError(f"Invalid user_id: {user_id}")
        
        try:
            return self.db.query("SELECT * FROM users WHERE id = ?", (user_id,))
        except Exception as e:
            logger.error(f"Failed to get user: {e}")
            raise
    
    def create_user(self, username: str, email: str) -> dict:
        """Create a new user.
        
        Args:
            username: User's username
            email: User's email
            
        Returns:
            Created user dict
        """
        if not username or not email:
            raise ValueError("Username and email are required")
        
        # Validate email format
        if "@" not in email:
            raise ValueError("Invalid email format")
        
        try:
            user = {
                "username": username,
                "email": email,
                "id": self.db.insert("INSERT INTO users (username, email) VALUES (?, ?)", 
                                   (username, email))
            }
            logger.info(f"Created user: {username}")
            return user
        except Exception as e:
            logger.error(f"Failed to create user: {e}")
            raise
