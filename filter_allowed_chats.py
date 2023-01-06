from telegram import Message
from telegram.ext.filters import MessageFilter
from logger import logger


class FilterAllowedChats(MessageFilter):

    def __init__(self, allowed_chat_ids):
        super().__init__()
        self.allowed_chat_ids = allowed_chat_ids

    def filter(self, message: Message) -> bool:
        is_voice = bool(message.voice) or bool(message.audio) or bool(message.video) or bool(message.document)
        chat_id = str(message.chat.id)
        if not is_voice:
            logger.info(f"chat_id={chat_id}: ignoring a message because it is not a voice or audio or video or "
                        f"document message")
            return False
        is_allowed_user = chat_id in self.allowed_chat_ids
        is_allowed = is_voice and is_allowed_user
        if not is_allowed:
            logger.error(f"chat_id={chat_id} is not allowed")
        return is_allowed
