from sqlalchemy import BigInteger, DECIMAL, String, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine, AsyncSession

engine = create_async_engine(url='sqlite+aiosqlite:///db.sqlite3')

async_session = async_sessionmaker(engine, class_=AsyncSession)


class Base(AsyncAttrs, DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id: Mapped[int] = mapped_column(BigInteger)


class Category(Base):
    __tablename__ = 'categories'

    id: Mapped[int] = mapped_column(primary_key=True)
    name = mapped_column(String(15))


class Income(Base):
    __tablename__ = 'incomes'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    cost: Mapped[int] = mapped_column(DECIMAL(10, 2))
    created_at: Mapped[str] = mapped_column(String(11))
    user: Mapped[int] = mapped_column(ForeignKey('users.tg_id'))


class Expense(Base):
    __tablename__ = 'expenses'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    cost: Mapped[int] = mapped_column(DECIMAL(10, 2))
    created_at: Mapped[str] = mapped_column(String(11))
    category: Mapped[int] = mapped_column(ForeignKey('categories.id'))
    user: Mapped[int] = mapped_column(ForeignKey('users.tg_id'))


async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        print('DB is start')
