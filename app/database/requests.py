from app.database.models import async_session
from app.database.models import User, Category, Expense, Income
from sqlalchemy import select, func


async def set_user(tg_id):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))

        if not user:
            session.add(User(tg_id=tg_id))
            await session.commit()


async def get_categories():
    async with async_session() as session:
        return await session.scalars(select(Category))


async def get_category_expense(category_id, tg_id):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        return await session.scalars(select(Expense).where(Expense.category == category_id)
                                     .where(Expense.user == user.tg_id))


async def get_expense(expense_id):
    async with async_session() as session:
        return await session.scalar(select(Expense).where(Expense.id == expense_id))


async def get_category_income(tg_id):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        return await session.scalars(select(Income).where(Income.user == user.tg_id))


async def get_income(income_id):
    async with async_session() as session:
        return await session.scalar(select(Income).where(Income.id == income_id))


async def get_income_sum(tg_id):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        return await session.scalar(func.sum(Income.cost).where(Income.user == user.tg_id))
