import telegram
import asyncio

# Bot find - t.me/AmenityAutoBot
BOT_TOKEN = "7205271683:AAGgMHvoiCdd1HklOoE2cm0ruwJU22Oti1o"

async def send_message(chat_id, message: str):
    """Sends a text message to the specified chat."""
    try:
        bot = telegram.Bot(token=BOT_TOKEN)
        await bot.send_message(chat_id=chat_id, text=message)
        print(f"Message sent to chat ID: {chat_id}")
    except Exception as e:
        print(f"An error occurred: {e}")


chat_ids = [-4164151676]


def send_telegram_message(my_message):
    asyncio.run(send_message(chat_id=chat_ids[0], message=my_message))

# for ids in chat_ids:
#     asyncio.run(send_message(ids, "Hello"))