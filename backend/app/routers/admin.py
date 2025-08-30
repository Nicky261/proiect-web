# backend/app/routers/admin.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User, Role, user_roles
from ..auth import get_current_user
from typing import List
from pydantic import BaseModel

router = APIRouter(prefix="/admin", tags=["admin"])

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool
    created_at: str
    roles: List[str] = []

    class Config:
        from_attributes = True

@router.get("/users", response_model=List[UserResponse])
async def list_users(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Lista tuturor utilizatorilor - doar pentru admin"""
    
    # Verifică dacă utilizatorul curent este admin
    user_roles_query = db.query(user_roles).filter(user_roles.c.user_id == current_user.id)
    role_ids = [row.role_id for row in user_roles_query.all()]
    
    if role_ids:
        roles = db.query(Role).filter(Role.id.in_(role_ids)).all()
        user_role_names = [role.name for role in roles]
        
        if 'administrator' not in user_role_names:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Doar administratorii pot accesa această resursă"
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Utilizatorul nu are roluri atribuite"
        )
    
    # Obține toți utilizatorii cu rolurile lor
    users = db.query(User).all()
    users_with_roles = []
    
    for user in users:
        # Obține rolurile utilizatorului
        user_roles_query = db.query(user_roles).filter(user_roles.c.user_id == user.id)
        role_ids = [row.role_id for row in user_roles_query.all()]
        
        if role_ids:
            roles = db.query(Role).filter(Role.id.in_(role_ids)).all()
            role_names = [role.name for role in roles]
        else:
            role_names = ['guest']
        
        users_with_roles.append({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "is_active": user.is_active,
            "created_at": user.created_at.isoformat(),
            "roles": role_names
        })
    
    return users_with_roles

@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Șterge un utilizator - doar pentru admin"""
    
    # Verifică dacă utilizatorul curent este admin (same logic ca mai sus)
    user_roles_query = db.query(user_roles).filter(user_roles.c.user_id == current_user.id)
    role_ids = [row.role_id for row in user_roles_query.all()]
    
    if role_ids:
        roles = db.query(Role).filter(Role.id.in_(role_ids)).all()
        user_role_names = [role.name for role in roles]
        
        if 'administrator' not in user_role_names:
            raise HTTPException(status_code=403, detail="Acces interzis")
    else:
        raise HTTPException(status_code=403, detail="Acces interzis")
    
    # Nu permite ștergerea propriului cont
    if user_id == current_user.id:
        raise HTTPException(
            status_code=400, 
            detail="Nu îți poți șterge propriul cont"
        )
    
    user_to_delete = db.query(User).filter(User.id == user_id).first()
    if not user_to_delete:
        raise HTTPException(status_code=404, detail="Utilizatorul nu există")
    
    # Șterge rolurile utilizatorului mai întâi
    db.execute(user_roles.delete().where(user_roles.c.user_id == user_id))
    
    # Șterge utilizatorul
    db.delete(user_to_delete)
    db.commit()
    
    return {"message": f"Utilizatorul {user_to_delete.username} a fost șters"}

@router.post("/users/{user_id}/toggle-status")
async def toggle_user_status(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Activează/dezactivează un utilizator"""
    
    # Verifică admin permissions (same logic)
    user_roles_query = db.query(user_roles).filter(user_roles.c.user_id == current_user.id)
    role_ids = [row.role_id for row in user_roles_query.all()]
    
    if role_ids:
        roles = db.query(Role).filter(Role.id.in_(role_ids)).all()
        user_role_names = [role.name for role in roles]
        
        if 'administrator' not in user_role_names:
            raise HTTPException(status_code=403, detail="Acces interzis")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilizatorul nu există")
    
    user.is_active = not user.is_active
    db.commit()
    
    return {"message": f"Utilizatorul {user.username} {'activat' if user.is_active else 'dezactivat'}"}