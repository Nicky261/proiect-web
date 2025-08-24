from sqlalchemy import (
    Column, Integer, String, ForeignKey, Text, DateTime, Boolean, Table
)
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime

Base = declarative_base()

# Tabel many-to-many intre User si Role
user_roles = Table(
    "user_roles", Base.metadata,
    Column("user_id", ForeignKey("users.id"), primary_key=True),
    Column("role_id", ForeignKey("roles.id"), primary_key=True),
)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    roles = relationship("Role", secondary=user_roles, back_populates="users")

class Role(Base):
    __tablename__ = "roles"
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)

    users = relationship("User", secondary=user_roles, back_populates="roles")

class Post(Base):
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True)
    author_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    is_public = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class File(Base):
    __tablename__ = "files"
    id = Column(Integer, primary_key=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    object_name = Column(String(512), nullable=False)
    filename = Column(String(255), nullable=False)
    size = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

class Discussion(Base):
    __tablename__ = "discussions"
    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True)
    discussion_id = Column(Integer, ForeignKey("discussions.id"))
    author_id = Column(Integer, ForeignKey("users.id"))
    body = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class Status(Base):
    __tablename__ = "statuses"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    text = Column(String(280), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
