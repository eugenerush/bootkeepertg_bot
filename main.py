import logging
from datetime import datetime
import asyncio
from aiogram import Bot, Dispatcher, Router, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
import app.keyboard as kb
from app.database.models import async_main, Income, async_session, Expense
from app.database import requests as rq

td = datetime.now().strftime('%d %b %y, %H:%M')

router = Router()


@router.message(CommandStart())
@router.callback_query(F.data == 'to_main')
async def cmd_start(message: Message):
    if isinstance(message, Message):
        await rq.set_user(message.from_user.id)
        await message.answer(f'{message.from_user.first_name}, добро пожаловать в бота для учета твоих расходов и '
                             f'доходов!',
                             reply_markup=kb.main)
    else:
        await message.answer('Вы вернулись на главную')
        await message.message.edit_text(f'{message.from_user.first_name}, добро пожаловать в бота для учета твоих '
                                        f'расходов и доходов!',
                                        reply_markup=kb.main)


class IncomeForm(StatesGroup):
    name = State()
    cost = State()
    created_at = State()
    user = State()


class ExpenseForm(StatesGroup):
    name = State()
    cost = State()
    category = State()
    created_at = State()
    user = State()


# IncomeForm
@router.callback_query(F.data == 'new_income')
async def create_income(callback: CallbackQuery, state: FSMContext):
    await state.set_state(IncomeForm.name)
    await callback.message.answer('С чего ты заработал ?')


@router.message(IncomeForm.name)
async def process_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(IncomeForm.cost)
    await message.answer('Сколько ты заработал ?')


@router.message(IncomeForm.cost)
async def process_cost(message: Message, state: FSMContext):
    await state.update_data(cost=message.text)
    await state.update_data(created_at=td)
    await state.update_data(user=message.from_user.id)
    data = await state.get_data()
    income = Income(name=data.get("name"), cost=data.get("cost"), created_at=data.get('created_at'),
                    user=data.get('user'))

    async with async_session() as session:
        session.add(income)
        await session.commit()

    msg = (f'Новый доход: {data.get("name")} - {data.get("cost")} - {data.get("created_at")}\n'
           f'Новая запись успешно создана')
    await message.answer(msg, reply_markup=kb.main)
    await state.clear()


# ExpensesForm
@router.callback_query(F.data == 'new_expense')
async def create_income(callback: CallbackQuery, state: FSMContext):
    await state.set_state(ExpenseForm.category)
    await callback.message.answer('Это личные или рабочие траты ?', reply_markup=ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text='Рабочие'), KeyboardButton(text='Личные')]
    ], resize_keyboard=True))


@router.message(ExpenseForm.category, F.text == "Рабочие")
async def process_work_category(message: Message, state: FSMContext):
    await state.update_data(category='2')
    await state.set_state(ExpenseForm.name)
    await message.answer('На что ты потратил ?', reply_markup=ReplyKeyboardRemove())


@router.message(ExpenseForm.category, F.text == "Личные")
async def process_self_category(message: Message, state: FSMContext):
    await state.update_data(category='1')
    await state.set_state(ExpenseForm.name)
    await message.answer('На что ты потратил ?', reply_markup=ReplyKeyboardRemove())


@router.message(ExpenseForm.category)
async def process_unknown_category(message: Message):
    await message.reply('Я тебя не понял :(', reply_markup=ReplyKeyboardRemove())


@router.message(ExpenseForm.name)
async def process_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(ExpenseForm.cost)
    await message.answer('Сколько ты потратил ?')


@router.message(ExpenseForm.cost)
async def process_cost(message: Message, state: FSMContext):
    await state.update_data(cost=message.text)
    await state.update_data(created_at=td)
    await state.update_data(user=message.from_user.id)
    data = await state.get_data()
    expens = Expense(name=data.get("name"), cost=data.get("cost"), created_at=data.get('created_at'),
                     category=data.get('category'), user=data.get('user'))

    async with async_session() as session:
        session.add(expens)
        await session.commit()

    msg = (f'Новая трата: {data.get("name")} - {data.get("cost")} - {data.get("created_at")}\n'
           f'Новая запись успешно создана')
    await message.answer(msg, reply_markup=kb.main)
    await state.clear()


@router.callback_query(F.data == 'expenses')
async def expenses(callback: CallbackQuery):
    await callback.message.edit_text('Выберите категорию трат', reply_markup=await kb.categories())


@router.callback_query(F.data == 'incomes')
async def expense(callback: CallbackQuery):
    total_sum = await rq.get_income_sum(callback.from_user.id)
    await callback.message.edit_text(f'Сумма доходов {total_sum}', reply_markup=await kb.incomes(callback.from_user.id))


@router.callback_query(F.data.startswith('income_'))
async def incomes(callback: CallbackQuery):
    income_data = await rq.get_income(callback.data.split('_')[1])
    await callback.answer('Вы выбрали доход')
    await callback.message.edit_text(f'Заработал с {income_data.name}\nСколько - {income_data.cost}₽\n'
                                     f'Когда: {income_data.created_at}',
                                     reply_markup=await kb.incomes(callback.from_user.id))


@router.callback_query(F.data.startswith('category_'))
async def category(callback: CallbackQuery):
    await callback.answer('Вы выбрали категорию трат')
    await callback.message.edit_text('Выберите трату',
                                     reply_markup=await kb.expenses(callback.data.split('_')[1], callback.from_user.id))


@router.callback_query(F.data.startswith('expense_'))
async def expens(callback: CallbackQuery):
    expense_data = await rq.get_expense(callback.data.split('_')[1])
    await callback.answer('Вы выбрали трату')
    await callback.message.edit_text(f'Потратил на: {expense_data.name}\nСколько: {expense_data.cost}₽\n'
                                     f'Когда: {expense_data.created_at}')


async def main():
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s - [%(levelname)s] - %(name)s - "
                               "(%(filename)s).%(funcName)s(%(lineno)d) - %(message)s")
    await async_main()
    bot = Bot('TOKEN')
    dp = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Bot is off')
