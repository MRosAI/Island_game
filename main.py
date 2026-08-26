
import asyncio
import os

from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from dotenv import load_dotenv

from database import (
    init_db,
    get_player,
    create_player,
    update_player_name,
    update_player_gender
)

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не найден в .env")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Кнопки выбора пола
gender_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="👨 Мужчина"),
            KeyboardButton(text="👩 Женщина")
        ]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

# Состояния регистрации
class Registration(StatesGroup):
    waiting_for_name = State()
    waiting_for_gender = State()

# ==========================================
# START
# ==========================================

@dp.message(CommandStart())
async def start_handler(message: Message, state: FSMContext):
    telegram_id = message.from_user.id

    player = get_player(telegram_id)

    # Новый игрок
    if player is None:
        create_player(telegram_id)

        await message.answer(
            "🏝 Добро пожаловать в «Остров жизни»!\n\n"
            "Давай создадим твоего персонажа.\n\n"
            "Как тебя зовут?"
        )

        await state.set_state(Registration.waiting_for_name)
        return

    # Получаем данные игрока
    name = player[2]
    gender = player[3]

    # Имя ещё не указано
    if not name:
        await message.answer(
            "🏝 Давай продолжим создание персонажа.\n\n"
            "Как тебя зовут?"
        )

        await state.set_state(Registration.waiting_for_name)
        return

    # Имя есть, пола ещё нет
    if not gender:
        await message.answer(
            f"Отлично, {name}! 👋\n\n"
            "Теперь выбери своего персонажа.",
            reply_markup=gender_keyboard
        )

        await state.set_state(Registration.waiting_for_gender)
        return

    # Полностью зарегистрированный игрок
    await message.answer(
        f"🏝 С возвращением, {name}!\n\n"
        "Твой остров ждёт тебя."
    )

# ==========================================
# ВВОД ИМЕНИ
# ==========================================

@dp.message(Registration.waiting_for_name)
async def process_name(message: Message, state: FSMContext):
    name = message.text.strip()

    if len(name) < 2:
        await message.answer(
            "Имя слишком короткое 😅\n\n"
            "Напиши имя ещё раз."
        )
        return

    if len(name) > 20:
        await message.answer(
            "Имя слишком длинное.\n\n"
            "Давай максимум 20 символов."
        )
        return

    telegram_id = message.from_user.id

    update_player_name(telegram_id, name)

    await state.set_state(Registration.waiting_for_gender)

    await message.answer(
        f"Отлично, {name}! 👋\n\n"
        "Теперь выбери своего персонажа.",
        reply_markup=gender_keyboard
    )

# ==========================================
# ВЫБОР ПОЛА
# ==========================================

@dp.message(Registration.waiting_for_gender)
async def process_gender(message: Message, state: FSMContext):
    gender = message.text

    if gender == "👨 Мужчина":
        gender_value = "male"

    elif gender == "👩 Женщина":
        gender_value = "female"

    else:
        await message.answer(
            "Пожалуйста, выбери один из вариантов ниже 👇",
            reply_markup=gender_keyboard
        )
        return

    telegram_id = message.from_user.id

    update_player_gender(telegram_id, gender_value)

    await state.clear()

    await message.answer(
        "🎉 Персонаж создан!\n\n"
        "🏝 Добро пожаловать на твой остров!\n\n"
        "Сейчас начнём твою историю.",
        reply_markup=None
    )

# ==========================================
# ЗАПУСК
#


async def main():
    print("🏝 Игра запускается...")

    init_db()

    print("🗄 База данных подключена.")

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())



