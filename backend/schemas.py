from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

# ====== User ======
class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserOut(UserBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True

# ====== Post ======
class PostBase(BaseModel):
    title: str
    content: Optional[str] = None
    image: Optional[str] = None
    categorie: Optional[str] = None

class PostCreate(PostBase):
    pass

class PostOut(PostBase):
    id: int
    user_id: int
    created_at: datetime
    likes: int = 0  # Número total de likes
    isliked: bool = False  # Si el usuario actual ha dado like
    visits: int = 0  # Contador de visitas

    class Config:
        orm_mode = True

# Este comentario se elimina ya que la clase LikeOut se define más abajo

# ====== Like ======
class LikeBase(BaseModel):
    user_id: int
    post_id: int

class LikeCreate(LikeBase):
    pass

class LikeOut(LikeBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True

# ====== Visit ======
class VisitBase(BaseModel):
    post_id: int
    user_id: Optional[int] = None
    ip_address: Optional[str] = None

class VisitCreate(VisitBase):
    pass

class VisitOut(VisitBase):
    id: int
    visit_date: datetime

    class Config:
        orm_mode = True

# schemas.py (إضافة إلى الملف الحالي)
from pydantic import BaseModel
from typing import Optional

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None