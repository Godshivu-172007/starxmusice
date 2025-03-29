import asyncio
from pyrogram import filters
from pyrogram.enums import ChatMembersFilter
from pyrogram.errors import FloodWait

from BrandrdXMusic import app
from BrandrdXMusic.misc import SUDOERS
from BrandrdXMusic.utils.database import (
    get_active_chats,
    get_authuser_names,
    get_client,
    get_served_chats,
    get_served_users,
)
from BrandrdXMusic.utils.decorators.language import language
from BrandrdXMusic.utils.formatters import alpha_to_int
from config import adminlist

IS_BROADCASTING = False


@app.on_message(filters.command("broadcast") & filters.user(list(SUDOERS)))  # Ensure SUDOERS is a list
@language
async def broadcast_message(client, message, _):
    """Handles the broadcast of messages to chats and users."""
    global IS_BROADCASTING
    if IS_BROADCASTING:
        return await message.reply_text(_["broad_0"])  # Notify if another broadcast is in progress

    # Determine if the broadcast is a reply or text command
    if message.reply_to_message:
        msg_id = message.reply_to_message.id
        chat_id = message.chat.id
    else:
        if len(message.command) < 2:
            return await message.reply_text(_["broad_2"])  # Error if no text provided
        query = message.text.split(None, 1)[1]
        query = process_flags(query)  # Handle broadcast flags
        if not query:
            return await message.reply_text(_["broad_8"])  # Error if query is empty

    IS_BROADCASTING = True
    await message.reply_text(_["broad_1"])  # Notify that the broadcast has started

    # Broadcast to served chats
    if "-nobot" not in message.text:
        await broadcast_to_chats(message, query, msg_id, chat_id, _)

    # Broadcast to served users
    if "-user" in message.text:
        await broadcast_to_users(message, query, msg_id, chat_id, _)

    # Broadcast using assistants
    if "-assistant" in message.text:
        await broadcast_with_assistants(message, query, msg_id, chat_id, _)

    IS_BROADCASTING = False


async def broadcast_to_chats(message, query, msg_id, chat_id, _):
    """Broadcast to all served chats."""
    sent = 0
    pinned = 0
    served_chats = await get_served_chats()
    chat_ids = [int(chat["chat_id"]) for chat in served_chats]

    for chat_id in chat_ids:
        try:
            if message.reply_to_message:
                msg = await app.forward_messages(chat_id, chat_id, msg_id)
            else:
                msg = await app.send_message(chat_id, text=query)

            # Handle pinning
            if "-pin" in message.text:
                try:
                    await msg.pin(disable_notification=True)
                    pinned += 1
                except Exception:
                    pass
            elif "-pinloud" in message.text:
                try:
                    await msg.pin(disable_notification=False)
                    pinned += 1
                except Exception:
                    pass

            sent += 1
            await asyncio.sleep(0.2)

        except FloodWait as fw:
            await asyncio.sleep(fw.value)
        except Exception:
            continue

    await message.reply_text(_["broad_3"].format(sent, pinned))


async def broadcast_to_users(message, query, msg_id, chat_id, _):
    """Broadcast to all served users."""
    sent_users = 0
    served_users = await get_served_users()
    user_ids = [int(user["user_id"]) for user in served_users]

    for user_id in user_ids:
        try:
            if message.reply_to_message:
                await app.forward_messages(user_id, chat_id, msg_id)
            else:
                await app.send_message(user_id, text=query)

            sent_users += 1
            await asyncio.sleep(0.2)

        except FloodWait as fw:
            await asyncio.sleep(fw.value)
        except Exception:
            continue

    await message.reply_text(_["broad_4"].format(sent_users))


async def broadcast_with_assistants(message, query, msg_id, chat_id, _):
    """Broadcast using assistant accounts."""
    from BrandrdXMusic.core.userbot import assistants  # Import assistants dynamically

    assistant_reply = await message.reply_text(_["broad_5"])
    result_text = _["broad_6"]

    for assistant in assistants:
        sent_count = 0
        client = await get_client(assistant)

        async for dialog in client.get_dialogs():
            try:
                if message.reply_to_message:
                    await client.forward_messages(dialog.chat.id, chat_id, msg_id)
                else:
                    await client.send_message(dialog.chat.id, text=query)

                sent_count += 1
                await asyncio.sleep(3)

            except FloodWait as fw:
                await asyncio.sleep(fw.value)
            except Exception:
                continue

        result_text += _["broad_7"].format(assistant, sent_count)

    await assistant_reply.edit_text(result_text)


def process_flags(query):
    """Process and clean broadcast flags from the query text."""
    flags = ["-pin", "-nobot", "-pinloud", "-assistant", "-user"]
    for flag in flags:
        query = query.replace(flag, "")
    return query.strip()


async def auto_clean():
    """Automatically refresh admin list periodically."""
    while not await asyncio.sleep(10):
        try:
            served_chats = await get_active_chats()
            for chat_id in served_chats:
                if chat_id not in adminlist:
                    adminlist[chat_id] = []

                    # Fetch chat administrators
                    async for user in app.get_chat_members(
                        chat_id, filter=ChatMembersFilter.ADMINISTRATORS
                    ):
                        if user.privileges.can_manage_video_chats:
                            adminlist[chat_id].append(user.user.id)

                    # Fetch authorized users
                    auth_users = await get_authuser_names(chat_id)
                    for user in auth_users:
                        user_id = await alpha_to_int(user)
                        adminlist[chat_id].append(user_id)
        except Exception:
            continue


# Start the auto_clean task
asyncio.create_task(auto_clean())
