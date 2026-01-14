"""訊息服務模組 - 處理 LINE Bot 的各種訊息類型"""

from app.services.handlers import (
    handle_postback_event,
    send_message,
)
from app.config.logger import get_logger

logger = get_logger(__name__)


class PostbackService:
    """處理 LINE Bot 的按鈕事件"""

    async def handle_postback_event(self, event):
        """處理按鈕事件"""
        await handle_postback_event(event)

    async def send_message(self, reply_token, messages):
        """發送訊息到 LINE"""
        logger.info(f"發送訊息到 LINE: {messages}")
        await send_message(reply_token, messages)
