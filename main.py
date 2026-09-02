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


# =========================
# КНОПКИ ВЫБОРА ПОЛА
# =========================

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


# =========================
# ГЛАВНОЕ МЕНЮ
# =========================

main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="🌴 Мой остров"),
            KeyboardButton(text="🎁 Открыть сундук")
        ],
        [
            KeyboardButton(text="🏠 Мой дом"),
            KeyboardButton(text="🎒 Рюкзак")
        ],
        [
            KeyboardButton(text="👤 Профиль")
        ]
    ],
    resize_keyboard=True
)


# =========================
# СОСТОЯНИЯ РЕГИСТРАЦИИ
# =========================

class Registration(StatesGroup):
    waiting_for_name = State()
    waiting_for_gender = State()


# =========================
# START
# =========================

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

    # Имя есть, пола нет
    if not gender:

        await message.answer(
            f"Отлично, {name}! 👋\n\n"
            "Теперь выбери своего персонажа.",
            reply_markup=gender_keyboard
        )

        await state.set_state(Registration.waiting_for_gender)

        return

    # Игрок уже зарегистрирован
    await message.answer(
        f"🏝 С возвращением, {name}!\n\n"
        "Твой остров ждёт тебя.",
        reply_markup=main_keyboard
    )


# =========================
# ВВОД ИМЕНИ
# =========================

@dp.message(Registration.waiting_for_name)
async def process_name(message: Message, state: FSMContext):

    if not message.text:
        await message.answer("Пожалуйста, напиши своё имя.")
        return

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


# =========================
# ВЫБОР ПОЛА
# =========================

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
        "Твоя история начинается прямо сейчас.",
        reply_markup=main_keyboard
    )


# =========================
# МОЙ ОСТРОВ
# =========================

@dp.message(lambda message: message.text == "🌴 Мой остров")
async def island_handler(message: Message):

    await message.answer(
        "🌴 ТВОЙ ОСТРОВ\n\n"
        "🏝 Здесь находится твой остров.\n\n"
        "Пока он пустой, но совсем скоро "
        "мы начнём его развивать."
    )


# =========================
# ОТКРЫТЬ СУНДУК
# =========================

@dp.message(lambda message: message.text == "🎁 Открыть сундук")
async def chest_handler(message: Message):

    await message.answer(
        "🎁 СУНДУК\n\n"
        "Сундук пока закрыт.\n\n"
        "Скоро здесь появится первая игровая механика."
    )


# =========================
# МОЙ ДОМ
# =========================

@dp.message(lambda message: message.text == "🏠 Мой дом")
async def house_handler(message: Message):

    await message.answer(
        "🏠 ТВОЙ ДОМ\n\n"
        "Пока у тебя нет дома.\n\n"
        "Мы построим его на твоём острове."
    )


# =========================
# РЮКЗАК
# =========================

@dp.message(lambda message: message.text == "🎒 Рюкзак")
async def inventory_handler(message: Message):

    await message.answer(
        "🎒 РЮКЗАК\n\n"
        "Пока здесь пусто.\n\n"
        "Предметы появятся после первых игровых действий."
    )


# =========================
# ПРОФИЛЬ
# =========================

@dp.message(lambda message: message.text == "👤 Профиль")
async def profile_handler(message: Message):

    telegram_id = message.from_user.id

    player = get_player(telegram_id)

    if player is None:

        await message.answer(
            "❌ Персонаж не найден."
        )

        return

    name = player[2]
    gender = player[3]
    level = player[4]
    xp = player[5]
    coins = player[6]
    day = player[7]

    if gender == "male":
        gender_text = "👨 Мужчина"
    else:
        gender_text = "👩 Женщина"

    await message.answer(
        "👤 ТВОЙ ПРОФИЛЬ\n\n"
        f"Имя: {name}\n"
        f"Пол: {gender_text}\n\n"
        f"⭐ Уровень: {level}\n"
        f"✨ XP: {xp}\n"
        f"💰 Монеты: {coins}\n"
        f"📅 День: {day}"
    )


# =========================
# ЗАПУСК
# =========================

async def main():

    print("🏝 Игра запускается...")

    init_db()

    print("🗄 База данных подключена.")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())