from aiogram import types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from app.database.requests import get_categories, get_category_expense, get_category_income


main = InlineKeyboardMarkup(inline_keyboard=[
    [types.InlineKeyboardButton(text="Траты", callback_data='expenses')],
    [types.InlineKeyboardButton(text="Доходы", callback_data='incomes')],
    [types.InlineKeyboardButton(text="Новая трата", callback_data='new_expense')],
    [types.InlineKeyboardButton(text="Новый доход", callback_data='new_income')],
])


to_main = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='На главную', callback_data='to_main')]
])


async def categories():
    all_categories = await get_categories()
    keyboard = InlineKeyboardBuilder()
    for category in all_categories:
        keyboard.add(InlineKeyboardButton(text=category.name, callback_data=f'category_{category.id}'))
    keyboard.add(InlineKeyboardButton(text='Назад', callback_data='to_main'))
    return keyboard.adjust(2).as_markup()


async def expenses(category_id, user_id):
    all_expenses = await get_category_expense(category_id, user_id)
    keyboard = InlineKeyboardBuilder()
    for expense in all_expenses:
        keyboard.add(InlineKeyboardButton(text=expense.name + ' ' + str(expense.created_at),
                                          callback_data=f'expense_{expense.id}'))
    keyboard.add(InlineKeyboardButton(text='Назад', callback_data='to_main'))
    return keyboard.adjust(2).as_markup()


async def incomes(user_id):
    all_incomes = await get_category_income(user_id)
    keyboard = InlineKeyboardBuilder()
    for income in all_incomes:
        keyboard.add(InlineKeyboardButton(text=income.name + ' ' + str(income.created_at),
                                          callback_data=f'income_{income.id}'))
    keyboard.add(InlineKeyboardButton(text='Назад', callback_data='to_main'))
    return keyboard.adjust(2).as_markup()
