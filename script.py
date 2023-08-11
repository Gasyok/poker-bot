import asyncio
import random
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.types import ParseMode

TELEGRAM_ACCESS_TOKEN = '6573861788:AAGZsFzVujd8Xl5HjGbiaO4CSMFGlXLythE'
TELEGRAM_CHAT_ID = '-878850232'

game_running = False

STRATEGIES = {
    "basics": """
Основы покера:
- Покер — это карточная игра, где игроки соревнуются за банк, который формируется их ставками.
- Цель игры — выиграть фишки, поставив наилучшую комбинацию карт или заставив других игроков сбросить карты.
- Существует множество вариаций покера, но в большинстве из них используется стандартная колода из 52 карт.
    """,

    "starting_hands": """
Начальные руки в Texas Hold'em:
- Лучшие стартовые руки — это пары валетов, дам, королей и тузов. Эти руки имеют высокий потенциал для формирования сильных комбинаций.
- Средние стартовые руки включают в себя пары от десяток до восьмерок, а также две карты одной масти от десятки до туза.
- Слабые стартовые руки — это низкие несогласованные карты. С такими руками лучше играть осторожно.
    """,

    "position": """
Позиция за покерным столом:
- Ранняя позиция: первые 2-3 игрока после дилера. В этой позиции лучше играть только сильные руки, так как многие игроки будут действовать после вас.
- Средняя позиция: следующие 2-3 игрока. Здесь можно немного расширить диапазон рук для игры.
- Поздняя позиция: последние 2-3 игрока перед дилером. В этой позиции можно играть более агрессивно, так как вы видите действия большинства игроков.
    """,

    "bluffing": """
Блеф в покере:
- Блеф — это когда игрок делает ставку с плохой рукой в надежде заставить соперников сбросить свои карты.
- Эффективный блеф требует хорошего понимания динамики стола и психологии соперников.
- Не стоит часто блефовать против большого числа игроков или против очень консервативных игроков.
    """
}


LEVELS = [
    {"blinds": "5/10", "duration": 30},
    {"blinds": "10/20", "duration": 35},
    {"blinds": "25/50", "duration": 45},
    {"blinds": "BREAK", "duration": 30},
    {"blinds": "50/100", "duration": 40},
    {"blinds": "100/200", "duration": None}
]

bot = Bot(token=TELEGRAM_ACCESS_TOKEN)
dp = Dispatcher(bot)
timer_paused = False
pause_event = asyncio.Event()

current_level_index = 0

voted_users = {}


@dp.message_handler(commands=['move'])
async def move_level(message: types.Message):
    global current_level_index
    try:
        num = int(message.text.split()[1]) - 1
        if 0 <= num < len(LEVELS):
            current_level_index = num
            await message.reply(f"Уровень изменен на: {LEVELS[num]['blinds']}.")
        else:
            await message.reply("Неверный номер уровня.")
    except (ValueError, IndexError):
        await message.reply("Пожалуйста, предоставьте корректный номер уровня.")


async def poker_timer(chat_id):
    global current_level_index
    global game_running
    for idx in range(current_level_index, len(LEVELS)):
        if not game_running:
            break
        level = LEVELS[idx]
        blinds = level["blinds"]
        duration = level["duration"]

        if blinds == "BREAK":
            await bot.send_message(chat_id, "Перерыв! 30 минут отдыха.")
        else:
            await bot.send_message(chat_id, f"Текущие ставки: {blinds}. Длительность: {duration if duration else 'до конца'} минут.")

        if duration:
            for _ in range(duration * 60):
                if timer_paused:
                    await pause_event.wait()
                await asyncio.sleep(1)
        current_level_index += 1

    await bot.send_message(chat_id, "Турнир завершен!")


@dp.message_handler(commands=['current_level'])
async def show_current_level(message: types.Message):
    global current_level_index
    level = LEVELS[current_level_index]
    blinds = level["blinds"]
    duration = level["duration"]
    await message.reply(f"Текущие ставки: {blinds}. Длительность: {duration if duration else 'до конца'} минут.")


@dp.message_handler(commands=['levels'])
async def show_levels(message: types.Message):
    levels_text = ""
    for i, level in enumerate(LEVELS):
        blinds = level["blinds"]
        duration = level["duration"]
        levels_text += f"{i + 1}. Ставки: {blinds}. Длительность: {duration if duration else 'до конца'} минут.\n"
    await message.reply(levels_text)


@dp.message_handler(commands=['vote'])
async def vote(message: types.Message):
    names = message.text.split()[1:]
    if len(names) != 2:
        await message.reply("Пожалуйста, предоставьте две фамилии для голосования.")
        return

    winner = random.choice(names)
    await message.reply(f"Победитель: {winner}!")


@dp.message_handler(commands=['pause'])
async def pause_timer(message: types.Message):
    global timer_paused
    timer_paused = True
    await bot.send_message(message.chat.id, "Таймер на паузе!")


@dp.message_handler(commands=['go'])
async def resume_timer(message: types.Message):
    global timer_paused
    timer_paused = False
    pause_event.set()
    pause_event.clear()
    await bot.send_message(message.chat.id, "Таймер возобновлен!")


@dp.message_handler(commands=['start_game'])
async def start_game(message: types.Message):
    global game_running
    game_running = True
    await bot.send_message(message.chat.id, "Начинаем турнир!")
    asyncio.create_task(poker_timer(message.chat.id))


@ dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.reply("Всё епта, я нахуй работаю!")


@ dp.message_handler(commands=['help'])
async def send_help(message: types.Message):
    await message.reply("Это справочная информация.")


@ dp.message_handler(commands=['free_porn'])
async def send_info(message: types.Message):
    await message.reply("Ебать самая лучшая порнуха -->>>  www.pornhub.com")

votes = {}


@dp.message_handler(commands=['anonym_vote'])
async def anonym_vote(message: types.Message):
    names = message.text.split()[1:]
    if len(names) != 2:
        await message.reply("Пожалуйста, предоставьте две фамилии для голосования.")
        return

    votes[names[0]] = 0
    votes[names[1]] = 0

    markup = types.InlineKeyboardMarkup()
    for name in names:
        button = types.InlineKeyboardButton(name, callback_data=name)
        markup.add(button)

    await bot.send_message(message.chat.id, "Выберите победителя:", reply_markup=markup)


@dp.callback_query_handler(lambda c: c.data in votes)
async def process_callback(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    name = callback_query.data

    if user_id in voted_users:
        await bot.answer_callback_query(callback_query.id, "Вы уже проголосовали!")
        return

    votes[name] += 1
    voted_users[user_id] = True
    await bot.answer_callback_query(callback_query.id, f"Вы проголосовали за {name}!")


@dp.message_handler(commands=['results'])
async def show_results(message: types.Message):
    results = "\n".join([f"{name}: {votes[name]}" for name in votes])
    await message.reply(f"Результаты голосования:\n{results}")


@dp.message_handler(commands=['stop_game'])
async def stop_game(message: types.Message):
    global game_running
    game_running = False
    await message.reply("Игра остановлена!")


@dp.message_handler(commands=['strategy'])
async def strategy(message: types.Message):
    global STRATEGIES
    topic = message.text.split()[1] if len(message.text.split()) > 1 else None

    if not topic:
        available_topics = ", ".join(STRATEGIES.keys())
        await message.reply(f"Доступные темы: {available_topics}. \n\nДля получения информации по теме используйте `/strategy [тема]`.")
        return

    if topic in STRATEGIES:
        await message.reply(STRATEGIES[topic])
    else:
        await message.reply("Такой темы нет. Пожалуйста, выберите другую тему.")


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
