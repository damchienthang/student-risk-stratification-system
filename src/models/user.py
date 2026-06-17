# Define SQLModel database schemas for Users, StudentRisk, and InferenceLogs
from typing import ClassVar, Optional
from sqlmodel import Field, SQLModel

class User(SQLModel, table=True):
    __tablename__: ClassVar[str] = "users"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True)
    email: Optional[str] = Field(default=None, unique=True, index=True)
    password_hash: str
    role: str = Field(default="student") # Roles: 'lecturer', 'student'
    is_external: bool = Field(default=False)
    is_active: bool = Field(default=True)
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
