import sys
sys.path.append("..")

from sqlalchemy import Boolean, Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from db.database import Base

class User(Base):
	__tablename__ = "users"

	id = Column(Integer, primary_key=True, index=True)
	email = Column(String, unique=True, index=True)
	username = Column(String, unique=True, index=True)
	hashed_password = Column(String)
	is_active = Column(Boolean, default=False)
	is_admin = Column(Boolean, default=False)

	my_items = relationship("TaskRecord", back_populates="owner")

class Item(Base):
	__tablename__ = "items"

	id = Column(Integer, primary_key=True, index=True)
	name = Column(String)
	date_created = Column(String)
	is_deleted = Column(Boolean, default=False)

	#foreign key
	owner_id = Column(Integer, ForeignKey("users.id"))
	owner = relationship("User", back_populates="my_items")