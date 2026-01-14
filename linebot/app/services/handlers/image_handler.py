from linebot.models import TextSendMessage
from app.services.handlers.common import create_quick_reply
from app.config.logger import get_logger

# 取得模組的日誌記錄器
logger = get_logger(__name__)


def handle_image_message(event):
    """處理音訊訊息"""
    return [TextSendMessage(text="收到圖片", quick_reply=create_quick_reply())]
