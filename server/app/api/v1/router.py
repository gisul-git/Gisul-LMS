from fastapi import APIRouter

from app.api.v1.routes import admin, auth, instructor, student

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth.router)
api_router.include_router(student.router)
api_router.include_router(instructor.router)
api_router.include_router(admin.router)
