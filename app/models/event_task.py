from app.db.database import Base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from datetime import datetime, timezone
from sqlalchemy.orm import relationship

class EventTask(Base):
    __tablename__ = 'event_tasks'
    id = Column(Integer, primary_key= True, autoincrement= True, index= True)
    event_id = Column(Integer, ForeignKey('events.id'), nullable= False)
    title = Column(String(255), nullable= False)
    description = Column(String(255), nullable= True)
    assignee_id = Column(Integer, ForeignKey('users.id'), nullable= True)
    status = Column(Enum('Todo', 'In_progress', 'Done'), nullable= False)
    priority = Column(Enum('Low', 'Medium', 'High'), nullable= False)
    due_date = Column(DateTime, nullable= True)
    created_at = Column(DateTime, nullable= False, default= datetime.now(timezone.utc))

    event = relationship('Event', back_populates= 'tasks')
    assignee = relationship('User', back_populates= 'assigned_tasks')