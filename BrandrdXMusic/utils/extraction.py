from pyrogram.enums import MessageEntityType
from pyrogram.types import Message, User
from pyrogram.errors import PeerIdInvalid

from BrandrdXMusic import app


async def extract_user(m: Message) -> User:
    """
    Extracts a user from a message.
    If the command is directed at a specific user or the message is a reply, 
    this function retrieves the target user.

    Args:
        m (Message): The incoming message.

    Returns:
        User: The extracted user object.
    """
    try:
        # Case 1: The message is a reply
        if m.reply_to_message:
            return m.reply_to_message.from_user

        # Case 2: Extract user based on command arguments or mentions
        msg_entities = m.entities[1] if m.text.startswith("/") else m.entities[0]
        if msg_entities.type == MessageEntityType.TEXT_MENTION:
            # If the user is directly mentioned
            return msg_entities.user
        else:
            # Parse the user ID or username from the command
            user_id_or_username = m.command[1]
            if user_id_or_username.isdecimal():
                # If the argument is a numeric ID
                user_id_or_username = int(user_id_or_username)
            # Fetch the user using the app
            return await app.get_users(user_id_or_username)
    except IndexError:
        # Handle missing arguments in the command
        raise ValueError("No user specified. Reply to a message or provide a valid username/ID.")
    except PeerIdInvalid:
        # Handle invalid user IDs or usernames
        raise ValueError("Invalid user ID or username provided.")
    except Exception as e:
        # Catch-all for any other errors
        raise ValueError(f"An unexpected error occurred: {e}")
