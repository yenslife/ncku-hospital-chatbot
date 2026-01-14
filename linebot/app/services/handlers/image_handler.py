from linebot.v3.messaging import TextMessage
from app.services.handlers.common import create_quick_reply, send_message
from app.config.logger import get_logger

logger = get_logger(__name__)


async def handle_image_message(event):
    """處理圖片訊息"""
    await send_message(event.reply_token, [TextMessage(text="收到圖片", quick_reply=create_quick_reply())])
