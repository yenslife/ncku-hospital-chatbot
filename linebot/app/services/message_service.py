"""訊息服務模組 - 處理 LINE Bot 的各種訊息類型"""

from app.services.handlers import (
    handle_text_message,
    handle_image_message,
    handle_audio_message,
    send_message,
)
from app.config.logger import get_logger

logger = get_logger(__name__)


class MessageService:
    """處理 LINE Bot 的訊息服務"""

    async def handle_text_message(self, event):
        """處理文字訊息"""
        await handle_text_message(event)

    async def handle_image_message(self, event):
        """處理圖片訊息"""
        await handle_image_message(event)

    async def handle_audio_message(self, event):
        """處理音訊訊息"""
        await handle_audio_message(event)

    async def send_message(self, reply_token, messages):
        """發送訊息到 LINE"""
        await send_message(reply_token, messages)
