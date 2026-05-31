import uuid
from sqlalchemy import select, desc

from app.models.order import Order
from app.database import async_session


class OrderDAO:

    async def create_order(self, order: Order) -> Order:
        async with async_session() as db:
            db.add(order)
            await db.commit()
            await db.refresh(order)
            return order

    async def get_by_id(self, order_id: uuid.UUID) -> Order | None:
        async with async_session() as db:
            result = await db.execute(select(Order).where(Order.id == order_id))
            return result.scalar_one_or_none()

    async def get_by_order_no(self, order_no: str) -> Order | None:
        async with async_session() as db:
            result = await db.execute(select(Order).where(Order.order_no == order_no))
            return result.scalar_one_or_none()

    async def update_order(self, order: Order) -> Order:
        async with async_session() as db:
            db.add(order)
            await db.commit()
            await db.refresh(order)
            return order

    async def list_by_user(self, user_id: uuid.UUID, limit: int = 20) -> list[Order]:
        async with async_session() as db:
            result = await db.execute(
                select(Order)
                .where(Order.user_id == user_id)
                .order_by(desc(Order.created_at))
                .limit(limit)
            )
            return list(result.scalars().all())
