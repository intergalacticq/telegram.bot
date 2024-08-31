
from aiogram import Router, F,types
from aiogram import Bot
import sqlite3 as sl
import re
from aiogram.types import Message, ContentType, BotCommand
from aiogram.types import ReplyKeyboardMarkup,KeyboardButton
import threading
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
router = Router()

db_lock = threading.Lock()
AUTO_NUMBER_REGEX = re.compile(r'^[A-Z]\d{3}[A-Z]{2}\d{2,3}$')
class AddAutoState(StatesGroup):
    waiting_for_auto = State()
    waiting_for_auto_search = State()
def execute_query(query, params=None):
    db_lock.acquire()
    try:
        con = sl.connect('fordfocusyug.db')
        cursor = con.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        results = cursor.fetchall()
        con.commit()
        con.close()
        return results
    finally:
        db_lock.release()
@router.message(F.content_type == ContentType.NEW_CHAT_MEMBERS)
async def welcome_new_member(message: Message):
    for new_member in message.new_chat_members:
        mention = f'<a href="tg://user?id={new_member.id}">{new_member.first_name}</a>'
        await message.answer(f"Привет, {mention}!👋\nДобро пожаловать в группу!🤝\nНе забудь ознакомиться с правилами в закрепе группы!📕\n")
def create_reply_keyboard():
    keyboard = [
        [KeyboardButton(text="Добавить Авто")],
        [KeyboardButton(text="Поиск Авто")],
        [KeyboardButton(text="Бросить кубик")],
        [KeyboardButton(text="Поддержать разработчика")]
    ]

    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)
@router.startup()
async def on_startup():
    execute_query("""CREATE TABLE IF NOT EXISTS auto (
            auto_id STR
        )""")
    print("Database ready")
@router.message(F.text == "reload_buttons")
async def send_reply_keyboard(message: Message):
    await message.delete()
    await message.answer("Кнопки перезагружены!",reply_markup=create_reply_keyboard())
#Первая кнопка на добавление(обработчик)
@router.message(F.text == "Добавить Авто")
async def handle_button_1(message: Message,state: FSMContext):
    await message.answer("Введите номер вашего автомобиля\nИспользуя английские символы, без пробелов.")
    await state.set_state(AddAutoState.waiting_for_auto)
@router.message(AddAutoState.waiting_for_auto)
async def handle_auto_input(message: Message, state: FSMContext):
    auto_data = message.text
    res = execute_query("SELECT auto_id FROM auto WHERE auto_id = ?",(auto_data,))
    if res:
        await message.answer("Данный номер уже есть!")
        await state.clear()
    else:
        if AUTO_NUMBER_REGEX.match(auto_data):
            execute_query("INSERT INTO auto (auto_id) VALUES (?)",(auto_data,))
            await message.answer(f"Вы добавили номер: {auto_data}.")
            await state.clear()
        else:
            await message.answer("Некорректный формат номера.\nПожалуйста, введите номер в формате: А111АА00\nИспользуйте английские символы!")

#Вторая кнопка на поиск(обработчик)    
@router.message(F.text == "Поиск Авто")
async def handle_button_1(message: Message,state: FSMContext):
    await message.answer("Введите номер искомого автомобиля")
    await state.set_state(AddAutoState.waiting_for_auto_search)
@router.message(AddAutoState.waiting_for_auto_search)
async def handle_auto_input(message: Message, state: FSMContext):
    auto_data = str(message.text)
    if AUTO_NUMBER_REGEX.match(auto_data):
        result = execute_query("SELECT auto_id FROM auto WHERE auto_id = ?",(auto_data,))
        if result:
            await message.answer(f"Номер найден и числится в группе!")
            await state.clear()
        else:
            await message.answer(f"Данный номер не зарегистрирован в группе.")
            await state.clear()
    else:
        await message.answer("Некорректный формат номера.\nПожалуйста, введите номер в формате: А111АА00\nИспользуйте английские символы!")
#Третья кнопка для кубика 
@router.message(F.text == "Бросить кубик")
async def handle_button_1(message: Message):
    await message.answer_dice(emoji="🎲")
    return
#Дать мне деняк
@router.message(F.text == "Поддержать разработчика",)
async def sendMessage(message: Message, bot:Bot):
    username = str(message.from_user.id)
    await message.delete()
    await bot.send_message(chat_id = username, text = "Сбербанк - 2202 2061 3050 1609")
    return
