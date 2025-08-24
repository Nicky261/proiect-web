# backend/app/admin_routes.py
from typing import List, Optional, Literal
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session
from sqlalchemy import select, func, asc, desc

# NOTE: Adjust these imports to match your project structure.
# Assumptions (common in your repo):
# - get_db: returns SQLAlchemy Session
# - get_current_user: returns current user based on JWT
# - User model has: id, email, full_name, hashed_password, role, is_active, created_at
# - File model has: id, user_id, filename, size_bytes, created_at
try:
    from .database import get_db  # your dependency that yields a Session
except Exception:
    from .deps import get_db  # fallback if you keep deps separate

from .models import User, File  # adjust path if needed
from .auth import get_current_user  # your JWT dependency that returns a User-like object

router = APIRouter(prefix="/admin", tags=["admin"])

# ---- Role & Access control ----
RoleLiteral = Literal["guest", "user", "admin"]  # align with DB Enum/Check constraint

def ensure_admin(current_user: User):
    if getattr(current_user, "role", None) != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admins only.")
    return current_user

# ---- Schemas ----
class UserOut(BaseModel):
    id: int
    email: EmailStr
    full_name: Optional[str] = None
    role: RoleLiteral
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True  # SQLAlchemy -> Pydantic v2

class UserCreate(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    password: str = Field(min_length=6, max_length=128)
    role: RoleLiteral = "user"
    is_active: bool = True

class UserPatch(BaseModel):
    full_name: Optional[str] = None
    role: Optional[RoleLiteral] = None
    is_active: Optional[bool] = None
    password: Optional[str] = Field(default=None, min_length=6, max_length=128)

class UsersPage(BaseModel):
    items: List[UserOut]
    total: int
    page: int
    page_size: int

class FileOut(BaseModel):
    id: int
    user_id: int
    filename: str
    size_bytes: int
    created_at: datetime

    class Config:
        from_attributes = True

class FilesPage(BaseModel):
    items: List[FileOut]
    total: int
    page: int
    page_size: int

# ---- Helpers (hashing, etc.) ----
# If you already have a password utility, import and reuse it.
from passlib.hash import bcrypt

def hash_password(raw: str) -> str:
    return bcrypt.hash(raw)

# ---- Users endpoints ----
@router.get("/users", response_model=UsersPage)
def admin_list_users(
    q: Optional[str] = Query(None, description="Search by email or name"),
    role: Optional[RoleLiteral] = Query(None),
    is_active: Optional[bool] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    order_by: str = Query("created_at", description="created_at|email|full_name|role"),
    order: Literal["asc", "desc"] = "desc",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ensure_admin(current_user)

    stmt = select(User)
    if q:
        like = f"%{q.lower()}%"
        stmt = stmt.where(func.lower(User.email).like(like) | func.lower(User.full_name).like(like))
    if role:
        stmt = stmt.where(User.role == role)
    if is_active is not None:
        stmt = stmt.where(User.is_active == is_active)

    # ordering
    colmap = {
        "created_at": User.created_at,
        "email": User.email,
        "full_name": User.full_name,
        "role": User.role,
    }
    col = colmap.get(order_by, User.created_at)
    stmt = stmt.order_by(asc(col) if order == "asc" else desc(col))

    total = db.execute(select(func.count()).select_from(stmt.subquery())).scalar_one()
    items = db.execute(stmt.offset((page - 1) * page_size).limit(page_size)).scalars().all()

    return UsersPage(items=items, total=total, page=page, page_size=page_size)

@router.post("/users", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def admin_create_user(
    payload: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ensure_admin(current_user)

    # unique email
    existing = db.execute(select(User).where(User.email == payload.email)).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=409, detail="Email already exists")

    u = User(
        email=payload.email,
        full_name=payload.full_name,
        hashed_password=hash_password(payload.password),
        role=payload.role,
        is_active=payload.is_active,
        created_at=datetime.utcnow(),
    )
    db.add(u)
    db.commit()
    db.refresh(u)
    return u

@router.patch("/users/{user_id}", response_model=UserOut)
def admin_update_user(
    user_id: int,
    patch: UserPatch,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ensure_admin(current_user)

    u = db.get(User, user_id)
    if not u:
        raise HTTPException(status_code=404, detail="User not found")

    if patch.full_name is not None:
        u.full_name = patch.full_name
    if patch.role is not None:
        u.role = patch.role
    if patch.is_active is not None:
        u.is_active = patch.is_active
    if patch.password:
        u.hashed_password = hash_password(patch.password)

    db.add(u)
    db.commit()
    db.refresh(u)
    return u

@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def admin_delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ensure_admin(current_user)

    u = db.get(User, user_id)
    if not u:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(u)
    db.commit()
    return

# ---- Roles helper endpoint (optional for frontend dropdowns) ----
@router.get("/roles", response_model=List[RoleLiteral])
def admin_list_roles(
    current_user: User = Depends(get_current_user),
):
    ensure_admin(current_user)
    return ["guest", "user", "admin"]

# ---- Files endpoints ----
@router.get("/files", response_model=FilesPage)
def admin_list_files(
    q: Optional[str] = Query(None, description="Search by filename or user email"),
    user_id: Optional[int] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    order_by: str = Query("created_at", description="created_at|filename|size_bytes"),
    order: Literal["asc", "desc"] = "desc",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ensure_admin(current_user)

    # join to users for search by email
    from sqlalchemy import join
    from sqlalchemy.orm import aliased
    U = aliased(User)
    j = join(File, U, File.user_id == U.id)
    base = select(File).select_from(j)

    if q:
        like = f"%{q.lower()}%"
        base = base.where(func.lower(File.filename).like(like) | func.lower(U.email).like(like))
    if user_id:
        base = base.where(File.user_id == user_id)

    colmap = {
        "created_at": File.created_at,
        "filename": File.filename,
        "size_bytes": File.size_bytes,
    }
    col = colmap.get(order_by, File.created_at)
    base = base.order_by(asc(col) if order == "asc" else desc(col))

    total = db.execute(select(func.count()).select_from(base.subquery())).scalar_one()
    items = db.execute(base.offset((page - 1) * page_size).limit(page_size)).scalars().all()

    return FilesPage(items=items, total=total, page=page, page_size=page_size)

@router.delete("/files/{file_id}", status_code=status.HTTP_204_NO_CONTENT)
def admin_delete_file(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ensure_admin(current_user)

    f = db.get(File, file_id)
    if not f:
        raise HTTPException(status_code=404, detail="File not found")
    db.delete(f)
    db.commit()
    return
