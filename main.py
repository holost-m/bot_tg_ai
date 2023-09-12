import sqlite3
import openai
from config import AI_API_KEY, TG_TOKEN
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from aiogram import F

class DB_users:
    def __init__(self, path_db='users_tg.db'):
        self.conn = sqlite3.connect('users_tg.db')
        self.cur = self.conn.cursor()

    def execute(self, data):
        if type(data) == str:
            self.cur.execute(data)
            self.conn.commit()

    def select_one(self, data):
        if type(data) == str:
            self.cur.execute(data)
            one_result = self.cur.fetchone()
            return one_result

    def select_all(self, data):
        if type(data) == str:
            self.cur.execute(data)
            results = self.cur.fetchall()
            return results

class DB_service:
    def __init__(self):
        self.db = DB_users()

    def reg_user(self, username, name, surname, reg_data):
        self.db.execute(f"INSERT INTO users (username, name, surname, reg_data) "
                        f"VALUES ('{username}', '{name}', '{surname}', '{reg_data}');")

    def save_user_character(self, user_id, character_id):
        self.db.execute(f"UPDATE users set character_id = {character_id} where user_id = {user_id};")

    def get_first_message(self, character_id):
        res = self.db.select_one(f"SELECT first_message FROM characters WHERE character_id={character_id};")
        return res[0]

    def save_user_message(self, message_text, date, user_id, character_id):
        self.db.execute(f"INSERT INTO user_messages (message_text, date, user_id, character_id) "
                        f"VALUES ('{message_text}', '{date}', {user_id}, {character_id});")

    def save_character_message(self, message_text, date, user_id, character_id):
        self.db.execute(f"INSERT INTO character_messages (message_text, date, user_id, character_id) "
                        f"VALUES ('{message_text}', '{date}', {user_id}, {character_id});")


# db = DB_service()
# db.reg_user('razdv', 'Андрей', 'Раздвигалов', '2023-09-12 00:05')
# db.save_user_character(2, 2)
# print(db.get_first_message(1))
# db.save_character_message('Привет, Человек!', '2023-09-12 02:13:33', 2, 2)


class API_openai:
    def __init__(self, AI_API_KEY):
        self.api_key = AI_API_KEY

    def send_message(self, text='Hey'):
        openai.api_key = self.api_key
        response = openai.Completion.create(
            model='text-davinci-003',
            prompt=text,
            temperature=0.8,
            max_tokens= 1000,
            top_p=1.0,
            frequency_penalty=0.5,
            presence_penalty=0.0
        )
        return response["choices"][0]['text'].strip()


# res = ai_bot.send_message('Проверим как ты работаещь. Какие навки нужны питонисту?')
# print(res)

# Объект бота
ai_bot = API_openai(AI_API_KEY)
bot = Bot(token=TG_TOKEN)
# Диспетчер
dp = Dispatcher()

# Хэндлер на команду /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Hello!")

@dp.message(F.text)
async def echo_with_time(message: types.Message):
    res = ai_bot.send_message(message.text)
    # Отправляем новое сообщение с добавленным текстом
    await message.answer(res)

# Запуск процесса поллинга новых апдейтов
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())