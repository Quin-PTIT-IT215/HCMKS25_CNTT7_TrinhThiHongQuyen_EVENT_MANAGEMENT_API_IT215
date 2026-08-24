from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from app.models.user import User
from app.models.event import Event, EventStaff
from app.models.event_task import EventTask
from app.routers import auth, users, event
from app.db.database import Base, engine
from app.schemas.response import APIResponse
from datetime import datetime, timezone


app = FastAPI()
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(event.router)
Base.metadata.create_all(bind= engine)

# chuẩn hóa response lỗi, trong api nào có raise HTTPException() thì hàm này để xử lý lỗi trước khi trả response cho người dùng
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    response = APIResponse(
        statusCode= exc.status_code,
        data= None,
        message= str(exc.detail),
        timestamp= datetime.now(timezone.utc),
        path= request.url.path,
        error= exc.detail
    )

    return JSONResponse(
        status_code= exc.status_code,
        content= response.model_dump(mode= 'json')
    )


# nếu người dùng gửi lên không đúng với bên pydantic schema thì lỗi này sẽ xảy ra, xử lý response trả về cho người dùng theo format thống nhất
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    response = APIResponse(
        statusCode= 422,
        data= None,
        message= 'Dữ liệu đầu vào không hợp lệ',
        timestamp= datetime.now(timezone.utc),
        path= request.url.path,
        error= exc.errors()
    )

    return JSONResponse(
        status_code= 422,
        content= response.model_dump(mode= 'json')
    )


@app.get('/health')
def health_check():
    return APIResponse(
        statusCode= 200,
        data= {'status': 'ok'},
        message= 'API đang hoạt động',
        timestamp= datetime.now(timezone.utc),
        path= '/health',
        error= None
    )

