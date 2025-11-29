from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user
from app.core.db import get_db
from app.models.category import Category
from app.models.user import User
from app.schemas.category import CategoryCreate, CategoryRead, CategoryUpdate


router = APIRouter()


@router.post('/', response_model=CategoryRead, status_code=status.HTTP_201_CREATED)
def create_category(
    category_in: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Создать новую категорию.

    Требует аутентификации.
    """
    # Проверяем, не существует ли уже категория с таким именем
    existing_category = db.query(Category).filter(Category.name == category_in.name).first()
    if existing_category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Категория с таким именем уже существует",
        )

    db_category = Category(
        name=category_in.name,
        description=category_in.description,
    )

    db.add(db_category)
    db.commit()
    db.refresh(db_category)

    return db_category


@router.get('/', response_model=list[CategoryRead])
def get_categories(db: Session = Depends(get_db)):
    """
    Получить список всех категорий.

    Публичный доступ.
    """
    categories = db.query(Category).all()
    return categories


@router.get('/{category_id}', response_model=CategoryRead)
def get_category(category_id: int, db: Session = Depends(get_db)):
    """
    Получить категорию по ID.

    Публичный доступ.
    """
    category = db.query(Category).filter(Category.id == category_id).first()

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Категория не найдена',
        )

    return category


@router.put('/{category_id}', response_model=CategoryRead)
def update_category(
    category_id: int,
    category_in: CategoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Обновить категорию.

    Требует аутентификации.
    """
    category = db.query(Category).filter(Category.id == category_id).first()

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Категория не найдена',
        )

    # Обновляем только те поля, которые были переданы
    update_data = category_in.model_dump(exclude_unset=True)

    # Если обновляется name, проверяем уникальность
    if 'name' in update_data:
        existing_category = db.query(Category).filter(
            Category.name == update_data['name'],
            Category.id != category_id
        ).first()
        if existing_category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Категория с таким именем уже существует",
            )

    for field, value in update_data.items():
        setattr(category, field, value)

    db.commit()
    db.refresh(category)

    return category


@router.delete('/{category_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Удалить категорию.

    Требует аутентификации.
    """
    category = db.query(Category).filter(Category.id == category_id).first()

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Категория не найдена',
        )

    db.delete(category)
    db.commit()

    return None
