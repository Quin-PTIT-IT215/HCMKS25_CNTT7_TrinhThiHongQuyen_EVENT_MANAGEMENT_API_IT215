from fastapi import HTTPException, status

def bad_request(message: str = 'Dữ liệu không hợp lệ'):
    return HTTPException(
        status_code= status.HTTP_400_BAD_REQUEST,
        detail= message
    )

def not_found(message: str = 'Không tìm thấy dữ liệu'):
    return HTTPException(
        status_code= status.HTTP_404_NOT_FOUND,
        detail= message
    )

def forbidden(message: str = 'Bạn không có quyền truy cập'):
    return HTTPException(
        status_code= status.HTTP_403_FORBIDDEN,
        detail= message
    )

