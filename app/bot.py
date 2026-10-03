import asyncio
import os

import aiohttp
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
from dotenv import load_dotenv


load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TIKTOK_API_KEY = os.getenv("TIKTOK_API_KEY")

if not TELEGRAM_BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN is not set")

if not TIKTOK_API_KEY:
    raise ValueError("TIKTOK_API_KEY is not set")


bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher()


async def get_tiktok_followers(username: str) -> int:
    url = "https://api.fetchlayer.dev/tiktok/user-profile"

    headers = {
        "Authorization": f"Bearer {TIKTOK_API_KEY}",
        "Content-Type": "application/json",
    }

    data = {
        "username": username,
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(
            url,
            headers=headers,
            json=data,
        ) as response:

            if response.status != 200:
                raise RuntimeError(
                    f"TikTok API returned {response.status}"
                )

            result = await response.json()

    return result["profile"]["stats"]["followerCount"]


@dp.message(Command("start"))
async def start_handler(message: Message):
    await message.answer(
        "Отправьте /followers <username> чтобы проверить TikTok аккаунт."
    )


@dp.message(Command("followers"))
async def followers_handler(message: Message):
    parts = message.text.split(maxsplit=1)

    if len(parts) < 2:
        await message.answer(
            "Использование:\n/followers username"
        )
        return

    username = parts[1].strip().lstrip("@")

    try:
        followers = await get_tiktok_followers(username)

        await message.answer(
            f"@{username}\n\n"
            f"Подписчики: {followers:,}"
        )

    except Exception:
        await message.answer(
            "TikTok аккаунт не найден."
        )


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())