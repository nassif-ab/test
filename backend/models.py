from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, func, Boolean
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    is_admin = Column(Boolean, default=False)  # False: usuario normal, True: administrador
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    posts = relationship("Post", back_populates="owner")
    likes = relationship("Like", back_populates="user")

class Post(Base):
    __tablename__ = 'posts'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(255))
    content = Column(Text)
    image = Column(String(255), nullable=True)  # URL o ruta de la imagen
    categorie = Column(String(100), nullable=True)  # Categoría del post
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    owner = relationship("User", back_populates="posts")
    likes = relationship("Like", back_populates="post")
    visits = relationship("Visit", back_populates="post")

class Like(Base):
    __tablename__ = 'likes'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    post_id = Column(Integer, ForeignKey("posts.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="likes")
    post = relationship("Post", back_populates="likes")

class Visit(Base):
    __tablename__ = 'visits'
    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.id"))
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Puede ser null para visitantes anónimos
    ip_address = Column(String(50), nullable=True)  # Para identificar visitantes anónimos
    visit_date = Column(DateTime(timezone=True), server_default=func.now())
    
    post = relationship("Post", back_populates="visits")
    user = relationship("User", backref="visits")  # Relación opcional con el usuario
