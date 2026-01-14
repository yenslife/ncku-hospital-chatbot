from fastapi import APIRouter, Request, HTTPException
from linebot.exceptions import InvalidSignatureError
from linebot.models import (
    MessageEvent,
    TextMessage,
    ImageMessage,
    AudioMessage,
    FollowEvent,
    PostbackEvent,
)
from app.config.line_config import handler
from app.services.message_service import MessageService
from app.services.welcome_service import WelcomeService
from app.services.postback_service import PostbackService
from app.config.logger import get_logger

logger = get_logger(__name__)


router = APIRouter(prefix="/linebot", tags=["linebot"])

message_service = MessageService()
welcome_service = WelcomeService()
postback_service = PostbackService()


@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    logger.info("收到文字訊息")
    reply_messages = message_service.handle_text_message(event)
    message_service.send_message(event.reply_token, reply_messages)


@handler.add(MessageEvent, message=ImageMessage)
def handle_image_message(event):
    logger.info("收到圖片訊息")
    reply_message = message_service.handle_image_message(event)
    message_service.send_message(event.reply_token, [reply_message])


@handler.add(MessageEvent, message=AudioMessage)
def handle_audio_message(event):
    logger.info("收到音訊訊息")
    reply_message = message_service.handle_audio_message(event)
    message_service.send_message(event.reply_token, [reply_message])


@handler.add(FollowEvent)
def handle_follow_event(event):
    logger.info("收到加入好友事件")
    welcome_service.send_welcome_message(event)


@handler.add(PostbackEvent)
def handle_postback_event(event):
    logger.info("收到 Postback 事件")
    reply_messages = postback_service.handle_postback_event(event)
    if not reply_messages:
        logger.warning("未知的 Postback event，可能是換 rich menu 頁面")
        return
    postback_service.send_message(event.reply_token, reply_messages)


@router.post("/webhook")
async def line_webhook(request: Request):
    # 獲取 X-Line-Signature header 值
    signature = request.headers["X-Line-Signature"]

    # 獲取請求體內容
    body = await request.body()

    try:
        # 驗證簽名並處理請求
        handler.handle(body.decode(), signature)
    except InvalidSignatureError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    return "OK"
