import asyncio
from pyrogram import filters
from pyrogram.errors import FloodWait
from pyrogram.types import Message

from BrandrdXMusic import app
from BrandrdXMusic.misc import SUDOERS
from BrandrdXMusic.utils import get_readable_time
from BrandrdXMusic.utils.database import (
    add_banned_user,
    get_banned_count,
    get_banned_users,
    get_served_chats,
    is_banned_user,
    remove_banned_user,
)
from BrandrdXMusic.utils.decorators.language import language
from BrandrdXMusic.utils.extraction import extract_user
from config import BANNED_USERS


@app.on_message(filters.command(["gban", "globalban"]) & filters.user(list(SUDOERS)))  # Fix: Convert SUDOERS to a list
@language
async def global_ban(client, message: Message, _):
    """Globally bans a user from all served chats."""
    if not message.reply_to_message and len(message.command) < 2:
        return await message.reply_text(_["general_1"])

    # Extract user
    user = await extract_user(message)
    if not user:
        return await message.reply_text(_["gban_11"])  # Handle invalid user extraction

    # Prevent banning the bot, self, or sudoers
    if user.id == message.from_user.id:
        return await message.reply_text(_["gban_1"])
    if user.id == app.id:
        return await message.reply_text(_["gban_2"])
    if user.id in SUDOERS:
        return await message.reply_text(_["gban_3"])

    # Check if already banned
    if await is_banned_user(user.id):
        return await message.reply_text(_["gban_4"].format(user.mention))

    # Add user to banned users and notify
    if user.id not in BANNED_USERS:
        BANNED_USERS.add(user.id)
    served_chats = await get_served_chats()
    time_expected = get_readable_time(len(served_chats))
    mystic = await message.reply_text(_["gban_5"].format(user.mention, time_expected))

    # Ban user in all chats
    number_of_chats = 0
    for chat in served_chats:
        try:
            await app.ban_chat_member(chat["chat_id"], user.id)
            number_of_chats += 1
        except FloodWait as fw:
            await asyncio.sleep(fw.value)
        except Exception as e:
            # Log the error for debugging purposes (optional)
            continue

    # Add to database
    await add_banned_user(user.id)
    await message.reply_text(
        _["gban_6"].format(
            app.mention,
            message.chat.title,
            message.chat.id,
            user.mention,
            user.id,
            message.from_user.mention,
            number_of_chats,
        )
    )
    await mystic.delete()


@app.on_message(filters.command(["ungban"]) & filters.user(list(SUDOERS)))  # Fix: Convert SUDOERS to a list
@language
async def global_unban(client, message: Message, _):
    """Globally unbans a user from all served chats."""
    if not message.reply_to_message and len(message.command) < 2:
        return await message.reply_text(_["general_1"])

    # Extract user
    user = await extract_user(message)
    if not user:
        return await message.reply_text(_["gban_11"])  # Handle invalid user extraction

    # Check if user is already not banned
    if not await is_banned_user(user.id):
        return await message.reply_text(_["gban_7"].format(user.mention))

    # Remove user from banned users and notify
    if user.id in BANNED_USERS:
        BANNED_USERS.remove(user.id)
    served_chats = await get_served_chats()
    time_expected = get_readable_time(len(served_chats))
    mystic = await message.reply_text(_["gban_8"].format(user.mention, time_expected))

    # Unban user in all chats
    number_of_chats = 0
    for chat in served_chats:
        try:
            await app.unban_chat_member(chat["chat_id"], user.id)
            number_of_chats += 1
        except FloodWait as fw:
            await asyncio.sleep(fw.value)
        except Exception as e:
            # Log the error for debugging purposes (optional)
            continue

    # Remove from database
    await remove_banned_user(user.id)
    await message.reply_text(_["gban_9"].format(user.mention, number_of_chats))
    await mystic.delete()


@app.on_message(filters.command(["gbannedusers", "gbanlist"]) & filters.user(list(SUDOERS)))  # Fix: Convert SUDOERS to a list
@language
async def gbanned_list(client, message: Message, _):
    """Lists all globally banned users."""
    counts = await get_banned_count()
    if counts == 0:
        return await message.reply_text(_["gban_10"])

    mystic = await message.reply_text(_["gban_11"])
    msg = _["gban_12"]
    count = 0
    users = await get_banned_users()

    for user_id in users:
        count += 1
        try:
            user = await app.get_users(user_id)
            user = user.first_name if not user.mention else user.mention
            msg += f"{count}➤ {user}\n"
        except Exception:
            msg += f"{count}➤ {user_id}\n"
            continue

    if count == 0:
        await mystic.edit_text(_["gban_10"])
    else:
        await mystic.edit_text(msg)
