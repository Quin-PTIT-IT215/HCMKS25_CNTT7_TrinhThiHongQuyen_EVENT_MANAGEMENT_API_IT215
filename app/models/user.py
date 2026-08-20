from app.db.database import Base
from sqlalchemy import Column, Integer, String, Enum, Boolean, DateTime
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key= True, index= True, autoincrement= True)
    email = Column(String(255), unique= True, nullable= False)
    password_hash = Column(String(255), nullable= False)
    full_name = Column(String(255), nullable= False)
    role = Column(Enum('User', 'Admin'), default= 'User')
    is_active = Column(Boolean, default= True)
    created_at = Column(DateTime, nullable= False)

    owned_events = relationship('Event', back_populates= 'owner')
    event_staff = relationship('EventStaff', back_populates= 'user')