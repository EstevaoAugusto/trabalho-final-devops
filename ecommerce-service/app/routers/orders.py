from collections import defaultdict
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Order, OrderItem, OrderStatus, Product
from ..schemas import OrderCreate, OrderOut

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("", response_model=OrderOut, status_code=status.HTTP_201_CREATED)
def create_order(payload: OrderCreate, db: Session = Depends(get_db)):
    # Soma quantidades caso o mesmo produto apareça mais de uma vez
    quantities: dict[int, int] = defaultdict(int)
    for item in payload.items:
        quantities[item.product_id] += item.quantity

    order = Order(customer_email=payload.customer_email)
    total = Decimal("0")

    for product_id, quantity in quantities.items():
        product = db.get(Product, product_id)
        if not product:
            raise HTTPException(status.HTTP_404_NOT_FOUND, f"Produto {product_id} não encontrado")
        if product.stock < quantity:
            raise HTTPException(
                status.HTTP_409_CONFLICT,
                f"Estoque insuficiente para '{product.name}' (disponível: {product.stock})",
            )
        product.stock -= quantity
        total += product.price * quantity
        order.items.append(
            OrderItem(product_id=product_id, quantity=quantity, unit_price=product.price)
        )

    order.total = total
    db.add(order)
    db.commit()
    db.refresh(order)
    return order


@router.get("", response_model=list[OrderOut])
def list_orders(
    customer_email: str | None = None,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    stmt = select(Order).order_by(Order.id.desc()).offset(skip).limit(limit)
    if customer_email:
        stmt = stmt.where(Order.customer_email == customer_email)
    return db.scalars(stmt).all()


@router.get("/{order_id}", response_model=OrderOut)
def get_order(order_id: int, db: Session = Depends(get_db)):
    order = db.get(Order, order_id)
    if not order:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Pedido não encontrado")
    return order


@router.post("/{order_id}/cancel", response_model=OrderOut)
def cancel_order(order_id: int, db: Session = Depends(get_db)):
    order = db.get(Order, order_id)
    if not order:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Pedido não encontrado")
    if order.status == OrderStatus.CANCELLED:
        raise HTTPException(status.HTTP_409_CONFLICT, "Pedido já cancelado")

    # Devolve os itens ao estoque
    for item in order.items:
        product = db.get(Product, item.product_id)
        if product:
            product.stock += item.quantity
    order.status = OrderStatus.CANCELLED
    db.commit()
    db.refresh(order)
    return order
