import os
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from minio import Minio
from minio.error import S3Error

from .db import get_db, engine
from .models import Base, User, Role, Post, File as FileModel, Discussion, Message, Status
from .schemas import (
    UserCreate, UserOut, Token, PostCreate, PostOut,
    DiscussionCreate, MessageCreate, StatusCreate
)
from .auth import get_password_hash, verify_password, create_access_token, get_current_user
from .deps import is_admin

# === App init ===
app = FastAPI(title="Hub Studenti API")
app.include_router(admin_router)

# CORS (pentru frontend dev)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Creare tabele
Base.metadata.create_all(bind=engine)

# Seed roluri default
from sqlalchemy import select
with next(get_db()) as db:
    for name in ["guest", "user", "admin"]:
        if not db.query(Role).filter(Role.name == name).first():
            db.add(Role(name=name))
    db.commit()

# MinIO client setup
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "minio:9000")
MINIO_ROOT_USER = os.getenv("MINIO_ROOT_USER", "minioadmin")
MINIO_ROOT_PASSWORD = os.getenv("MINIO_ROOT_PASSWORD", "minioadmin")
MINIO_BUCKET = os.getenv("MINIO_BUCKET", "materials")
MINIO_SECURE = os.getenv("MINIO_SECURE", "false").lower() == "true"

minio_client = Minio(
    MINIO_ENDPOINT,
    access_key=MINIO_ROOT_USER,
    secret_key=MINIO_ROOT_PASSWORD,
    secure=MINIO_SECURE,
)
try:
    if not minio_client.bucket_exists(MINIO_BUCKET):
        minio_client.make_bucket(MINIO_BUCKET)
except S3Error:
    pass

# === Health check ===
@app.get("/health")
def health():
    return {"status": "ok"}

# === Auth ===
@app.post("/auth/register", response_model=UserOut)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter((User.username == payload.username) | (User.email == payload.email)).first():
        raise HTTPException(status_code=400, detail="User already exists")
    user = User(email=payload.email, username=payload.username, password_hash=get_password_hash(payload.password))
    role_user = db.query(Role).filter(Role.name == "user").first()
    user.roles.append(role_user)
    db.add(user)
    db.commit()
    db.refresh(user)
    return UserOut(id=user.id, email=user.email, username=user.username, roles=[r.name for r in user.roles])

@app.post("/auth/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token({"sub": user.username})
    return Token(access_token=token)

@app.get("/users/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)):
    return UserOut(id=user.id, email=user.email, username=user.username, roles=[r.name for r in user.roles])

# === Admin: role assignment ===
@app.post("/admin/users/{user_id}/roles/{role}")
def assign_role(user_id: int, role: str, db: Session = Depends(get_db), _=Depends(is_admin)):
    u = db.query(User).get(user_id)
    r = db.query(Role).filter(Role.name == role).first()
    if not u or not r:
        raise HTTPException(status_code=404, detail="User or role not found")
    if r not in u.roles:
        u.roles.append(r)
        db.commit()
    return {"ok": True}

# === Blog posts ===
@app.post("/posts", response_model=PostOut)
def create_post(payload: PostCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    p = Post(author_id=user.id, title=payload.title, content=payload.content, is_public=payload.is_public)
    db.add(p)
    db.commit()
    db.refresh(p)
    return p

@app.get("/posts", response_model=list[PostOut])
def list_posts(db: Session = Depends(get_db)):
    return db.query(Post).filter(Post.is_public == True).order_by(Post.created_at.desc()).all()

# === Files (Drive) ===
@app.post("/files/upload")
def upload_file(f: UploadFile = File(...), db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    object_name = f"u{user.id}/" + f.filename
    data = f.file
    size = 0
    data.seek(0, 2)
    size = data.tell()
    data.seek(0)
    minio_client.put_object(MINIO_BUCKET, object_name, data, size, content_type=f.content_type)
    rec = FileModel(owner_id=user.id, object_name=object_name, filename=f.filename, size=size)
    db.add(rec)
    db.commit()
    return {"ok": True, "object": object_name}

@app.get("/files")
def list_files(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.query(FileModel).filter(FileModel.owner_id == user.id).all()

# === Discussions ===
@app.post("/discussions")
def create_discussion(payload: DiscussionCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    d = Discussion(title=payload.title, created_by=user.id)
    db.add(d)
    db.commit()
    db.refresh(d)
    return d

@app.post("/messages")
def post_message(payload: MessageCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    m = Message(discussion_id=payload.discussion_id, author_id=user.id, body=payload.body)
    db.add(m)
    db.commit()
    db.refresh(m)
    return m

# === Status ===
@app.post("/status")
def set_status(payload: StatusCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    s = Status(user_id=user.id, text=payload.text)
    db.add(s)
    db.commit()
    db.refresh(s)
    return s
