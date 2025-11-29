from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user
from app.core.db import get_db
from app.models.category import Category
from app.models.product import Product
from app.models.user import User
from app.schemas.product import ProductCreate, ProductRead, ProductUpdate


router = APIRouter()


@router.post('/', response_model=ProductRead, status_code=status.HTTP_201_CREATED)
def create_product(
    product_in: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Создать новый товар.

    Требует аутентификации.
    """
    # Проверяем, существует ли категория
    category = db.query(Category).filter(Category.id == product_in.category_id).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Категория не найдена",
        )

    db_product = Product(
        name=product_in.name,
        description=product_in.description,
        price=product_in.price,
        quantity=product_in.quantity,
        category_id=product_in.category_id,
    )

    db.add(db_product)
    db.commit()
    db.refresh(db_product)

    return db_product


@router.get('/', response_model=list[ProductRead])
def get_products(
    category_id: int | None = Query(None, description="Фильтр по ID категории"),
    db: Session = Depends(get_db)
):
    """
    Получить список всех товаров.

    Можно фильтровать по категории используя параметр category_id.
    Публичный доступ.
    """
    query = db.query(Product)

    # Если указан category_id, фильтруем по категории
    if category_id is not None:
        query = query.filter(Product.category_id == category_id)

    products = query.all()
    return products


@router.get('/{product_id}', response_model=ProductRead)
def get_product(product_id: int, db: Session = Depends(get_db)):
    """
    Получить товар по ID.

    Публичный доступ.
    """
    product = db.query(Product).filter(Product.id == product_id).first()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Товар не найден',
        )

    return product


@router.put('/{product_id}', response_model=ProductRead)
def update_product(
    product_id: int,
    product_in: ProductUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Обновить товар.

    Требует аутентификации.
    """
    product = db.query(Product).filter(Product.id == product_id).first()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Товар не найден',
        )

    # Обновляем только те поля, которые были переданы
    update_data = product_in.model_dump(exclude_unset=True)

    # Если обновляется category_id, проверяем существование категории
    if 'category_id' in update_data:
        category = db.query(Category).filter(Category.id == update_data['category_id']).first()
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Категория не найдена",
            )

    for field, value in update_data.items():
        setattr(product, field, value)

    db.commit()
    db.refresh(product)

    return product


@router.delete('/{product_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Удалить товар.

    Требует аутентификации.
    """
    product = db.query(Product).filter(Product.id == product_id).first()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Товар не найден',
        )

    db.delete(product)
    db.commit()

    return None
