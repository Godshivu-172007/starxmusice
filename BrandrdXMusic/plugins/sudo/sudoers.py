from pyrogram import filters
from pyrogram.types import Message
from BrandrdXMusic import app
from BrandrdXMusic.misc import SUDOERS
from BrandrdXMusic.utils.database import add_sudo, remove_sudo
from BrandrdXMusic.utils.decorators.language import language
from BrandrdXMusic.utils.extraction import extract_user
from BrandrdXMusic.utils.inline import close_markup
from config import BANNED_USERS, OWNER_ID


# Add Sudo User
@app.on_message(filters.command(["addsudo"]) & filters.user(OWNER_ID))
@language
async def useradd(client, message: Message, _):
    try:
        # Check if command is correct
        if not message.reply_to_message and len(message.command) != 2:
            return await message.reply_text(_["general_1"])  # Missing argument

        # Extract the user
        user = await extract_user(message)
        if not user:
            return await message.reply_text("❌ User not found. Please provide a valid user ID or reply to a user.")

        # Check if the user is already a sudo user
        if user.id in SUDOERS:
            return await message.reply_text(_["sudo_1"].format(user.mention))

        # Add the user to SUDOERS
        added = await add_sudo(user.id)
        if added:
            SUDOERS.add(user.id)
            return await message.reply_text(_["sudo_2"].format(user.mention))
        else:
            return await message.reply_text("❌ Failed to add user as sudo. Please try again.")
    except Exception as e:
        # Log and respond to errors
        print(f"Error in /addsudo command: {e}")
        return await message.reply_text("❌ An unexpected error occurred. Check logs for details.")


# Remove Sudo User
@app.on_message(filters.command(["delsudo", "rmsudo"]) & filters.user(OWNER_ID))
@language
async def userdel(client, message: Message, _):
    try:
        # Check if command is correct
        if not message.reply_to_message and len(message.command) != 2:
            return await message.reply_text(_["general_1"])  # Missing argument

        # Extract the user
        user = await extract_user(message)
        if not user:
            return await message.reply_text("❌ User not found. Please provide a valid user ID or reply to a user.")

        # Check if the user is in SUDOERS
        if user.id not in SUDOERS:
            return await message.reply_text(_["sudo_3"].format(user.mention))

        # Remove the user from SUDOERS
        removed = await remove_sudo(user.id)
        if removed:
            SUDOERS.remove(user.id)
            return await message.reply_text(_["sudo_4"].format(user.mention))
        else:
            return await message.reply_text("❌ Failed to remove user as sudo. Please try again.")
    except Exception as e:
        # Log and respond to errors
        print(f"Error in /delsudo command: {e}")
        return await message.reply_text("❌ An unexpected error occurred. Check logs for details.")


# List Sudo Users
@app.on_message(filters.command(["sudolist", "listsudo", "sudoers"]) & ~BANNED_USERS)
@language
async def sudoers_list(client, message: Message, _):
    try:
        # Display the owner if the user is not in the SUDOERS list
        if message.from_user.id not in SUDOERS:
            return await message.reply_text(
                "💔 <b>ᴏᴡɴᴇʀs:</b>\n1➤ <a href='https://t.me/+zofL0InuuzlhNjhl'>🇷🇺⛦Sungjinwu172007°</a>",
                disable_web_page_preview=True,
                parse_mode="html",  # Ensure "html" is lowercase
            )

        # Initialize the text for sudoers list
        text = _["sudo_5"]
        user = await app.get_users(OWNER_ID)
        user = user.first_name if not user.mention else user.mention
        text += f"1➤ {user}\n"
        count = 0
        smex = 0

        # Loop through SUDOERS and add to the text
        for user_id in SUDOERS:
            if user_id != OWNER_ID:
                try:
                    user = await app.get_users(user_id)
                    user = user.first_name if not user.mention else user.mention
                    if smex == 0:
                        smex += 1
                        text += _["sudo_6"]
                    count += 1
                    text += f"{count}➤ {user}\n"
                except Exception as e:
                    print(f"Error fetching user {user_id}: {e}")
                    continue

        # Handle the case where no sudoers are found
        if not text:
            return await message.reply_text(_["sudo_7"])
        else:
            return await message.reply_text(text, reply_markup=close_markup(_), parse_mode="html")
    except Exception as e:
        # Log and respond to errors
        print(f"Error in /sudolist command: {e}")
        return await message.reply_text("❌ An unexpected error occurred. Check logs for details.")
