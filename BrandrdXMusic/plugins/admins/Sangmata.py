import asyncio
import random

from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.raw.functions.messages import DeleteHistory

from BrandrdXMusic import userbot as us, app
from BrandrdXMusic.core.userbot import assistants

@app.on_message(filters.command("sg"))
async def sg(client: Client, message: Message):
    # Check if there is no argument and no reply to a message
    if len(message.text.split()) < 2 and not message.reply_to_message:
        return await message.reply("Usage: /sg <username/id> or reply to a message")

    # Extract user ID or username from reply or command argument
    if message.reply_to_message:
        args = message.reply_to_message.from_user.id
    else:
        args = message.text.split()[1]

    lol = await message.reply("<code>Processing...</code>")
    
    try:
        # Try fetching user information
        user = await client.get_users(args)
    except Exception:
        return await lol.edit("<code>Please specify a valid user!</code>")
    
    # Randomly choose a bot
    bo = ["sangmata_bot", "sangmata_beta_bot"]
    sg_bot = random.choice(bo)
    
    # Check if an assistant is available
    if 1 in assistants:
        ubot = us.one
    
    try:
        # Send a message to the selected bot
        a = await ubot.send_message(sg_bot, f"{user.id}")
        await a.delete()
    except Exception as e:
        return await lol.edit(f"<code>Error:</code> {e}")

    await asyncio.sleep(1)
    
    try:
        # Retrieve messages from the bot
        async for stalk in ubot.search_messages(a.chat.id):
            if not stalk or stalk.text is None:
                continue
            await message.reply(stalk.text)
            break
        else:
            await message.reply("The bot did not return any response.")
    except Exception as e:
        return await lol.edit(f"<code>Error fetching bot response:</code> {e}")
    
    try:
        # Delete chat history with the bot
        user_info = await ubot.resolve_peer(sg_bot)
        await ubot.send(DeleteHistory(peer=user_info, max_id=0, revoke=True))
    except Exception:
        pass

    await lol.delete()
