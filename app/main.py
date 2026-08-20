from fastapi import FastAPI
from app.models.user import User
from app.models.event import Event, EventStaff
from app.models.event_task import EventTask
from app.db.database import Base, engine


app = FastAPI()

Base.metadata.create_all(bind= engine)

@app.get('/')
def test():
    return "Đang kết nối"