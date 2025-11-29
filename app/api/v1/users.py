from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user
from app.core.db import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserRead
from app.services.auth import get_password_hash


router = APIRouter()


@router.post('/', response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(user_in: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user_in.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким email уже существует",
        )
    
    db_user = User(
        email=user_in.email,    
        hashed_password=get_password_hash(user_in.password),
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


@router.get('/me', response_model=UserRead)
def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """
    Получить информацию о текущем аутентифицированном пользователе.

    Требует токен в заголовке: Authorization: Bearer <token>
    """
    return current_user


@router.get('/{user_id}', response_model=UserRead)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Пользователь не найден',
        )

    return user
