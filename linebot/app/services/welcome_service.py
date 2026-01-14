from linebot.models import TextSendMessage
from linebot.models.events import FollowEvent

from app.services.handlers import (
    send_message,
    show_loading_animation,
)
from app.config.line_config import line_bot_api
from app.config.logger import get_logger

logger = get_logger(__name__)

WELCOME_MESSAGE_1 = """親愛的{user_display_name}，歡迎使用成大醫院「我在腎邊，你問我懂」！我可以回答所有和洗腎相關的問題呦！🫶 你可以透過打字或者錄音的方式和我聊聊，準備好就開始吧！"""


class WelcomeService:
    def __init__(self):
        self.logger = logger
        self.line_bot_api = line_bot_api

    def send_welcome_message(self, event: FollowEvent):
        if event.type != "follow":
            self.logger.info(f"Not a follow event: {event}")
            return
        reply_token = event.reply_token

        if not reply_token:
            self.logger.warning("No reply token found in the event.")
            return

        user_id = event.source.user_id
        user_profile = self.line_bot_api.get_profile(user_id)
        user_display_name = user_profile.display_name
        self.logger.info("Follow event received")
        self.logger.info(f"User id: {user_id}")
        self.logger.info(f"User display name: {user_display_name}")
        show_loading_animation(user_id)
        self.logger.info(f"Sending welcome message to user: {user_id}")
        send_message(
            reply_token,
            [
                TextSendMessage(
                    text=WELCOME_MESSAGE_1.format(user_display_name=user_display_name)
                )
            ],
        )
