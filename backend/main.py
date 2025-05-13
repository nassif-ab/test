# main.py
from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from routers import users, posts, auth  # إضافة auth

Base.metadata.create_all(bind=engine)

app = FastAPI()

# إعداد CORS
origins = [
    "http://localhost:3000",    # عنوان تطبيق React
    "http://localhost:3030",    # عنوان تطبيق React
    "http://localhost:4040",    # عنوان تطبيق React
    "http://localhost:5173",    # عنوان Vite
    "http://127.0.0.1:5173",    # عنوان Vite البديل
    "http://localhost:8000",    # عنوان آخر محتمل
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# إنشاء Router رئيسي بالـ prefix "/api"
api_router = APIRouter(prefix="/api")

# إضافة الـ routers إلى الـ api_router
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])  # إضافة router المصادقة
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(posts.router, prefix="/posts", tags=["Posts"])

# إضافة api_router إلى التطبيق الرئيسي
app.include_router(api_router)