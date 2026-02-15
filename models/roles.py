from sqlalchemy import Column, String, Text, Integer
from sqlalchemy.orm import relationship
from database.engine import Base


class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(50), unique=True, index=True)
    description = Column(Text)

    users = relationship("Users", back_populates="role")
