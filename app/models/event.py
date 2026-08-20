from app.db.database import Base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship

class Event(Base):
    __tablename__ = 'events'
    id = Column(Integer, primary_key= True, index= True, autoincrement= True)
    name = Column(String(255), nullable= False)
    description = Column(String(255), nullable= True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable= False)
    created_at = Column(DateTime, nullable= False)

    ownwe = relationship('User', back_populates= 'owned_events')
    staff = relationship('EventStaff', back_populates='event')


class EventStaff(Base):
    __tablename__ = 'event_staff'
    event_id = Column(Integer, ForeignKey("events.id"), primary_key= True)
    user_id = Column(Integer, ForeignKey('users.id'), primary_key= True)
    role = Column(Enum('Owner', 'Member'), nullable= False)
    joined_at = Column(DateTime, nullable= False)

    event = relationship('Event', back_populates= 'staff')
    user = relationship('User', back_populates= 'event_staff')
    assigned_tasks = relationship('EventTask', back_populates= 'assignee')